"""Read-only local demo API. Reference: architecture.md evidence/graph interfaces."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from .common import *
from .graph import snapshot

@asynccontextmanager
async def lifespan(app):
    retry(initialize)
    yield

app = FastAPI(title='DW-TADS Synthetic Evidence Demo',lifespan=lifespan)

@app.get('/health')
def health():
    return {'alive':True,'synthetic':True}

@app.get('/ready')
def ready():
    try:
        return readiness()
    except Exception as exc:
        raise HTTPException(503,str(exc)) from exc

@app.get('/graph')
def get_graph():
    return snapshot()

@app.get('/status')
def status():
    with db() as conn:
        evidence = conn.execute('SELECT count(*) FROM evidence').fetchone()[0]
        users = conn.execute('SELECT count(*) FROM users').fetchone()[0]
        pending = conn.execute('SELECT count(*) FROM outbox WHERE NOT sent').fetchone()[0]
    data = snapshot()
    return {'mode':'synthetic-fixtures-only','evidence_rows':evidence,'users':users,
            'minio_objects':sum(1 for _ in objects().list_objects('raw-crawl',recursive=True)),
            'graph_nodes':len(data['nodes']),'graph_edges':len(data['edges']),
            'pending_outbox':pending,'audit_log_chain_valid':verify_audit()}

@app.get('/',response_class=HTMLResponse)
def home():
    return '''<!doctype html><html><head><meta charset="utf-8"><title>Synthetic Evidence Demo</title>
    <style>body{background:#101923;color:#e3edf5;font:17px system-ui;max-width:960px;margin:60px auto;padding:20px}a{color:#7bcaff}pre{background:#1e2d3b;padding:24px;border-radius:12px;white-space:pre-wrap}small{color:#b4c8d8}</style></head>
    <body><small>DW-TADS · LOCAL SYNTHETIC DEMONSTRATION</small><h1>Evidence and graph explorer</h1>
    <p>All records and relationships are supplied fixtures. Relationship confidence values are fixture assertions, not calibrated attribution.</p>
    <p><a href="/docs">API documentation</a> · <a href="/graph">Graph JSON</a> · <a href="http://localhost:7474">Neo4j graph browser</a></p>
    <pre id="status">Loading status…</pre><p>In Neo4j Browser, run:</p><pre>MATCH (a)-[r]-&gt;(b) RETURN a,r,b LIMIT 100</pre>
    <script>fetch('/status').then(r=>{if(!r.ok)throw Error('Status unavailable');return r.json()}).then(x=>document.getElementById('status').textContent=JSON.stringify(x,null,2)).catch(e=>document.getElementById('status').textContent=e.message)</script></body></html>'''
