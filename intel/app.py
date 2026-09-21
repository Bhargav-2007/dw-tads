"""Authenticated queries and exports for public technical intelligence."""
import csv
import html
import io
import secrets
from datetime import date,timedelta,datetime,timezone
from contextlib import asynccontextmanager
from typing import Literal
from fastapi import FastAPI,Depends,HTTPException,Query
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from fastapi.responses import HTMLResponse,Response
from psycopg.rows import dict_row
from .common import *

bearer=HTTPBearer(auto_error=False)

def source_licenses():
    return {'cisa-kev': Path('/app/licenses/CISA-KEV.txt').read_text(),
            'mitre-attack': Path('/app/licenses/MITRE-ATTACK.txt').read_text()}


def authorize(credentials: HTTPAuthorizationCredentials | None=Depends(bearer)):
    if credentials:
        for role,key in [('admin','INTEL_ADMIN_TOKEN'),('reader','INTEL_READER_TOKEN')]:
            if secrets.compare_digest(credentials.credentials,os.environ[key]):
                return role
    raise HTTPException(401,'Valid bearer token required',headers={'WWW-Authenticate':'Bearer'})

@asynccontextmanager
async def lifespan(app):
    for key in ['INTEL_ADMIN_TOKEN','INTEL_READER_TOKEN']:
        if len(os.environ.get(key,''))<32:
            raise RuntimeError(key+' must be generated before startup')
    retry(initialize)
    yield

app=FastAPI(title='DW-TADS Public Technical Intelligence',version='2.0.0',lifespan=lifespan)

class Filters:
    def __init__(self,q: str=Query('',max_length=200),source: Literal['cisa-kev','mitre-attack'] | None=None,
                 kind: Literal['vulnerability','malware','technique'] | None=None,start: date | None=None,end: date | None=None,
                 limit: int=Query(50,ge=1,le=1000),offset: int=Query(0,ge=0),as_of: datetime | None=None):
        if start and end and start>end:
            raise HTTPException(422,'start must not be after end')
        if as_of and as_of.tzinfo is None:
            raise HTTPException(422,'as_of must include a timezone')
        self.as_of=as_of.astimezone(timezone.utc) if as_of else None
        self.q,self.source,self.kind,self.start,self.end,self.limit,self.offset=q,source,kind,start,end,limit,offset


def search(filters):
    terms=['active=TRUE']
    values=[]
    table='intel_records'
    if filters.as_of:
        table='intel_history_records'
        terms.append('snapshot_sha IN (SELECT DISTINCT ON (source) sha256 FROM intel_snapshots WHERE captured_at<=%s AND processed_at IS NOT NULL ORDER BY source,captured_at DESC,sha256)')
        values.append(filters.as_of)
    for field,value in [('source',filters.source),('kind',filters.kind)]:
        if value:
            terms.append(field+'=%s'); values.append(value)
    if filters.q:
        terms.append('(title ILIKE %s OR external_id ILIKE %s OR description ILIKE %s)')
        values.extend(['%'+filters.q+'%']*3)
    if filters.start:
        terms.append('published_at >= %s'); values.append(filters.start)
    if filters.end:
        terms.append('published_at < %s'); values.append(filters.end+timedelta(days=1))
    clause=' AND '.join(terms)
    with db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('SELECT count(*) AS total FROM '+table+' WHERE '+clause,values)
            total=cur.fetchone()['total']
            cur.execute('SELECT * FROM '+table+' WHERE '+clause+' ORDER BY published_at DESC,id LIMIT %s OFFSET %s',values+[filters.limit,filters.offset])
            rows=cur.fetchall()
        cid=str(uuid.uuid4())
        audit(conn,'intel_query',digest(canonical({'q':filters.q,'source':filters.source,'kind':filters.kind,'start':str(filters.start),'end':str(filters.end),'limit':filters.limit,'offset':filters.offset,'as_of':str(filters.as_of)})),cid)
    return {'results':rows,'total':total,'limit':filters.limit,'offset':filters.offset,'query_id':cid,'as_of':filters.as_of,'source_licenses':source_licenses()}

@app.get('/health')
def health():
    return {'alive':True}

@app.get('/ready')
def ready():
    try:
        return health_dependencies()
    except Exception as exc:
        raise HTTPException(503,'A backend dependency is unavailable') from exc

