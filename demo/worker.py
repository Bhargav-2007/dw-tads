"""Evidence consumer. Reference: DEMO-DATA-CONTRACT.md sections 2, 3, 6."""
import asyncio
import threading
from contextlib import asynccontextmanager
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from .common import *

stop = threading.Event()
state = {'ready': False, 'error': None}

class Crawl(BaseModel):
    model_config = ConfigDict(extra='forbid')
    event_id: str = Field(pattern=r'^[a-f0-9]{64}$')
    correlation_id: str
    synthetic: Literal[True]
    sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    minio_bucket: Literal['raw-crawl']
    minio_key: str = Field(pattern=r'^fixtures/posts/[a-f0-9]{64}\.json$')
    captured_at: str
    source_url: str = Field(pattern=r'^fixture://')

def process(raw):
    event = Crawl.model_validate(raw)
    response = objects().get_object(event.minio_bucket,event.minio_key)
    try:
        body = response.read()
    finally:
        response.close()
        response.release_conn()
    if digest(body) != event.sha256:
        raise ValueError('Evidence hash mismatch')
    post = json.loads(body)
    # Accept only an exact record in the bundled synthetic fixture corpus.
    allowed = {digest(canonical(p)) for p in json.loads((DATA/'forum_posts.json').read_text())}
    if event.sha256 not in allowed:
        raise ValueError('Object is outside the bundled fixture corpus')
    with db() as conn:
        fresh = conn.execute("INSERT INTO processed VALUES ('evidence',%s) ON CONFLICT DO NOTHING RETURNING event_id",(event.event_id,)).fetchone()
        if not fresh:
            return
        inserted = conn.execute('INSERT INTO evidence(sha256,source_url,source_type,captured_at,minio_bucket,minio_key,ingested_by) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING sha256',
             (event.sha256,event.source_url,'synthetic-fixture',event.captured_at,event.minio_bucket,event.minio_key,'evidence-demo')).fetchone()
        if inserted:
            audit(conn,'evidence_ingested',event.sha256,event.correlation_id)
            clean = envelope('content.clean',dict(**post,source_sha256=event.sha256,source_url=event.source_url))
            clean['correlation_id'] = event.correlation_id
            queue(conn,'content.clean',clean)

def run():
    consumer = None
    p = None
    try:
        p = producer()
        consumer = KafkaConsumer('crawl.raw',bootstrap_servers=os.environ['KAFKA_BOOTSTRAP'],group_id='synthetic-evidence-v1',
            enable_auto_commit=False,auto_offset_reset='earliest',max_poll_records=10)
        state.update(ready=True,error=None)
        while not stop.is_set():
            flush_outbox(p)
            for records in consumer.poll(timeout_ms=500).values():
                for record in records:
                    raw = None
                    try:
                        raw = json.loads(record.value)
                        retry(lambda: process(raw))
                    except (ValidationError, ValueError, KeyError) as exc:
                        cid = raw.get('correlation_id','invalid') if isinstance(raw,dict) else 'invalid'
                        error = envelope('invalid',dict(error=str(exc),original_topic=record.topic,partition=record.partition,offset=record.offset,original=record.value.decode('utf-8',errors='replace')))
                        log('invalid_message',cid,error=str(exc))
                        with db() as conn:
                            queue(conn,'dlq.crawl.raw',error)
                            queue(conn,'service.errors',dict(error,event_id=error['event_id']+'-error'))
                    flush_outbox(p)
                # Explicit per-partition offset: never commit unprocessed fetched records.
                from kafka.structs import TopicPartition, OffsetAndMetadata
                last = records[-1]
                consumer.commit({TopicPartition(last.topic,last.partition):OffsetAndMetadata(last.offset+1,'')})
    except Exception as exc:
        state.update(ready=False,error=str(exc))
        log('worker_failed','worker',error=str(exc))
        if p:
            try:
                p.send('service.errors',envelope('worker-error',{'error':str(exc)})).get(timeout=3)
            except Exception as report_error:
                log('error_reporting_failed','worker',error=str(report_error))
    finally:
        state['ready'] = False
        if consumer:
            consumer.close(autocommit=False)
        if p:
            p.close(timeout=3)

@asynccontextmanager
async def lifespan(app):
    thread = threading.Thread(target=run,daemon=True)
    thread.start()
    yield
    stop.set()
    await asyncio.to_thread(thread.join,8)

app = FastAPI(lifespan=lifespan)

@app.get('/health')
def health():
    return {'alive':True}

@app.get('/ready')
def ready():
    if not state['ready']:
        raise HTTPException(503,state['error'] or 'starting')
    try:
        return readiness()
    except Exception as exc:
        raise HTTPException(503,str(exc)) from exc
