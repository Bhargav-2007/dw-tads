import asyncio
import csv
import html
import io
import json
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from uuid import UUID,uuid4
from xml.etree.ElementTree import Element,SubElement,tostring
import httpx
from fastapi import FastAPI,Depends,HTTPException,BackgroundTasks
from fastapi.responses import HTMLResponse,Response
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from pydantic import BaseModel,ConfigDict,Field
from .contracts import CATALOG,BY_ID,NOTICE,graph_fixture,sha
from .store import database,initialize,audit,verify,now
from .engine import execute

if os.getenv('MOCK_ONLY')!='true':
    raise RuntimeError('MOCK_ONLY=true is mandatory')
security=HTTPBearer(auto_error=False)

def role(credentials: HTTPAuthorizationCredentials | None=Depends(security)):
    if credentials:
        for name in ('admin','analyst','reviewer','auditor'):
            if secrets.compare_digest(credentials.credentials,os.environ['MOCK_'+name.upper()+'_TOKEN']):
                return name
    raise HTTPException(401,'Simulation access token required')

def require(actual,allowed):
    if actual not in allowed:
        raise HTTPException(403,'Role does not permit this simulation operation')

@asynccontextmanager
async def lifespan(app):
    initialize()
    with database() as conn:
        pending=[row[0] for row in conn.execute("SELECT id FROM runs WHERE status IN ('queued','running')")]
    tasks=[asyncio.create_task(execute(ident)) for ident in pending]
    yield
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks,return_exceptions=True)

app=FastAPI(title='DW-TADS Seven-Plane Mock Architecture',version='1.0.0',lifespan=lifespan)

class Start(BaseModel):
    model_config=ConfigDict(extra='forbid')
    run_id: UUID=Field(default_factory=uuid4)
    scenario: Literal['baseline','insufficient-evidence']='baseline'
    fail_service: str | None=None

class Review(BaseModel):
    model_config=ConfigDict(extra='forbid')
    decision: Literal['approve','reject']

@app.get('/health')
def health():
    return {'alive':True,'mock_only':True}

@app.get('/ready')
async def ready():
    with database() as conn:
        conn.execute('SELECT 1')
    async with httpx.AsyncClient(timeout=3,trust_env=False) as client:
        try:
            responses=await asyncio.gather(*(client.get('http://plane-'+str(i)+':8000/ready') for i in range(1,8)))
            for response in responses:
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(503,'A mock plane is unavailable') from exc
    return {'ready':True,'mock_only':True,'planes':7,'simulated_services':len(CATALOG)}

@app.get('/services',dependencies=[Depends(role)])
def services():
    return {'notice':NOTICE,'document_heading_count':78,'actual_inventory_count':len(CATALOG),'services':CATALOG}

@app.post('/runs',status_code=202)
async def start(body: Start,tasks: BackgroundTasks,actor: str=Depends(role)):
    require(actor,('admin','analyst'))
    if body.fail_service:
        require(actor,('admin',))
        if body.fail_service not in BY_ID:
            raise HTTPException(422,'Unknown fault target')
    ident=str(body.run_id)
    with database() as conn:
        existing=conn.execute('SELECT * FROM runs WHERE id=?',(ident,)).fetchone()
        if existing:
            if existing['scenario']!=body.scenario or existing['fail_service']!=body.fail_service:
                raise HTTPException(409,'Run ID already used with different parameters')
            return dict(existing)
        conn.execute('INSERT INTO runs(id,scenario,created_by,status,fail_service,created_at) VALUES (?,?,?,?,?,?)',
            (ident,body.scenario,actor,'queued',body.fail_service,now()))
        audit(conn,ident,'mock_run_created',actor,{'scenario':body.scenario})
    tasks.add_task(execute,ident)
    return {'run_id':ident,'status':'queued','notice':NOTICE}

@app.get('/runs',dependencies=[Depends(role)])
def runs():
    with database() as conn:
        return {'runs':[dict(r) for r in conn.execute('SELECT * FROM runs ORDER BY created_at DESC LIMIT 100')],'notice':NOTICE}

