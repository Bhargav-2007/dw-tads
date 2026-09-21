"""History, storage versioning, migrations and Merkle integrity tests."""
from datetime import timedelta,datetime,timezone
import hashlib
import uuid
import io
import pytest
import psycopg
from fastapi.testclient import TestClient
from intel.app import app
from intel.common import db,objects,BUCKET,canonical,verify_audit
from intel.integrity import leaf,root,proof,verify_proof,backfill
from intel.migrate import migrate
import os
HEADERS={'Authorization':'Bearer '+os.environ['INTEL_READER_TOKEN']}

client=TestClient(app)

@pytest.mark.parametrize('size',[1,2,3,7,8])
def test_merkle_vectors_and_tamper(size):
    records=[{'id':str(i),'value':'example'} for i in range(size)]
    hashes=[hashlib.sha256(b'\x00'+canonical(r)).hexdigest() for r in records]
    expected=list(hashes)
    while len(expected)>1:
        if len(expected)%2:
            expected.append(expected[-1])
        expected=[hashlib.sha256(b'\x01'+bytes.fromhex(expected[i])+bytes.fromhex(expected[i+1])).hexdigest() for i in range(0,len(expected),2)]
    assert root(hashes)==expected[0]
    for i,record in enumerate(records):
        assert verify_proof(record,proof(hashes,i),expected[0])
        assert not verify_proof({**record,'value':'tampered'},proof(hashes,i),expected[0])

def test_deployed_merkle_proof():
    row=client.get('/records?kind=vulnerability&limit=1',headers=HEADERS).json()['results'][0]
    result=client.get('/evidence/'+row['snapshot_sha']+'/merkle/'+row['id'],headers=HEADERS)
    assert result.status_code==200,result.text
    data=result.json()
    assert data['verified']
    assert verify_proof(data['record'],data['proof'],data['root'])
    assert not verify_proof({**data['record'],'title':'altered'},data['proof'],data['root'])

def test_as_of_boundaries():
    with db() as conn:
        first,last=conn.execute('SELECT min(captured_at),max(captured_at) FROM intel_snapshots WHERE processed_at IS NOT NULL').fetchone()
    before=client.get('/records',params={'as_of':(first-timedelta(microseconds=1)).isoformat()},headers=HEADERS)
    assert before.status_code==200,before.text
    assert before.json()['total']==0
    current=client.get('/records?limit=1',headers=HEADERS).json()['total']
    historical=client.get('/records',params={'as_of':last.isoformat(),'limit':1},headers=HEADERS)
    assert historical.status_code==200,historical.text
    assert historical.json()['total']==current
    assert 'valid_from' in historical.json()['results'][0]
    assert client.get('/records?as_of=2026-01-01T00:00:00',headers=HEADERS).status_code==422

def test_historical_graph_and_export():
    stamp=datetime.now(timezone.utc).isoformat()
    result=client.get('/graph',params={'as_of':stamp,'source':'mitre-attack','limit':1000},headers=HEADERS)
    assert result.status_code==200,result.text
    data=result.json()
    assert data['nodes'] and data['edges']
    result=client.get('/export',params={'as_of':stamp,'format':'json','limit':1},headers=HEADERS)
    assert result.status_code==200
    assert result.json()['as_of']

def test_history_and_anchors_append_only():
    for table in ['intel_record_versions','intel_relationship_versions','intel_merkle_anchors']:
        with pytest.raises(psycopg.errors.RaiseException,match='append-only'):
            with db() as conn:
                conn.execute('DELETE FROM '+table)
    assert verify_audit()

def test_migration_and_backfill_idempotency():
    with db() as conn:
        before=conn.execute('SELECT count(*) FROM intel_record_versions').fetchone()[0]
        versions=conn.execute('SELECT count(*) FROM intel_schema_migrations').fetchone()[0]
        migrate(conn)
        assert conn.execute('SELECT count(*) FROM intel_schema_migrations').fetchone()[0]==versions
    assert backfill()==0
    with db() as conn:
        assert conn.execute('SELECT count(*) FROM intel_record_versions').fetchone()[0]==before

def test_object_versioning_recovers_previous_bytes():
    client=objects()
    assert client.get_bucket_versioning(BUCKET).status=='Enabled'
    key='verification/'+str(uuid.uuid4())
    versions=[]
    try:
        for body in [b'original evidence',b'new version']:
            result=client.put_object(BUCKET,key,io.BytesIO(body),len(body))
            versions.append(result.version_id)
        assert all(versions) and versions[0]!=versions[1]
        response=client.get_object(BUCKET,key,version_id=versions[0])
        try:
            assert response.read()==b'original evidence'
        finally:
            response.close(); response.release_conn()
    finally:
        # Only versions created by this test's unique key are removed.
        for version in versions:
            client.remove_object(BUCKET,key,version_id=version)

def test_modified_applied_migration_rejected(monkeypatch):
    from intel import migrate as module
    class ChangedMigration:
        name='001_history_and_integrity.sql'
        def read_text(self,encoding):
            return 'SELECT 1; -- modified'
    monkeypatch.setattr(module.Path,'glob',lambda self,pattern:[ChangedMigration()])
    with pytest.raises(RuntimeError,match='Applied migration was modified'):
        with db() as conn:
            migrate(conn)

def test_new_snapshot_archive_transaction():
    from intel.integrity import archive
    from intel.common import digest
    records=[{'id':'cisa-kev:CVE-test-archive','source':'cisa-kev','external_id':'CVE-test-archive',
        'kind':'vulnerability','title':'transaction-only test','description':'test',
        'published_at':'2026-01-01T00:00:00+00:00','source_url':'https://www.cisa.gov/','data':{}}]
    sha=digest(canonical(records))
    with db() as conn:
        with conn.transaction(force_rollback=True):
            conn.execute('INSERT INTO intel_snapshots(sha256,source,object_key,captured_at,byte_count) VALUES (%s,%s,%s,NOW(),1)',(sha,'cisa-kev','transaction-only-test'))
            archive(conn,sha,records,[],'archive-test')
            archive(conn,sha,records,[],'archive-test-replay')
            count=conn.execute('SELECT count(*) FROM intel_record_versions WHERE snapshot_sha=%s',(sha,)).fetchone()[0]
            assert count==1
            assert conn.execute('SELECT root FROM intel_merkle_anchors WHERE snapshot_sha=%s',(sha,)).fetchone()[0]==leaf(records[0])
    with db() as conn:
        assert conn.execute('SELECT count(*) FROM intel_snapshots WHERE sha256=%s',(sha,)).fetchone()[0]==0
    assert verify_audit()
