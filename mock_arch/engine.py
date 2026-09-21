"""Seven-plane fixture orchestration with durable progress and retry."""
import asyncio
import json
import os
import httpx
from .contracts import CATALOG,BY_ID,sha
from .store import database,audit

lock=asyncio.Lock()

async def execute(run_id):
    async with lock:
        with database() as conn:
            run=conn.execute('SELECT * FROM runs WHERE id=?',(run_id,)).fetchone()
            if not run or run['status'] not in ('queued','running'):
                return
            conn.execute("UPDATE runs SET status='running',error=NULL WHERE id=?",(run_id,))
        upstream='0'*64
        try:
            async with httpx.AsyncClient(timeout=10,trust_env=False) as client:
                for item in CATALOG:
                    service=item['id']
                    with database() as conn:
                        saved=conn.execute('SELECT response FROM steps WHERE run_id=? AND service=?',(run_id,service)).fetchone()
                        if saved:
                            upstream=json.loads(saved['response'])['result_hash']
                            continue
                        if run['fail_service']==service and not run['fault_used']:
                            conn.execute("UPDATE runs SET status='failed',fault_used=1,error='Injected one-shot mock failure' WHERE id=?",(run_id,))
                            audit(conn,run_id,'mock_fault_injected','orchestrator',{'service':service})
                            return
                    response=await client.post('http://plane-'+str(item['plane'])+':8000/services/'+service+'/simulate',
                        json={'run_id':run_id,'scenario':run['scenario'],'upstream_hash':upstream},
                        headers={'X-Mock-Internal':os.environ['MOCK_INTERNAL_TOKEN']})
                    response.raise_for_status()
                    result=response.json()
                    payload={k:v for k,v in result.items() if k!='result_hash'}
                    if result.get('synthetic') is not True or result.get('operational') is not False or result['result_hash']!=sha(payload):
                        raise ValueError('Mock service response failed integrity checks')
                    with database() as conn:
                        conn.execute('INSERT INTO steps VALUES (?,?,?)',(run_id,service,json.dumps(result)))
                        audit(conn,run_id,'mock_service_completed','orchestrator',{'service':service,'result_hash':result['result_hash'],'plane':item['plane']})
                    upstream=result['result_hash']
            with database() as conn:
                conn.execute("UPDATE runs SET status='awaiting_review' WHERE id=?",(run_id,))
                audit(conn,run_id,'mock_workflow_finished','orchestrator',{'services':len(CATALOG),'final_hash':upstream})
        except Exception as exc:
            with database() as conn:
                conn.execute("UPDATE runs SET status='failed',error=? WHERE id=?",(str(exc),run_id))
                audit(conn,run_id,'mock_workflow_failed','orchestrator',{'error':str(exc)})
