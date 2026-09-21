import json
import os
import uuid
from pathlib import Path
from demo.common import db, graph, objects, producer, retry, canonical, digest, now, log, queue, flush_outbox, verify_audit
from psycopg.types.json import Jsonb
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

FEEDS = {
    'cisa-kev': 'https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json',
    'mitre-attack': 'https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json',
}
TOPICS = ['intel.raw','intel.errors','dlq.intel.raw']
BUCKET = 'public-intelligence'


def audit(conn, action, resource, cid):
    conn.execute('SELECT pg_advisory_xact_lock(424242)')
    previous = conn.execute('SELECT this_hash FROM audit_log ORDER BY audit_id DESC LIMIT 1').fetchone()
    previous = previous[0] if previous else '0'*64
    payload = dict(event_type=action, actor_user='public-intel',action=action,resource=resource,
                   query_hash=None,result_hash=None,ts=now(),metadata={'correlation_id':cid,'synthetic':False})
    sha = digest(previous.encode()+canonical(payload))
    conn.execute('INSERT INTO audit_log(event_type,actor_user,action,resource,prev_hash,this_hash,ts,metadata) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
        (action,'public-intel',action,resource,previous,sha,payload['ts'],Jsonb(payload['metadata'])))


def initialize():
    with db() as conn:
        conn.execute('SELECT pg_advisory_xact_lock(424246)')
        conn.execute(Path('/app/intel/schema.sql').read_text(encoding='utf-8-sig'))
        from .migrate import migrate
        migrate(conn)
        for name,url in FEEDS.items():
            conn.execute('INSERT INTO intel_sources(name,url) VALUES (%s,%s) ON CONFLICT(name) DO UPDATE SET url=EXCLUDED.url',(name,url))
    client = objects()
    if not client.bucket_exists(BUCKET):
        client.make_bucket(BUCKET)
    from minio.versioningconfig import VersioningConfig, ENABLED
    client.set_bucket_versioning(BUCKET,VersioningConfig(ENABLED))
    admin = KafkaAdminClient(bootstrap_servers=os.environ['KAFKA_BOOTSTRAP'])
    try:
        existing=admin.list_topics()
        for topic in TOPICS:
            if topic not in existing:
                try:
                    admin.create_topics([NewTopic(topic,3,1)])
                except TopicAlreadyExistsError:
                    log('topic_exists','startup',topic=topic)
    finally:
        admin.close()
    with graph() as driver, driver.session() as s:
        s.run('CREATE CONSTRAINT intel_id IF NOT EXISTS FOR (n:IntelRecord) REQUIRE n.id IS UNIQUE').consume()
    from .integrity import backfill
    backfill()
    with db() as conn:
        snapshots=conn.execute('SELECT sha256,captured_at,processed_at FROM intel_snapshots WHERE processed_at IS NOT NULL').fetchall()
    with graph() as driver, driver.session() as session:
        for sha,captured,recorded in snapshots:
            session.run('MATCH (n:IntelRecord {snapshot_sha:$sha}) SET n.valid_from=$captured,n.recorded_at=$recorded,n.classification="U"',sha=sha,captured=captured.isoformat(),recorded=recorded.isoformat()).consume()
            session.run('MATCH (:IntelRecord)-[r:USES {snapshot_sha:$sha}]->(:IntelRecord) SET r.valid_from=$captured,r.recorded_at=$recorded,r.classification="U"',sha=sha,captured=captured.isoformat(),recorded=recorded.isoformat()).consume()

    with db() as conn:
        audit(conn,'graph_temporal_metadata_backfilled',str(len(snapshots)),'startup')


def health_dependencies():
    from demo.common import readiness
    result=readiness()
    result['mode']='public-technical-intelligence'
    return result
