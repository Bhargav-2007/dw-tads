"""Stateless, fixture-only services hosted by one process per architecture plane."""
import os
import secrets
from uuid import UUID
from typing import Literal
from fastapi import FastAPI,Header,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from .contracts import BY_ID,result

if os.getenv('MOCK_ONLY')!='true':
    raise RuntimeError('This service may run only with MOCK_ONLY=true')
PLANE=int(os.environ['MOCK_PLANE'])
if PLANE not in range(1,8):
    raise RuntimeError('Invalid mock plane')
app=FastAPI(title='Architecture Plane '+str(PLANE)+' Simulation')

class SimulationRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    run_id: UUID
    scenario: Literal['baseline','insufficient-evidence']
    upstream_hash: str=Field(pattern=r'^[a-f0-9]{64}$')

@app.get('/health')
@app.get('/ready')
def health():
    return {'ready':True,'plane':PLANE,'mock_only':True,'service_count':sum(e['plane']==PLANE for e in BY_ID.values())}

@app.post('/services/{service}/simulate')
def simulate(service: str,body: SimulationRequest,x_mock_internal: str=Header('')):
    if not secrets.compare_digest(x_mock_internal,os.environ['MOCK_INTERNAL_TOKEN']):
        raise HTTPException(401,'Internal simulation token required')
    if service not in BY_ID or BY_ID[service]['plane']!=PLANE:
        raise HTTPException(404,'Service not hosted by this plane')
    return result(service,body.scenario,str(body.run_id),body.upstream_hash)
