# Backend checklist audit — 2026-09-20

Result: the original checklist is NOT complete. The deployed system is the previously approved synthetic-only demonstration. Missing operational services were deliberately excluded from that scope; existing fixture loaders and seeded graph relationships must not be represented as those services.

Evidence: inspected source inventory, Compose services, live PostgreSQL tables, live Neo4j constraints, live Kafka topics, and reran `python -m demo.cli verify`. Integration suite previously passed eight tests; it was not rerun during this read-only audit because it injects another malformed event.

| Requested item | Status against original specification | Evidence / gap |
|---|---|---|
| Tor Proxy Manager | Missing | No service, Tor process, circuit endpoint, rotation, or metrics. |
| Crawler Scheduler | Missing | No scheduling API, Celery, Redis, priority queue, or domain rate limiter. |
| Onion Crawler | Missing | No live collector, Scrapy worker, SOCKS routing, or honeypot detector. |
| Forum Crawler | Missing | No XenForo/IPB/MyBB/vBulletin parsers; JSON fixtures are loaded directly. |
| Evidence Pipeline | Partial | Worker verifies object hashes and fixture membership, persists evidence, appends audit entries, and publishes clean content. Uses a reduced synthetic schema and canonical post JSON; no Merkle tree/signing. |
| Blockchain Node | Partial | Fixture loader publishes chain.tx; no separate blockchain-node worker or actual node. |
| Misconfig Analyzer | Missing | scan.raw is populated but no analyzer consumes it. |
| Clearnet Correlator | Missing | No SQLite index or matching worker. |
| Stylometry Engine | Missing | No model, embeddings, similarity calculation, or persona.links producer. Seeded StylometricMatch relationships are fixture assertions. |
| Behavioral Profiler | Missing | No posting-window aggregation, timezone estimator, anomalies, or behavior.profile producer. |
| Entity Resolver | Missing | Graph seeding is present, but no Kafka-driven entity-resolution service. |
| Confidence Scorer | Missing | Supplied confidence values are displayed; no weighted scoring or attribution tiers are computed. |
| PostgreSQL schema | Partial | users, evidence, audit_log, processed, outbox exist; wallet_clusters and pir_gaps are absent. |
| Neo4j constraints | Partial | actor_id, handle_id, wallet_addr, onion_addr, clearnet_ip, pgp_fp exist. Contact and VASP constraints are absent; no infra/neo4j/constraints.cypher file. |
| Kafka topics | Partial | Seven application topics exist; eight originally requested topics are absent. audit.events exists but is unused. |
| Shared library | Partial | demo/common.py provides connections, hashing, audit, retries, and outbox. No shared/python/dwtds_common package or complete topic validation models. |
| Scripts | Partial | Demo startup/load/seed/query/dump/verify scripts exist. Several originally requested scripts are absent; dump-graph.sh prints JSON rather than saving the required path. |
| Error prevention | Partial | Evidence deduplication, manual offset commits, hash checks, audit lock, DLQ, health checks, and internal networking exist. All-topic validation, universal retry/error publication/correlation logging, and bounded shutdown under failures are not fully implemented or demonstrated. |
| Tests | Partial | Eight synthetic integration tests exist and previously passed. Requested collection/analytics/extraction/wallet/fusion suites and their full scenarios are absent. |
| Quality gates | Partial | Synthetic runtime/data checks pass. Original full-service and analytics gates cannot pass with absent services; fixture count is 25 rather than the original gate of 20. |
| Anti-patterns | Partial | No latest image tags, TODO/FIXME markers, or interpolated Cypher values found in implementation scan. Secrets are generated. Original schema conformance and universal logging/health requirements are not met across the requested service inventory. This is not a complete security audit. |
| Handoff | Present for demo only | HANDOFF-BACKEND.md, SOURCE-BUNDLE.md, observed-count JSON, and graph snapshot exist. Handoff explicitly documents the narrower scope; it does not describe an implemented 17-service backend. |

## Exact missing Kafka topics

actor.entities, infra.indicators, wallet.attribution, persona.links, behavior.profile, category.signals, dlq.scan.raw, dlq.content.clean.

Existing: crawl.raw, content.clean, scan.raw, chain.tx, audit.events, service.errors, dlq.crawl.raw. Kafka internal topics are excluded from these counts.

## Missing original scripts

init-kafka-topics.sh (topic initialization instead occurs in demo/common.py), wait-for-it.sh, load-analytics-demo.sh, compute-attribution.sh, reset-demo.sh, precache-model.sh, precache-spacy.sh. generate-env.sh uses Python's OS-backed secrets generator rather than openssl. No live collection or model download tooling is included.

## Other original services omitted from this checklist

Autonomous Scheduler, Entity Extractor, Blockchain Clusterer, VASP Attributor, and Category Classifier are also absent. Redis is absent. The seven deployed services are demo API, evidence worker, gateway, PostgreSQL, Kafka, MinIO, and Neo4j; this count is not the number of original backend services implemented.

## Current verified state

- Seven running containers are healthy.
- 25 evidence records; 25 MinIO objects; four demo users.
- 22 graph nodes; 20 seeded relationships.
- Audit hash chain valid; pending outbox zero.
- Kafka: crawl.raw=26, content.clean=25, scan.raw=10, chain.tx=20, audit.events=0, service.errors=1, dlq.crawl.raw=1.
- The additional crawl/error/DLQ records come from the previous malformed-message test.

No application code, data, or deployment was changed by this audit. Only this report was added. Missing operational deanonymization components are not authorized by the previously approved synthetic-only scope, and this audit does not silently expand that scope.
