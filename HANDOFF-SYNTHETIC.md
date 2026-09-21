# Synthetic backend handoff

This is the approved offline fixture demonstration, not the original 17-service operational attribution backend. Existing binding documents and fixtures are retained unchanged. Graph assertions are supplied synthetic data, never identity findings or calibrated probabilities.

## Run on Windows

From `C:\Users\BHARGAV\Desktop\DW-TADS`:

```powershell
.\scripts\demo.ps1 start
.\scripts\demo.ps1 load
.\scripts\demo.ps1 verify
.\scripts\demo.ps1 test
```

Open http://localhost:8000 for status, http://localhost:8000/docs for the API, and http://localhost:7474 for Neo4j Browser. Neo4j username is `neo4j`; the generated password is stored locally in `.env` under `NEO4J_PASSWORD`. Credentials are not printed or embedded in the image. `stop` preserves data. No automatic destructive reset is provided.

Build and image download require internet access. After images are cached, the seven-container runtime uses the internal `dwtds-mvp` bridge network. This local Docker Compose deployment does not require Swarm. A fixed-destination gateway is attached to a separate ingress bridge and publishes only the API and Neo4j ports, bound to 127.0.0.1. Backend services remain exclusively on the internal network. The gateway has no credentials, configurable target API, or arbitrary forwarding capability. The read-only demo API has no authentication and must remain localhost-only. Bundled demo users are storage fixtures, not API accounts.

## Services and interfaces

| Service | Internal ports | Host ports | Health |
|---|---|---|---|
| demo API | 8000 | via gateway | `/health`, `/ready` |
| gateway | 8000, 7474, 7687 | localhost:8000, localhost:7474, localhost:7687 | API readiness through proxy |
| evidence worker | 8001 | none | `/health`, `/ready` |
| Postgres | 5432 | none | pg_isready |
| Kafka KRaft | 9092, 9093 | none | broker topic-list probe |
| MinIO | 9000 | none | `/minio/health/ready` |
| Neo4j | 7474, 7687 | via gateway | HTTP probe |

`GET /status` returns evidence_rows, users, minio_objects, graph_nodes, graph_edges, pending_outbox, audit_log_chain_valid, mode. `GET /graph` returns `{synthetic:true,nodes:[{id,type,properties}],edges:[{source,target,type,properties}]}`. There are no live target, upload, crawl, or inference endpoints. Load/seed commands execute inside Docker and read only the bundled fixtures.

Application environment: PGHOST, PGDATABASE, PGUSER, PGPASSWORD; NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD; MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY; KAFKA_BOOTSTRAP. Infrastructure credentials are supplied through Compose and `.env`. `scripts/generate_env.py` uses the OS cryptographic random generator and refuses to overwrite existing credentials.

## Kafka and evidence

Each topic has three partitions and replication factor one. All application messages include `event_id` (deterministic digest), `correlation_id` (UUID), and `synthetic:true`.

| Topic | Additional payload fields | Producer / consumer |
|---|---|---|
| crawl.raw | sha256, minio_bucket, minio_key, captured_at, source_url | fixture loader / evidence worker |
| content.clean | handle_id, platform, posted_at, text, source_sha256, source_url | evidence worker / read-only inspection |
| scan.raw | all fields from onion_scans.json | fixture loader / no analysis |
| chain.tx | all fields from blockchain_txs.json | fixture loader / no attribution |
| dlq.crawl.raw | error, original_topic, partition, offset, original | evidence worker / operator inspection |
| service.errors | same malformed-record fields, or error for worker failure | evidence worker / operator inspection |
| audit.events | reserved; no events published in this demo | none |

Post evidence is SHA-256 over canonical UTF-8 JSON of the complete fixture record (sorted keys, compact separators), not text alone. Duplicate text with distinct author/time remains separate evidence. Objects are `raw-crawl/fixtures/posts/{sha256}.json`. The consumer verifies object bytes and membership in the bundled fixture corpus before ingestion.

Postgres evidence, audit entry, deduplication marker, and output event are committed together. Outbox publishing is at-least-once: a crash between publishing and marking sent can duplicate a Kafka event. Stable event IDs and the evidence consumer's processed table prevent duplicate database effects. Topic counts are exact only for a clean normal demo run; this is not a claim of exactly-once transport. Consumer offsets commit after each fully processed partition batch. A failed worker becomes unready and requires an operator restart after the underlying error is fixed.

Audit inserts use a transaction advisory lock. `this_hash = SHA256(previous_hash UTF-8 bytes + canonical audit payload bytes)`. The payload includes event_type, actor_user, action, resource, query_hash, result_hash, ts, metadata. Verification recomputes every hash, including the genesis link. A database trigger blocks row UPDATE and DELETE; database-owner privileges are not a hardened production trust boundary.

## Graph catalog

Nodes: Actor(actor_id,risk_score,category,source_confidence); Handle(handle_id,platform); Wallet(address,currency); OnionService(onion_address,service_type); ClearnetIP(ip_address,hosting_provider); PGPKey(fingerprint,algorithm). Each has demo_id, synthetic=true, provenance, recorded_at. Identity constraints match the corresponding fixture keys, with composite address/currency for Wallet.

