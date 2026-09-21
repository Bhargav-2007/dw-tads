import json
import os
from datetime import datetime
from fastapi.testclient import TestClient
import pytest
from intel.app import app,csv_cell
from intel.common import db,graph,verify_audit
from intel.normalize import parse
from intel.worker import process,SnapshotEvent

client=TestClient(app)
HEADERS={'Authorization':'Bearer '+os.environ['INTEL_READER_TOKEN']}

def test_authentication_required():
    for path in ['/status','/records','/graph','/export']:
        assert client.get(path).status_code==401
    assert client.get('/records',headers={'Authorization':'Bearer wrong'}).status_code==401

def test_live_sources_processed():
    result=client.get('/status',headers=HEADERS)
    assert result.status_code==200,result.text
    status=result.json()
    assert status['pending_snapshots']==0,status
    assert all(s['last_success'] and not s['error'] for s in status['sources']),status
    counts={r['kind']:r['count'] for r in status['records']}
    assert counts['vulnerability']>100
    assert counts['malware']>100
    assert counts['technique']>100
    assert status['relationships']>100
    assert status['audit_chain_valid']

def test_query_and_timeline():
    result=client.get('/records?kind=vulnerability&limit=5',headers=HEADERS).json()
    assert len(result['results'])==5
    assert all(r['kind']=='vulnerability' and r['source']=='cisa-kev' for r in result['results'])
    assert client.get('/records?start=2026-01-02&end=2026-01-01',headers=HEADERS).status_code==422
    assert client.get('/records?limit=1001',headers=HEADERS).status_code==422
    injection=client.get('/records',params={'q':"' OR 1=1 --"},headers=HEADERS).json()
    assert injection['total']==0

def test_snapshot_integrity():
    row=client.get('/records?kind=vulnerability&limit=1',headers=HEADERS).json()['results'][0]
    result=client.get('/evidence/'+row['snapshot_sha'],headers=HEADERS)
    assert result.status_code==200,result.text
    assert result.json()['integrity_verified']

def test_replay_idempotency():
    with db() as conn:
        before=conn.execute('SELECT count(*) FROM intel_records').fetchone()[0]
        rows=conn.execute('SELECT source,sha256,object_key FROM intel_snapshots WHERE processed_at IS NOT NULL').fetchall()
    for source,sha,key in rows:
        process(dict(event_id=sha,sha256=sha,source=source,object_key=key,correlation_id='replay-test'))
    with db() as conn:
        assert conn.execute('SELECT count(*) FROM intel_records').fetchone()[0]==before

def test_exports():
    for format,mime in [('csv','text/csv'),('json','application/json'),('html','text/html')]:
        result=client.get('/export',params={'format':format,'limit':2},headers=HEADERS)
        assert result.status_code==200,result.text
        assert mime in result.headers['content-type']
        assert result.headers['x-exported-count']=='2'
        assert 'MITRE' in result.text
    assert csv_cell('=SUM(A1:A3)').startswith("'")
    assert csv_cell('  @SUM(A1)').startswith("'")

def test_graph_technical_only():
    result=client.get('/graph?source=mitre-attack&limit=1000',headers=HEADERS).json()
    assert result['nodes']
    assert all(n['kind'] in ('malware','technique') for n in result['nodes'])
    assert result['edges']
    assert all(e['type']=='USES' for e in result['edges'])

def test_parser_excludes_identity_objects():
    doc={'type':'bundle','objects':[
        {'type':'identity','id':'identity--test','name':'Not indexed'},
        {'type':'intrusion-set','id':'intrusion-set--test','name':'Not indexed'},
        {'type':'malware','id':'malware--test','name':'Test malware','modified':'2026-01-01T00:00:00Z'},
        {'type':'attack-pattern','id':'attack-pattern--test','name':'Test technique','modified':'2026-01-01T00:00:00Z'},
        {'type':'relationship','relationship_type':'uses','source_ref':'malware--test','target_ref':'attack-pattern--test'}]}
    records,edges=parse('mitre-attack',doc)
    assert len(records)==2 and len(edges)==1
    assert {r['kind'] for r in records}=={'malware','technique'}

def test_malformed_validation():
    with pytest.raises(ValueError):
        SnapshotEvent.model_validate({'source':'arbitrary-url'})
    with pytest.raises(ValueError):
        parse('cisa-kev',{'vulnerabilities':[]})

def test_audit_valid_after_reads_and_exports():
    assert verify_audit()

def test_malformed_event_reaches_dlq():
    import time
    from kafka import KafkaConsumer
    from kafka.structs import TopicPartition
    from intel.common import producer
    consumer=KafkaConsumer(bootstrap_servers=os.environ['KAFKA_BOOTSTRAP'],enable_auto_commit=False)
    def count():
        parts=[TopicPartition('dlq.intel.raw',p) for p in consumer.partitions_for_topic('dlq.intel.raw')]
        return sum(consumer.end_offsets(parts).values())
    try:
        baseline=count()
        p=producer()
        try:
            p.send('intel.raw',{'source':'invalid-test-source','correlation_id':'test-dlq'}).get(timeout=10)
        finally:
            p.close()
        deadline=time.monotonic()+40
        while count()==baseline:
            assert time.monotonic()<deadline,'No dead-letter event produced'
            time.sleep(1)
    finally:
        consumer.close()
