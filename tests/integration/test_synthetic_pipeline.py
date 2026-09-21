"""Integration checks against the running isolated synthetic stack."""
import json
import time
import uuid
import pytest

pytest.importorskip("kafka", reason="kafka-python is required for legacy live synthetic stack tests")
pytest.importorskip("psycopg", reason="psycopg is required for legacy live synthetic stack tests")

from demo.common import *
from demo.loader import load
from demo.graph import snapshot, seed_graph
from demo.worker import process
from demo.cli import verify, counts
from demo.app import status



def test_01_end_to_end():
    result = verify()
    expected = len(json.loads((DATA/'forum_posts.json').read_text()))
    assert result['evidence_rows'] == expected
    assert result['kafka_messages']['content.clean'] == expected


def test_02_replay_is_idempotent():
    before = status()
    before_topics = counts()
    before_graph = snapshot()
    load()
    seed_graph()
    after = verify()
    for key in ['evidence_rows','minio_objects','graph_nodes','graph_edges']:
        assert before[key] == after[key]
    assert before_topics == counts()
    assert before_graph == snapshot()


def test_03_audit_is_immutable():
    with pytest.raises(psycopg.errors.RaiseException):
        with db() as conn:
            conn.execute("UPDATE audit_log SET action='tampered'")
    assert verify_audit()


def test_04_evidence_bytes_verified():
    with db() as conn:
        rows = conn.execute('SELECT sha256,minio_bucket,minio_key FROM evidence').fetchall()
    for sha,bucket,key in rows:
        response = objects().get_object(bucket,key)
        try:
            assert digest(response.read()) == sha
        finally:
            response.close()
            response.release_conn()


def test_05_bad_hash_rejected():
    with db() as conn:
        sha,key,captured = conn.execute('SELECT sha256,minio_key,captured_at FROM evidence LIMIT 1').fetchone()
    event = envelope('bad-hash',dict(sha256='0'*64,minio_bucket='raw-crawl',minio_key=key,captured_at=captured.isoformat(),source_url='fixture://bad'))
    with pytest.raises(ValueError,match='hash mismatch'):
        process(event)


def test_06_malformed_to_dlq():
    baseline = counts()['dlq.crawl.raw']
    p = producer()
    try:
        p.send('crawl.raw', {'correlation_id':str(uuid.uuid4()),'synthetic':True,'bad':True}).get(timeout=10)
    finally:
        p.close()
    deadline = time.monotonic()+45
    while counts()['dlq.crawl.raw'] <= baseline:
        assert time.monotonic()<deadline,'Malformed message was not quarantined'
        time.sleep(1)
    assert verify_audit()


def test_07_graph_is_explicitly_synthetic():
    data = snapshot()
    assert all(n['properties']['synthetic'] for n in data['nodes'])
    assert all(e['properties']['synthetic'] for e in data['edges'])
    assert len(data['nodes'])==22
    assert len(data['edges'])==20


def test_08_users_passwords_hashed():
    from argon2 import PasswordHasher
    with db() as conn:
        users = dict(conn.execute('SELECT username,password_hash FROM users').fetchall())
    for user in json.loads((DATA/'demo_users.json').read_text())['users']:
        assert PasswordHasher().verify(users[user['username']],user['password'])