@app.get('/status',dependencies=[Depends(authorize)])
def status():
    with db() as conn,conn.cursor(row_factory=dict_row) as cur:
        cur.execute('SELECT name,url,last_attempt,last_success,error,last_sha FROM intel_sources ORDER BY name')
        sources=cur.fetchall()
        cur.execute('SELECT kind,count(*) AS count FROM intel_records WHERE active GROUP BY kind ORDER BY kind')
        counts=cur.fetchall()
        cur.execute('SELECT count(*) AS count FROM intel_snapshots WHERE processed_at IS NULL')
        pending=cur.fetchone()['count']
        cur.execute('SELECT count(*) AS count FROM intel_relationships')
        relationships=cur.fetchone()['count']
        cur.execute('SELECT count(*) AS count FROM intel_record_versions')
        versions=cur.fetchone()['count']
        cur.execute('SELECT count(*) AS count FROM intel_merkle_anchors')
        anchors=cur.fetchone()['count']
        cur.execute('SELECT version,sha256,applied_at FROM intel_schema_migrations ORDER BY version')
        migrations=cur.fetchall()
    return {'mode':'public-technical-intelligence','sources':sources,'records':counts,'pending_snapshots':pending,
            'relationships':relationships,'record_versions':versions,'merkle_anchors':anchors,'schema_migrations':migrations,
            'object_versioning':objects().get_bucket_versioning(BUCKET).status,'audit_chain_valid':verify_audit(),'refresh_interval_seconds':int(os.getenv('FEED_INTERVAL_SECONDS','21600'))}

@app.get('/records',dependencies=[Depends(authorize)])
@app.get('/query/timeline',dependencies=[Depends(authorize)])
def records(filters: Filters=Depends()):
    return search(filters)

@app.get('/records/{record_id:path}',dependencies=[Depends(authorize)])
def record(record_id: str):
    with db() as conn,conn.cursor(row_factory=dict_row) as cur:
        cur.execute('SELECT * FROM intel_records WHERE id=%s',(record_id,))
        row=cur.fetchone()
        if row is None:
            raise HTTPException(404,'Record not found')
        audit(conn,'intel_record_read',record_id,str(uuid.uuid4()))
        return {**row,'source_licenses':source_licenses()}

@app.get('/evidence/{sha}',dependencies=[Depends(authorize)])
def evidence(sha: str):
    with db() as conn,conn.cursor(row_factory=dict_row) as cur:
        cur.execute('SELECT * FROM intel_snapshots WHERE sha256=%s',(sha,))
        row=cur.fetchone()
        if row is None:
            raise HTTPException(404,'Snapshot not found')
    response=objects().get_object(BUCKET,row['object_key'],version_id=row.get('object_version'))
    try:
        actual=digest(response.read())
    finally:
        response.close(); response.release_conn()
    with db() as conn,conn.cursor(row_factory=dict_row) as cur:
        cur.execute('SELECT root,leaf_count,scheme,recorded_at FROM intel_merkle_anchors WHERE snapshot_sha=%s',(sha,))
        anchor=cur.fetchone()
    return {**row,'merkle_anchor':anchor,'integrity_verified':secrets.compare_digest(sha,actual),'source_url':FEEDS[row['source']]}

@app.get('/graph',dependencies=[Depends(authorize)])
def graph_query(filters: Filters=Depends()):
    result=search(filters)
    ids=[r['id'] for r in result['results']]
    if filters.as_of:
        nodes=[{k:r[k] for k in ('id','kind','title','source_url')} for r in result['results']]
        shas=list({r['snapshot_sha'] for r in result['results']})
        with db() as conn,conn.cursor(row_factory=dict_row) as cur:
            cur.execute('SELECT source_id AS source,target_id AS target,upper(type) AS type,snapshot_sha FROM intel_relationship_versions WHERE snapshot_sha=ANY(%s) AND source_id=ANY(%s) AND target_id=ANY(%s)',(shas,ids,ids))
            edges=cur.fetchall()
    else:
        with graph() as driver,driver.session() as session:
            nodes=[dict(r) for r in session.run('MATCH (n:IntelRecord) WHERE n.id IN $ids AND n.active RETURN n.id AS id,n.kind AS kind,n.title AS title,n.source_url AS source_url',ids=ids)]
            edges=[dict(r) for r in session.run('MATCH (a:IntelRecord)-[r:USES]->(b:IntelRecord) WHERE a.id IN $ids AND b.id IN $ids AND a.active AND b.active RETURN a.id AS source,b.id AS target,type(r) AS type,r.snapshot_sha AS snapshot_sha',ids=ids)]
    return {'nodes':nodes,'edges':edges,'total_matching':result['total'],'truncated':result['total']>len(ids),'source_licenses':source_licenses()}