Edges: HasHandle, StylometricMatch, Trusts, ControlsWallet, UsesPGP, ResolvesTo. Each has confidence from the fixture, synthetic=true, provenance. No similarity, geographic, real-world identity, or wallet ownership inference is performed. Cypher queries have fixed labels/types and parameterized fixture values. Graph seeding writes audit intent before its transaction and completion afterward; Postgres and Neo4j are not a distributed atomic transaction. An interrupted seed may leave an intent without completion; replay converges through MERGE.

Explore in Neo4j Browser:

```cypher
MATCH (a)-[r]->(b) RETURN a,r,b LIMIT 100;
MATCH (a:Actor)-[:HasHandle]->(h:Handle) RETURN a.actor_id,collect(h.handle_id);
MATCH (n) RETURN labels(n),count(n);
```

The expected fixture graph is 22 nodes and 20 relationships. Synthetic confidence is displayed as supplied, not converted to HIGH/MEDIUM identity attribution tiers.

## Verification and boundaries

Integration tests cover all 25 evidence records, object hashes, clean-message count, replay idempotency, audit-chain recomputation and immutability, malformed-message quarantine, hash mismatch rejection, synthetic graph provenance, and Argon2 passwords. `tests/data/expected_after_prompt_1.json` records observed results after ingestion. Test injection adds one malformed crawl event and its error/DLQ output; evidence and graph counts are unchanged.

No Tor, live crawlers, autonomous targeting, cross-platform identity inference, stylometry model, VASP inference, or production authentication is included. Marketplace listings are retained as fixtures but not processed. Scan and chain records exercise Kafka ingestion only. Original operational analytics quality gates do not apply to this narrower approved demo. This demo does not establish legal admissibility, production security certification, or probability calibration.

## Postgres schemas

The exact initialization DDL follows. Reference: DEMO-DATA-CONTRACT.md section 3; processed/outbox are reliability additions.

```sql
-- architecture.md: evidence-first storage and append-only audit trail.
CREATE TABLE users (
 user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), username TEXT UNIQUE NOT NULL,
 role TEXT NOT NULL CHECK (role IN ('analyst','senior_analyst','admin','auditor')),
 password_hash TEXT NOT NULL, mfa_secret TEXT NOT NULL,
 created_at TIMESTAMPTZ DEFAULT NOW(), last_login TIMESTAMPTZ
);
CREATE TABLE evidence (
 evidence_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), sha256 CHAR(64) UNIQUE NOT NULL,
 source_url TEXT, source_type TEXT NOT NULL, captured_at TIMESTAMPTZ NOT NULL,
 minio_bucket TEXT NOT NULL, minio_key TEXT NOT NULL, merkle_root CHAR(64), ingested_by TEXT NOT NULL
);
CREATE TABLE audit_log (
 audit_id BIGSERIAL PRIMARY KEY, event_type TEXT NOT NULL, actor_user TEXT NOT NULL,
 action TEXT NOT NULL, resource TEXT, query_hash CHAR(64), result_hash CHAR(64),
 prev_hash CHAR(64), this_hash CHAR(64) NOT NULL, ts TIMESTAMPTZ DEFAULT NOW(),
 metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_audit_ts ON audit_log(ts DESC);
CREATE FUNCTION audit_log_immutable() RETURNS TRIGGER AS $$
BEGIN RAISE EXCEPTION 'audit_log is append-only'; END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER audit_log_no_update BEFORE UPDATE OR DELETE ON audit_log
FOR EACH ROW EXECUTE FUNCTION audit_log_immutable();
CREATE TABLE processed (consumer TEXT, event_id TEXT, PRIMARY KEY (consumer,event_id));
CREATE TABLE outbox (
 id BIGSERIAL PRIMARY KEY, event_id TEXT UNIQUE NOT NULL, topic TEXT NOT NULL,
 payload JSONB NOT NULL, sent BOOLEAN NOT NULL DEFAULT FALSE
);
```

Fixture count reconciliation: the current forum_posts.json contains 25 posts, all retained and ingested. The original expected_outcomes.json specifies 20 and is preserved unchanged. This approved synthetic demo validates the actual bundled fixture count rather than truncating input to match that stale expectation.

## Observed verification

On 2026-09-20, all seven containers were healthy. Eight integration tests passed in 19.51 seconds. After gateway deployment and backend recreation, verification still showed 25 evidence records, 25 MinIO objects, four users, 22 graph nodes, 20 relationships, zero pending outbox records, and a valid full audit chain. All three evidence consumer partitions had lag zero. The localhost landing page, readiness endpoint, graph endpoint, and Neo4j Browser returned HTTP 200.

Before malformed-message testing: crawl.raw=25, content.clean=25, scan.raw=10, chain.tx=20, dlq.crawl.raw=0, service.errors=0. After testing: crawl.raw=26, dlq.crawl.raw=1, service.errors=1; clean content and database counts remain unchanged. The observed JSON report reflects this post-test state. Future test runs add further malformed records by design.

`tests/data/graph-snapshot.json` contains the actual exported graph. `SOURCE-BUNDLE.md` includes complete generated source files and their document references, excluding local credentials, unchanged input fixtures, and binary/runtime artifacts.
