"""Shared infrastructure. Reference: architecture.md sections 3, 5, 6."""
import hashlib
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from minio import Minio
from neo4j import GraphDatabase
from psycopg.types.json import Jsonb

DATA = Path('/app/tests/data')
TOPICS = ['crawl.raw', 'content.clean', 'scan.raw', 'chain.tx', 'audit.events', 'service.errors', 'dlq.crawl.raw']
logging.basicConfig(level=logging.INFO)
logging.getLogger('kafka').setLevel(logging.WARNING)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def digest(value):
    return hashlib.sha256(value).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def log(event, correlation_id, **fields):
    logging.info(json.dumps(dict(event=event, correlation_id=correlation_id, **fields)))

def db():
    return psycopg.connect(connect_timeout=3)

def graph():
    return GraphDatabase.driver(os.environ['NEO4J_URI'], auth=(os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD']), connection_timeout=3)

def objects():
    return Minio(os.environ['MINIO_ENDPOINT'], access_key=os.environ['MINIO_ACCESS_KEY'], secret_key=os.environ['MINIO_SECRET_KEY'], secure=False)

def producer():
    return KafkaProducer(bootstrap_servers=os.environ['KAFKA_BOOTSTRAP'], value_serializer=canonical, acks='all', retries=5, request_timeout_ms=5000, max_block_ms=5000)

def retry(fn):
    for attempt in range(5):
        try:
            return fn()
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)

def audit(conn, event, resource, correlation_id):
    conn.execute('SELECT pg_advisory_xact_lock(424242)')
    previous = conn.execute('SELECT this_hash FROM audit_log ORDER BY audit_id DESC LIMIT 1').fetchone()
    previous = previous[0] if previous else '0' * 64
    payload = dict(event_type=event, actor_user='synthetic-demo', action=event, resource=resource,
                   query_hash=None, result_hash=None, ts=now(), metadata={'correlation_id': correlation_id, 'synthetic': True})
    value = digest(previous.encode() + canonical(payload))
    conn.execute('INSERT INTO audit_log(event_type,actor_user,action,resource,prev_hash,this_hash,ts,metadata) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                 (event,'synthetic-demo',event,resource,previous,value,payload['ts'],Jsonb(payload['metadata'])))

def verify_audit():
    with db() as conn:
        rows = conn.execute('SELECT event_type,actor_user,action,resource,query_hash,result_hash,ts,metadata,prev_hash,this_hash FROM audit_log ORDER BY audit_id').fetchall()
    previous = '0' * 64
    for row in rows:
        payload = dict(zip(['event_type','actor_user','action','resource','query_hash','result_hash','ts','metadata'],row[:8]))
        payload['ts'] = payload['ts'].isoformat()
        if row[8] != previous or digest(previous.encode()+canonical(payload)) != row[9]:
            return False
        previous = row[9]
    return True

def queue(conn, topic, payload):
    conn.execute('INSERT INTO outbox(event_id,topic,payload) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING',
                 (payload['event_id'],topic,Jsonb(payload)))

def flush_outbox(p):
    with db() as conn:
        conn.execute('SELECT pg_advisory_xact_lock(424243)')
        rows = conn.execute('SELECT id,topic,payload FROM outbox WHERE NOT sent ORDER BY id').fetchall()
        for ident, topic, payload in rows:
            retry(lambda: p.send(topic, payload).get(timeout=10))
            conn.execute('UPDATE outbox SET sent=TRUE WHERE id=%s',(ident,))

def initialize():
    admin = KafkaAdminClient(bootstrap_servers=os.environ['KAFKA_BOOTSTRAP'])
    try:
        existing = admin.list_topics()
        for topic in TOPICS:
            if topic not in existing:
                try:
                    admin.create_topics([NewTopic(topic,3,1)])
                except TopicAlreadyExistsError:
                    log('topic_exists', 'startup', topic=topic)
    finally:
        admin.close()
    client = objects()
    if not client.bucket_exists('raw-crawl'):
        client.make_bucket('raw-crawl')

def readiness():
    with db() as conn:
        conn.execute('SELECT 1')
    with graph() as driver:
        driver.verify_connectivity()
    objects().list_buckets()
    p = producer()
    try:
        if not p.bootstrap_connected():
            raise RuntimeError('Kafka unavailable')
    finally:
        p.close(timeout=2)
    return {'ready': True, 'mode': 'synthetic-fixtures-only'}

def envelope(kind, value):
    event_id = digest(canonical({'kind': kind, 'value': value}))
    return dict(event_id=event_id, correlation_id=str(uuid.uuid5(uuid.NAMESPACE_URL,event_id)), synthetic=True, **value)
