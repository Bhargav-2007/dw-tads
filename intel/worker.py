"""Idempotent evidence normalization and technical graph projection."""
import asyncio
import threading
from contextlib import asynccontextmanager
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field
from fastapi import FastAPI,HTTPException
from kafka import KafkaConsumer
from kafka.structs import TopicPartition,OffsetAndMetadata
from .common import *
from .normalize import parse
from .integrity import archive

stop=threading.Event()
state={'running':False,'error':None}

class SnapshotEvent(BaseModel):
    model_config=ConfigDict(extra='forbid')
    event_id: str=Field(pattern=r'^[a-f0-9]{64}$')
    correlation_id: str
    source: Literal['cisa-kev','mitre-attack']
    sha256: str=Field(pattern=r'^[a-f0-9]{64}$')
    object_key: str


def process(raw):
    event=SnapshotEvent.model_validate(raw)
    if event.event_id!=event.sha256 or event.object_key!=event.source+'/'+event.sha256+'.json':
        raise ValueError('Invalid snapshot reference')
    with db() as conn:
        snapshot=conn.execute('SELECT source,processed_at,object_version FROM intel_snapshots WHERE sha256=%s',(event.sha256,)).fetchone()
        if snapshot is None or snapshot[0]!=event.source:
            raise ValueError('Unknown snapshot')
        if snapshot[1]:
            return
    response=objects().get_object(BUCKET,event.object_key,version_id=snapshot[2])
    try:
        body=response.read()
    finally:
        response.close(); response.release_conn()
    if digest(body)!=event.sha256:
        raise ValueError('Snapshot hash mismatch')
    records,edges=parse(event.source,json.loads(body))
    with db() as conn:
        conn.execute('SELECT pg_advisory_xact_lock(424248)')
        if conn.execute('SELECT processed_at FROM intel_snapshots WHERE sha256=%s',(event.sha256,)).fetchone()[0]:
            return
        archive(conn,event.sha256,records,edges,event.correlation_id)
        latest=conn.execute('SELECT last_sha FROM intel_sources WHERE name=%s',(event.source,)).fetchone()[0]
        if latest!=event.sha256:
            conn.execute('UPDATE intel_snapshots SET processed_at=NOW() WHERE sha256=%s',(event.sha256,))
            audit(conn,'superseded_snapshot_skipped',event.sha256,event.correlation_id)
            return
        conn.execute('UPDATE intel_records SET active=FALSE WHERE source=%s',(event.source,))
        values=[(r['id'],r['source'],r['external_id'],r['kind'],r['title'],r['description'],r['published_at'],r['source_url'],event.sha256,Jsonb(r['data'])) for r in records]
        with conn.cursor() as cur:
            cur.executemany('''INSERT INTO intel_records(id,source,external_id,kind,title,description,published_at,source_url,snapshot_sha,data)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT(id) DO UPDATE SET title=EXCLUDED.title,description=EXCLUDED.description,
                published_at=EXCLUDED.published_at,source_url=EXCLUDED.source_url,snapshot_sha=EXCLUDED.snapshot_sha,
                data=EXCLUDED.data,last_seen=NOW(),active=TRUE''',values)
        conn.execute('DELETE FROM intel_relationships WHERE source_id IN (SELECT id FROM intel_records WHERE source=%s)',(event.source,))
        with conn.cursor() as cur:
            cur.executemany('INSERT INTO intel_relationships VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING',[(e['source_id'],e['target_id'],e['type'],event.sha256) for e in edges])
        observed=conn.execute('SELECT captured_at FROM intel_snapshots WHERE sha256=%s',(event.sha256,)).fetchone()[0].isoformat()
        # Projection is idempotent. If the SQL transaction fails after graph commit, replay repairs it.
        with graph() as driver,driver.session() as session:
            def project(tx):
                tx.run('MATCH (n:IntelRecord {source:$source}) SET n.active=false',source=event.source).consume()
                tx.run('UNWIND $rows AS row MERGE (n:IntelRecord {id:row.id}) SET n.source=row.source,n.kind=row.kind,n.title=row.title,n.external_id=row.external_id,n.source_url=row.source_url,n.active=true,n.snapshot_sha=$sha,n.valid_from=$observed,n.recorded_at=$recorded,n.classification="U"',rows=records,sha=event.sha256,observed=observed,recorded=now()).consume()
                tx.run('MATCH (a:IntelRecord {source:$source})-[r:USES]->(:IntelRecord) DELETE r',source=event.source).consume()
                tx.run('UNWIND $rows AS row MATCH (a:IntelRecord {id:row.source_id}) MATCH (b:IntelRecord {id:row.target_id}) MERGE (a)-[r:USES]->(b) SET r.source=$source,r.snapshot_sha=$sha,r.valid_from=$observed,r.recorded_at=$recorded,r.classification="U"',rows=edges,source=event.source,sha=event.sha256,observed=observed,recorded=now()).consume()
            session.execute_write(project)
        conn.execute('UPDATE intel_snapshots SET processed_at=NOW() WHERE sha256=%s',(event.sha256,))
        audit(conn,'public_snapshot_processed',event.sha256,event.correlation_id)
    log('snapshot_processed',event.correlation_id,source=event.source,records=len(records),relationships=len(edges))


def run():
    consumer=None
    p=None
    try:
        p=producer()
        consumer=KafkaConsumer('intel.raw',bootstrap_servers=os.environ['KAFKA_BOOTSTRAP'],group_id='public-intel-v1',enable_auto_commit=False,auto_offset_reset='earliest',max_poll_records=1,max_poll_interval_ms=600000)
        state['running']=True
        while not stop.is_set():
            flush_outbox(p)
            for partition,records in consumer.poll(timeout_ms=500).items():
                for record in records:
                    try:
                        payload=json.loads(record.value)
                        retry(lambda:process(payload))
                    except (ValueError,KeyError,TypeError) as exc:
                        cid=str(uuid.uuid4())
                        error=dict(event_id=digest(record.value+str(record.offset).encode()+str(record.partition).encode()),correlation_id=cid,error=str(exc),partition=record.partition,offset=record.offset)
                        with db() as conn:
                            queue(conn,'dlq.intel.raw',error)
                            queue(conn,'intel.errors',dict(error,event_id=error['event_id']+'-error'))
                        log('snapshot_rejected',cid,error=str(exc))
                    flush_outbox(p)
                    consumer.commit({partition:OffsetAndMetadata(record.offset+1,'')})
    except Exception as exc:
        state['error']=str(exc)
        log('intel_worker_failed','worker',error=str(exc))
        if p:
            try:
                p.send('intel.errors',dict(event_id=str(uuid.uuid4()),correlation_id='worker',error=str(exc))).get(timeout=3)
            except Exception as report_error:
                log('error_reporting_failed','worker',error=str(report_error))
    finally:
        state['running']=False
        if consumer:
            consumer.close(autocommit=False)
        if p:
            p.close(timeout=3)

@asynccontextmanager
async def lifespan(app):
    thread=threading.Thread(target=run,daemon=True)
    thread.start()
    yield
    stop.set()
    await asyncio.to_thread(thread.join,8)

app=FastAPI(lifespan=lifespan)
@app.get('/health')
def health():
    return {'alive':True}
@app.get('/ready')
def ready():
    if not state['running']:
        raise HTTPException(503,state['error'] or 'starting')
    return health_dependencies()
