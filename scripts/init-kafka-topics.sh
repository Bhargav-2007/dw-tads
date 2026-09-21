#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

BOOTSTRAP=${KAFKA_BOOTSTRAP:-localhost:9092}
echo "=== Initializing Kafka Topics on ${BOOTSTRAP} ==="

TOPICS=(
  "scan.raw"
  "crawl.raw"
  "content.clean"
  "content.translated"
  "actor.entities"
  "chain.tx"
  "wallet.attribution"
  "infra.indicators"
  "persona.links"
  "behavior.profile"
  "category.signals"
  "threat.iocs"
  "onion.discovery"
  "malware.family"
  "media.forensics"
  "synthetic.media"
  "merkle.root"
  "cognitive.fingerprint"
  "quarantine.signals"
  "agent.actions"
  "case.events"
  "legal.orders"
  "humint.intel"
  "audit.events"
  "service.errors"
  "dlq.scan.raw"
  "dlq.crawl.raw"
  "dlq.content.clean"
)

# Can use kafka-topics.sh or python admin client
python3 - <<EOF
import os, sys
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

bootstrap = os.getenv("KAFKA_BOOTSTRAP", "${BOOTSTRAP}")
topics = [
  "scan.raw", "crawl.raw", "content.clean", "content.translated",
  "actor.entities", "chain.tx", "wallet.attribution", "infra.indicators",
  "persona.links", "behavior.profile", "category.signals", "threat.iocs",
  "onion.discovery", "malware.family", "media.forensics", "synthetic.media",
  "merkle.root", "cognitive.fingerprint", "quarantine.signals",
  "agent.actions", "case.events", "legal.orders", "humint.intel",
  "audit.events", "service.errors",
  "dlq.scan.raw", "dlq.crawl.raw", "dlq.content.clean"
]

try:
    admin = KafkaAdminClient(bootstrap_servers=bootstrap, request_timeout_ms=5000)
    existing = admin.list_topics()
    to_create = [NewTopic(name=t, num_partitions=3, replication_factor=1) for t in topics if t not in existing]
    if to_create:
        admin.create_topics(to_create)
        print(f"Created {len(to_create)} new topics.")
    else:
        print("All topics already exist.")
    print("Topics registered:", len(admin.list_topics()))
except Exception as e:
    print(f"Warning: Could not connect to Kafka at {bootstrap}: {e}")
    sys.exit(0)
EOF

echo "Topic initialization complete."