def csv_cell(value):
    value=str(value or '')
    return "'"+value if value.lstrip().startswith(('=','+','-','@')) or value.startswith(('\t','\r','\n')) else value

@app.get('/export',dependencies=[Depends(authorize)])
def export(format: Literal['csv','json','html']='json',filters: Filters=Depends()):
    result=search(filters)
    with db() as conn:
        audit(conn,'intel_export',format+':'+result['query_id'],result['query_id'])
    attribution='Sources: CISA KEV (CC0) and MITRE ATT&CK. © 2026 The MITRE Corporation. This work is reproduced and distributed with the permission of The MITRE Corporation.'
    license_text=Path('/app/licenses/MITRE-ATTACK.txt').read_text()
    headers={'Content-Disposition':'attachment; filename="threat-intelligence.'+format+'"','X-Total-Count':str(result['total']),'X-Exported-Count':str(len(result['results']))}
    if format=='json':
        return Response(json.dumps({**result,'attribution':attribution,'mitre_license':license_text},default=str,ensure_ascii=False),media_type='application/json',headers=headers)
    fields=['external_id','kind','title','published_at','source','source_url','snapshot_sha']
    if format=='csv':
        output=io.StringIO(newline='')
        writer=csv.writer(output)
        writer.writerow(fields+['attribution','mitre_license'])
        for row in result['results']:
            writer.writerow([csv_cell(row[f]) for f in fields]+[attribution,license_text])
        return Response(output.getvalue(),media_type='text/csv; charset=utf-8',headers=headers)
    body=''.join('<tr>'+''.join('<td>'+html.escape(str(r[f]))+'</td>' for f in fields)+'</tr>' for r in result['results'])
    report='<!doctype html><meta charset="utf-8"><title>Public threat intelligence report</title><h1>Public threat intelligence</h1><p>'+html.escape(attribution)+'</p><p>Exported '+str(len(result['results']))+' of '+str(result['total'])+' matching records.</p><table border="1"><tr>'+''.join('<th>'+f+'</th>' for f in fields)+'</tr>'+body+'</table><pre>'+html.escape(license_text)+'</pre>'
    return HTMLResponse(report,headers=headers)

@app.get('/',response_class=HTMLResponse)
def home():
    return Path('/app/intel/index.html').read_text()

@app.get('/licenses/mitre')
def mitre_license():
    return Response(Path('/app/licenses/MITRE-ATTACK.txt').read_text(),media_type='text/plain')


@app.get('/evidence/{sha}/merkle/{record_id:path}',dependencies=[Depends(authorize)])
def merkle_proof(sha: str,record_id: str):
    from .integrity import proof,verify_proof
    with db() as conn:
        anchor=conn.execute('SELECT root,scheme FROM intel_merkle_anchors WHERE snapshot_sha=%s',(sha,)).fetchone()
        rows=conn.execute('SELECT id,leaf_hash,payload FROM intel_record_versions WHERE snapshot_sha=%s ORDER BY id',(sha,)).fetchall()
        index=next((i for i,row in enumerate(rows) if row[0]==record_id),None)
        if anchor is None or index is None:
            raise HTTPException(404,'Record is not in this snapshot')
        steps=proof([row[1] for row in rows],index)
        payload=rows[index][2]
        audit(conn,'merkle_proof_read',sha+':'+record_id,str(uuid.uuid4()))
    return {'snapshot_sha':sha,'record':payload,'root':anchor[0],'scheme':anchor[1],
            'leaf_hash':rows[index][1],'leaf_index':index,'leaf_count':len(rows),'proof':steps,
            'verified':verify_proof(payload,steps,anchor[0]),'source_licenses':source_licenses()}