@app.get('/runs/{run_id}',dependencies=[Depends(role)])
def run(run_id: UUID):
    with database() as conn:
        row=conn.execute('SELECT * FROM runs WHERE id=?',(str(run_id),)).fetchone()
        if not row:
            raise HTTPException(404,'Unknown run')
        outputs={r[0]:json.loads(r[1]) for r in conn.execute('SELECT service,response FROM steps WHERE run_id=?',(str(run_id),))}
    return {**dict(row),'completed_services':len(outputs),'total_services':len(CATALOG),'outputs':outputs,'notice':NOTICE}

@app.post('/runs/{run_id}/retry',status_code=202)
async def retry_run(run_id: UUID,tasks: BackgroundTasks,actor: str=Depends(role)):
    require(actor,('admin',))
    ident=str(run_id)
    with database() as conn:
        row=conn.execute('SELECT status FROM runs WHERE id=?',(ident,)).fetchone()
        if not row:
            raise HTTPException(404,'Unknown run')
        if row[0]!='failed':
            raise HTTPException(409,'Only failed runs can be retried')
        conn.execute("UPDATE runs SET status='queued',error=NULL WHERE id=?",(ident,))
        audit(conn,ident,'mock_retry_requested',actor,{})
    tasks.add_task(execute,ident)
    return {'run_id':ident,'status':'queued','notice':NOTICE}

@app.post('/runs/{run_id}/review')
def review(run_id: UUID,body: Review,actor: str=Depends(role)):
    require(actor,('reviewer',))
    with database() as conn:
        row=conn.execute('SELECT * FROM runs WHERE id=?',(str(run_id),)).fetchone()
        if not row:
            raise HTTPException(404,'Unknown run')
        if row['status']!='awaiting_review':
            raise HTTPException(409,'Run is not awaiting review')
        status='approved' if body.decision=='approve' else 'rejected'
        conn.execute('UPDATE runs SET status=?,reviewed_by=?,decision=? WHERE id=?',(status,actor,body.decision,str(run_id)))
        audit(conn,str(run_id),'mock_review_'+body.decision,actor,{})
    return {'run_id':str(run_id),'status':status,'notice':NOTICE}

@app.get('/audit',dependencies=[Depends(role)])
def audit_state():
    with database() as conn:
        count=conn.execute('SELECT count(*) FROM events').fetchone()[0]
    return {'valid':verify(),'event_count':count,'notice':NOTICE}

@app.get('/graph',dependencies=[Depends(role)])
def graph():
    return {**graph_fixture(),'notice':NOTICE}

@app.get('/runs/{run_id}/export')
def export(run_id: UUID,format: Literal['json','csv','html','graphml']='json',actor: str=Depends(role)):
    require(actor,('admin','analyst','reviewer'))
    data=run(run_id)
    headers={'Content-Disposition':'attachment; filename="MOCK-'+str(run_id)+'.'+format+'"'}
    with database() as conn:
        audit(conn,str(run_id),'mock_export',actor,{'format':format})
    if format=='json':
        return Response(json.dumps(data,ensure_ascii=False),media_type='application/json',headers=headers)
    if format=='csv':
        stream=io.StringIO();writer=csv.writer(stream);writer.writerow(['notice','service','plane','result_hash','mock_output'])
        for service,result in data['outputs'].items():
            writer.writerow([NOTICE,service,result['plane'],result['result_hash'],json.dumps(result['output'])])
        return Response(stream.getvalue(),media_type='text/csv',headers=headers)
    if format=='graphml':
        root=Element('graphml',xmlns='http://graphml.graphdrawing.org/xmlns')
        key=SubElement(root,'key',id='notice',attrib={'for':'graph','attr.name':'notice','attr.type':'string'})
        graph=SubElement(root,'graph',id='mock',edgedefault='directed')
        SubElement(graph,'data',key='notice').text=NOTICE
        fixture=graph_fixture()
        for n in fixture['nodes']: SubElement(graph,'node',id=n['id'])
        for e in fixture['edges']: SubElement(graph,'edge',id=e['id'],source=e['source'],target=e['target'])
        return Response(tostring(root,encoding='utf-8',xml_declaration=True),media_type='application/graphml+xml',headers=headers)
    return HTMLResponse('<!doctype html><meta charset="utf-8"><h1>ARCHITECTURE SIMULATION</h1><p>'+html.escape(NOTICE)+'</p><pre>'+html.escape(json.dumps(data,indent=2))+'</pre>',headers=headers)

@app.get('/',response_class=HTMLResponse)
def home():
    return Path('/app/mock_arch/index.html').read_text()
