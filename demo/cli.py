"""Local operator commands; no public mutation API."""
import argparse
from .common import *
from .graph import snapshot, seed_graph
from .loader import load


def counts():
    consumer = KafkaConsumer(bootstrap_servers=os.environ['KAFKA_BOOTSTRAP'],enable_auto_commit=False)
    from kafka.structs import TopicPartition
    try:
        result = {}
        for topic in TOPICS:
            partitions = [TopicPartition(topic,p) for p in consumer.partitions_for_topic(topic)]
            beginning = consumer.beginning_offsets(partitions)
            ending = consumer.end_offsets(partitions)
            result[topic] = sum(ending[p]-beginning[p] for p in partitions)
        return result
    finally:
        consumer.close()

def verify():
    from .app import status
    expected_posts = len(json.loads((DATA/'forum_posts.json').read_text()))
    deadline = time.monotonic()+60
    while True:
        result = status()
        topics = counts()
        if result['evidence_rows'] == expected_posts and result['pending_outbox'] == 0 and topics['content.clean'] >= expected_posts:
            break
        if time.monotonic() > deadline:
            raise RuntimeError({'timeout':result,'topics':topics})
        time.sleep(1)
    assert result['users']==4,result
    assert result['minio_objects']==expected_posts,result
    assert result['audit_log_chain_valid'],result
    assert result['graph_nodes']==22,result
    assert result['graph_edges']==20,result
    assert topics['scan.raw']==10,topics
    assert topics['chain.tx']==20,topics
    result['kafka_messages'] = topics
    result['verified_at'] = now()
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command',choices=['load','seed','verify','audit','dump','counts'])
    args = parser.parse_args()
    result = {'load':load,'seed':seed_graph,'verify':verify,'audit':lambda:{'valid':verify_audit()},'dump':snapshot,'counts':counts}[args.command]()
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if args.command == 'audit' and not result['valid']:
        raise SystemExit(1)
