"""Scheduled downloads from two fixed official public feed URLs."""
import asyncio
import io
import threading
from contextlib import asynccontextmanager
import httpx
from minio.error import S3Error
from fastapi import FastAPI, HTTPException
from .common import *
from .normalize import parse

stop=threading.Event()
state={'running':False}
MAX_BYTES=100*1024*1024


def download(url):
    with httpx.Client(timeout=60,follow_redirects=False,trust_env=False) as client:
        with client.stream('GET',url,headers={'User-Agent':'DW-TADS-public-intel/2.0'}) as response:
            response.raise_for_status()
            result=bytearray()
            for chunk in response.iter_bytes():
                result.extend(chunk)
                if len(result)>MAX_BYTES:
                    raise ValueError('Feed exceeds 100 MiB size limit')
            return bytes(result)


def collect():
    result={}
    with db() as lock:
        if not lock.execute('SELECT pg_try_advisory_lock(424247)').fetchone()[0]:
            return {'busy':True}
        for source,url in FEEDS.items():
            cid=str(uuid.uuid4())
            with db() as conn:
                conn.execute('UPDATE intel_sources SET last_attempt=NOW() WHERE name=%s',(source,))
            try:
                body=retry(lambda:download(url))
                parse(source,json.loads(body))
                sha=digest(body)
                key=source+'/'+sha+'.json'
                client=objects()
                try:
                    stored=client.stat_object(BUCKET,key)
                    version=stored.version_id
                except S3Error as exc:
                    if exc.code!='NoSuchKey':
                        raise
                    stored=client.put_object(BUCKET,key,io.BytesIO(body),len(body),content_type='application/json')
                    version=stored.version_id
                response=client.get_object(BUCKET,key)
                try:
                    if digest(response.read())!=sha:
                        raise ValueError('Stored snapshot hash mismatch')
                finally:
                    response.close(); response.release_conn()
                with db() as conn:
                    inserted=conn.execute('INSERT INTO intel_snapshots(sha256,source,object_key,captured_at,byte_count,processed_at) VALUES (%s,%s,%s,NOW(),%s,NULL) ON CONFLICT DO NOTHING RETURNING sha256',(sha,source,key,len(body))).fetchone()
                    conn.execute('UPDATE intel_snapshots SET object_version=COALESCE(object_version,%s) WHERE sha256=%s',(version,sha))
                    conn.execute('UPDATE intel_sources SET last_success=NOW(),last_sha=%s,error=NULL WHERE name=%s',(sha,source))
                    if inserted:
                        queue(conn,'intel.raw',dict(event_id=sha,correlation_id=cid,source=source,sha256=sha,object_key=key))
                        audit(conn,'public_snapshot_downloaded',source+':'+sha,cid)
                result[source]={'sha256':sha,'new_snapshot':bool(inserted),'bytes':len(body)}
                log('feed_downloaded',cid,source=source,bytes=len(body))
            except Exception as exc:
                log('feed_error',cid,source=source,error=str(exc))
                with db() as conn:
                    conn.execute('UPDATE intel_sources SET error=%s WHERE name=%s',(str(exc),source))
                    queue(conn,'intel.errors',dict(event_id=cid,correlation_id=cid,source=source,error=str(exc),occurred_at=now()))
                    audit(conn,'public_feed_failed',source,cid)
                result[source]={'error':str(exc)}
        p=producer()
        try:
            flush_outbox(p)
        finally:
            p.close(timeout=3)
    return result


def run():
    state['running']=True
    try:
        while not stop.is_set():
            try:
                collect()
            except Exception as exc:
                log('collector_failed','collector',error=str(exc))
            stop.wait(max(60,int(os.getenv('FEED_INTERVAL_SECONDS','21600'))))
    finally:
        state['running']=False

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
        raise HTTPException(503,'Collector stopped')
    return health_dependencies()

if __name__=='__main__':
    print(json.dumps(collect(),indent=2))
