# DEMO-DATA-CONTRACT.md
## Binding data interface for DW-TADS MVP (48-hour build)

This document is referenced by all four build prompts. Every service
MUST conform to the schemas, filenames, and values below. Any deviation
will break downstream prompts.

---

## SECTION 1 — FILES THAT MUST EXIST BEFORE PROMPT 1 STARTS

Create these before executing Prompt 1. Do not skip any.

### 1.1 tests/data/seed_targets.txt

```
darkforum1234567.onion
marketxyz9876543.onion
exploit.in
breachforums.st
xss.is
ramp4ru.onion
lockbitapt.onion
alphvblog.onion
```

### 1.2 tests/data/forum_posts.json

```json
[
  {
    "handle_id": "actor_alpha",
    "platform": "BreachForums",
    "posted_at": "2025-04-10T09:12:00Z",
    "text": "Fresh CVE-2025-12345 exploit available. DM for price."
  },
  {
    "handle_id": "actor_alpha",
    "platform": "BreachForums",
    "posted_at": "2025-04-10T14:33:00Z",
    "text": "Bulk database of 2M Indian users. Sample on request."
  }
]
```

Rule: `actor_alpha` and `actor_beta` MUST use the same vocabulary,
punctuation style, and sentence length. This is required for the
stylometry engine to link them. Expand to 20 total posts from actor_alpha
in English (and matching posts for actor_beta) before Prompt 1 starts.

### 1.3 tests/data/marketplace_listings.json

```json
[
  {
    "seller_handle": "actor_alpha",
    "listing_id": "LST-001",
    "title": "Indian user database 2M records",
    "wallet_address": "1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q",
    "currency": "BTC",
    "posted_at": "2025-04-11T10:00:00Z"
  }
]
```

Expand to 5 listings sharing the same wallet before Prompt 1 starts.

### 1.4 tests/data/onion_scans.json

```json
[
  {
    "onion_address": "darkforum1234567.onion",
    "path": "/server-status",
    "http_status": 200,
    "body": "<!DOCTYPE html>...Apache Server Status...</html>",
    "headers": {"Server": "Apache/2.4.41 (Ubuntu)"},
    "favicon_sha256": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
    "ssl_serial": "0x1A2B3C4D",
    "etag": "\"5f8a-9c4\""
  }
]
```

Expand to 10 scans total: 3 with mod_status exposed, 2 with matching
favicon/SSL/ETag, 5 normal.

### 1.5 tests/data/blockchain_txs.json

```json
[
  {
    "tx_hash": "0xabc123def4567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "currency": "BTC",
    "from_address": "1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q",
    "to_address": "9I0J1K2L3M4N5O6P7Q8R9S0T1U2V3W4X5",
    "amount": 0.5,
    "timestamp": "2025-04-12T08:00:00Z"
  }
]
```

Expand to 20 txs forming 3 wallet clusters, with 3 txs to a Binance
deposit address `3BinanceDepositAddressXXX`.

### 1.6 tests/data/seed_graph.json

```json
{
  "actors": [
    {"actor_id": "actor:shadow_broker", "risk_score": 0.92, "category": ["stolen_data", "ransomware", "zero_day"]},
    {"actor_id": "actor:carder_king", "risk_score": 0.78, "category": ["carding"]},
    {"actor_id": "actor:broker_v2", "risk_score": 0.75, "category": ["stolen_data"]},
    {"actor_id": "actor:alpha_actor", "risk_score": 0.65, "category": ["hacking_services"]},
    {"actor_id": "actor:gamma_actor", "risk_score": 0.60, "category": ["drugs"]}
  ],
  "handles": [
    {"handle_id": "shadow_broker", "platform": "BreachForums"},
    {"handle_id": "zer0day_hunter", "platform": "Exploit.in"},
    {"handle_id": "cve_dealer_x", "platform": "XSS.is"},
    {"handle_id": "carder_king", "platform": "BreachForums"},
    {"handle_id": "cc_master", "platform": "BreachForums"},
    {"handle_id": "broker_v2", "platform": "BreachForums"},
    {"handle_id": "actor_alpha", "platform": "BreachForums"},
    {"handle_id": "actor_beta", "platform": "RAMP"},
    {"handle_id": "gamma_actor", "platform": "BreachForums"}
  ],
  "wallets": [
    {"address": "1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q", "currency": "BTC"},
    {"address": "4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U", "currency": "XMR"},
    {"address": "9I0J1K2L3M4N5O6P7Q8R9S0T1U2V3W4X5", "currency": "BTC"}
  ],
  "onion_services": [
    {"onion_address": "shadowmarket1234.onion", "service_type": "marketplace"},
    {"onion_address": "privatedump5678.onion", "service_type": "leak_site"}
  ],
  "clearnet_ips": [
    {"ip_address": "203.0.113.45", "hosting_provider": "ExampleHost"},
    {"ip_address": "198.51.100.22", "hosting_provider": "ExampleHost"}
  ],
  "edges": [
    {"from": "actor:shadow_broker", "to": "shadow_broker", "type": "HasHandle", "confidence": 0.95},
    {"from": "actor:shadow_broker", "to": "zer0day_hunter", "type": "HasHandle", "confidence": 0.94},
    {"from": "shadow_broker", "to": "zer0day_hunter", "type": "StylometricMatch", "confidence": 0.94}
  ]
}
```

Expand to 20 total edges with realistic confidence values before Prompt 3.

### 1.7 tests/data/demo_users.json

```json
{
  "users": [
    {
      "username": "analyst1",
      "password": "demo_password",
      "mfa_secret": "JBSWY3DPEHPK3PXP",
      "role": "analyst"
    },
    {
      "username": "senior1",
      "password": "demo_password",
      "mfa_secret": "KRSXGZDFNQQGK3DF",
      "role": "senior_analyst"
    },
    {
      "username": "admin1",
      "password": "demo_password",
      "mfa_secret": "MFRGGZDFMZTWQ2LK",
      "role": "admin"
    },
    {
      "username": "judge1",
      "password": "demo_password",
      "mfa_secret": "GEZDGNBVGY3TQOJQ",
      "role": "auditor"
    }
  ],
  "note": "These MFA secrets are RFC 6238 test vectors. Use pyotp.TOTP(secret).now() to generate valid codes during demo."
}
```

### 1.8 tests/data/expected_outcomes.json

```json
{
  "after_prompt_1": {
    "evidence_rows": 20,
    "minio_objects": 20,
    "kafka_content_clean_messages": 20,
    "audit_log_chain_valid": true
  },
  "after_prompt_2": {
    "infra_indicators_messages": 5,
    "persona_links_messages": 1,
    "behavior_profile_messages": 2,
    "required_link": {
      "handle_a": "actor_alpha",
      "handle_b": "actor_beta",
      "min_similarity": 0.85
    }
  },
  "after_prompt_3": {
    "neo4j_actor_nodes": 5,
    "neo4j_handle_nodes": 9,
    "neo4j_wallet_nodes": 3,
    "neo4j_onion_service_nodes": 2,
    "attributed_edges_with_confidence_gt_0_85": 2
  },
  "after_prompt_4": {
    "analyst_login_works": true,
    "timeline_query_returns": 5,
    "actor_profile_returns_handles": true,
    "graph_query_returns_nodes": true,
    "csv_export_works": true,
    "json_export_works": true,
    "pdf_export_works": true,
    "audit_log_has_query_records": true
  }
}
```

---

## SECTION 2 — KAFKA TOPIC CONTRACT

Every service MUST use these exact topic names and message schemas.

| Topic | Producer | Consumer(s) | Message Schema (JSON) |
|-------|----------|-------------|----------------------|
| scan.raw | external (synthetic) | misconfig-analyzer, clearnet-correlator | {onion_address, path, http_status, body, headers, favicon_sha256, ssl_serial, etag, captured_at} |
| crawl.raw | onion-crawler, forum-crawler | evidence-pipeline | {target, path, sha256, minio_bucket, minio_key, http_status, headers, content_length, elapsed_ms, captured_at} |
| content.clean | evidence-pipeline | stylometry-engine, behavioral-profiler | {handle_id, platform, text, posted_at, source_sha256} |
| actor.entities | entity-extractor | entity-resolver | {handle_id, entities: [{type, value}], source_sha256} |
| chain.tx | blockchain-node | blockchain-clusterer, vasp-attributor | {tx_hash, currency, from_address, to_address, amount, timestamp} |
| infra.indicators | misconfig-analyzer, clearnet-correlator | entity-resolver, confidence-scorer | {onion_address, finding_type, matched_clearnet_ip, confidence, detected_at} |
| wallet.attribution | blockchain-clusterer, vasp-attributor | entity-resolver, confidence-scorer | {wallet_address, cluster_id, vasp_name, confidence} |
| persona.links | stylometry-engine | entity-resolver, confidence-scorer | {handle_a, handle_b, similarity_score, confidence, signals} |
| behavior.profile | behavioral-profiler | entity-resolver, confidence-scorer | {handle_id, estimated_timezone_offset, posting_pattern, anomaly_score, confidence} |
| audit.events | all services | audit-ledger | {event_type, actor_user, action, resource, query_hash, result_hash} |

---

## SECTION 3 — POSTGRES SCHEMA CONTRACT

Tables required by every prompt. All prompts must use these exact names.

```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('analyst','senior_analyst','admin','auditor')),
  password_hash TEXT NOT NULL,
  mfa_secret TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_login TIMESTAMPTZ
);

CREATE TABLE evidence (
  evidence_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sha256 CHAR(64) UNIQUE NOT NULL,
  source_url TEXT,
  source_type TEXT NOT NULL,
  captured_at TIMESTAMPTZ NOT NULL,
  minio_bucket TEXT NOT NULL,
  minio_key TEXT NOT NULL,
  merkle_root CHAR(64),
  ingested_by TEXT NOT NULL
);

CREATE TABLE audit_log (
  audit_id BIGSERIAL PRIMARY KEY,
  event_type TEXT NOT NULL,
  actor_user TEXT NOT NULL,
  action TEXT NOT NULL,
  resource TEXT,
  query_hash CHAR(64),
  result_hash CHAR(64),
  prev_hash CHAR(64),
  this_hash CHAR(64) NOT NULL,
  ts TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE OR REPLACE FUNCTION audit_log_immutable() RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'audit_log is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_log_no_update
  BEFORE UPDATE OR DELETE ON audit_log
  FOR EACH ROW EXECUTE FUNCTION audit_log_immutable();
```

---

## SECTION 4 — NEO4J SCHEMA CONTRACT

Constraints and node/edge types. All prompts must use these exact names.

```cypher
CREATE CONSTRAINT actor_id IF NOT EXISTS
  FOR (a:Actor) REQUIRE a.actor_id IS UNIQUE;

CREATE CONSTRAINT handle_id IF NOT EXISTS
  FOR (h:Handle) REQUIRE h.handle_id IS UNIQUE;

CREATE CONSTRAINT handle_unique IF NOT EXISTS
  FOR (h:Handle) REQUIRE (h.handle_id, h.platform) IS UNIQUE;

CREATE CONSTRAINT wallet_addr IF NOT EXISTS
  FOR (w:Wallet) REQUIRE (w.address, w.currency) IS UNIQUE;

CREATE CONSTRAINT onion_addr IF NOT EXISTS
  FOR (o:OnionService) REQUIRE o.onion_address IS UNIQUE;

CREATE CONSTRAINT clearnet_ip IF NOT EXISTS
  FOR (c:ClearnetIP) REQUIRE c.ip_address IS UNIQUE;
```

**Node types:** Actor, Handle, PGPKey, Wallet, OnionService, ClearnetIP, SSLCert

**Edge types:** HasHandle, UsesPGP, ControlsWallet, ClustersWith, ResolvesTo, SharesCert, StylometricMatch, AttributedTo, Trusts

---

## SECTION 5 — SERVICE PORT AND HEALTH CONTRACT

Every service MUST expose these ports and health endpoints.

| Service | Port | Health endpoint |
|---------|------|-----------------|
| tor-proxy-manager | 8000 | GET /health |
| crawler-scheduler | 8001 | GET /health |
| onion-crawler | N/A (worker) | log-based |
| forum-crawler | N/A (worker) | log-based |
| evidence-pipeline | N/A (worker) | log-based |
| misconfig-analyzer | N/A (worker) | log-based |
| clearnet-correlator | N/A (worker) | log-based |
| stylometry-engine | 8002 | GET /health |
| behavioral-profiler | N/A (worker) | log-based |
| entity-resolver | N/A (worker) | log-based |
| confidence-scorer | N/A (worker) | log-based |
| analyst-api | 8010 | GET /health |
| analyst-dashboard | 3000 | GET / |
| report-generator | 8011 | GET /health |

---

## SECTION 6 — ERROR PREVENTION RULES

Every prompt MUST enforce these. Violation causes the demo to fail.

1. **Idempotency.** Every Kafka consumer MUST be idempotent. Processing the same message twice MUST NOT create duplicate DB rows or graph nodes. Use Kafka consumer group offsets committed AFTER processing.

2. **Retry with backoff.** Every Kafka producer and consumer MUST retry on transient failure (network, broker restart) with exponential backoff.

3. **Schema validation.** Every Kafka consumer MUST validate incoming messages against the schema in Section 2. Invalid messages go to a dead-letter queue topic `dlq.<original_topic>`.

4. **Startup ordering.** Services MUST wait for their dependencies using `wait-for-it.sh` before starting. Kafka, Postgres, Neo4j, and MinIO must all be healthy before any service connects.

5. **No hardcoded values.** Every connection string, credential, and configuration MUST come from environment variables loaded from `.env`. No exceptions.

6. **Deterministic seeds.** All synthetic data generators MUST use a fixed random seed (42) so results are reproducible.

7. **Hash chain continuity.** Every audit_log entry MUST reference the prev_hash of the last entry. A broken chain invalidates all downstream exports for court admissibility.

8. **Time consistency.** All services MUST use UTC. Every timestamp MUST end with `Z` or `+00:00`.

9. **UTF-8 only.** All text data MUST be UTF-8. Cyrillic, Arabic, and Hindi text MUST be preserved, not corrupted.

10. **Failure visibility.** Every service MUST log errors to stdout AND write to Kafka topic `service.errors`. Silent failures are prohibited.

---

## SECTION 7 — CONFIDENCE SCORING FORMULA (Prompt 3)

```
confidence = sigmoid(
  log(prior / (1 - prior))
  + 0.30 * stylometric_log_odds
  + 0.10 * behavioral_log_odds
  + 0.25 * infra_log_odds
  + 0.20 * wallet_log_odds
  + 0.10 * pgp_log_odds
  + 0.05 * trust_log_odds
)
where prior = 0.05
```

---

## SECTION 8 — API RESPONSE SHAPES (Prompt 4)

### POST /auth/token

Request:
```json
{"username": "analyst1", "password": "demo_password", "totp": "123456"}
```

Response:
```json
{"access_token": "<JWT>", "token_type": "bearer", "expires_in": 28800}
```

### GET /query/timeline?start=2025-04-01&end=2025-04-30&min_confidence=0.5

```json
{
  "results": [
    {
      "actor_id": "actor:shadow_broker",
      "risk_score": 0.92,
      "category": ["stolen_data", "ransomware"],
      "handles": ["shadow_broker", "zer0day_hunter", "cve_dealer_x"],
      "wallets": ["1A2B3C4D..."],
      "confidence": 0.91,
      "tier": "HIGH",
      "last_seen": "2025-04-18T14:23:00Z",
      "source": "6 distinct sources"
    }
  ],
  "result_hash": "<SHA256>",
  "query_id": "<UUID>"
}
```

### GET /query/actor/{actor_id}

```json
{
  "actor": {},
  "handles": [],
  "pgp_keys": [],
  "wallets": [],
  "onion_services": [],
  "clearnet_ips": [],
  "stylometric_matches": [{"handle": "...", "confidence": 0.94}],
  "behavioral_profile": {},
  "attribution_confidence": {
    "value": 0.91,
    "tier": "HIGH",
    "contributions": {}
  },
  "evidence_chain": [
    {"sha256": "...", "source_url": "...", "captured_at": "..."}
  ],
  "result_hash": "<SHA256>"
}
```

### GET /query/graph?actor_id={id}&depth=2

```json
{
  "nodes": [
    {"id": "...", "type": "Actor", "label": "...", "risk_score": 0.92}
  ],
  "edges": [
    {"from": "...", "to": "...", "type": "HasHandle", "confidence": 0.95}
  ],
  "result_hash": "<SHA256>"
}
```

### POST /export

Request:
```json
{"query_id": "<UUID>", "format": "pdf|csv|json"}
```

Response: binary file download with header  
`Content-Disposition: attachment; filename="export-<UUID>.<ext>"`

---

## SECTION 9 — RBAC MATRIX (Prompt 4)

| Role | query | export | approve | user management | oversight |
|------|-------|--------|---------|-----------------|-----------|
| analyst | Yes | Yes | No | No | No |
| senior_analyst | Yes | Yes | Yes | No | No |
| admin | Yes | Yes | Yes | Yes | Yes |
| auditor | Read-only | No | No | No | Yes |

JWT expires after 8 hours.

---

## SECTION 10 — COMMON ERRORS AND PROACTIVE FIXES

| Error | Cause | Fix |
|-------|-------|-----|
| Kafka broker not available | Topic not created yet | Run scripts/init-kafka-topics.sh first |
| Postgres connection refused | Service started before Postgres ready | Add wait-for-it.sh postgres:5432 to entrypoint |
| Neo4j constraint already exists | Reapplied schema | Use IF NOT EXISTS in every CREATE CONSTRAINT |
| MinIO bucket does not exist | Fresh volume | Create bucket on startup with mc mb |
| ModuleNotFoundError: aiokafka | Missing requirements | Pin versions in requirements.txt and rebuild |
| Stylometry model not found | Model not cached | Pre-download to models/stylometry/ BEFORE air-gap |
| JWT invalid signature | Secret rotated | Load JWT secret from Vault or .env consistently |
| Audit log hash chain broken | Concurrent writers | Use Postgres advisory lock during audit insert |
| TOTP code rejected | Clock skew | Sync system clock: ntpdate pool.ntp.org |
| Cytoscape.js blank graph | Empty result set | Verify Neo4j has nodes: MATCH (n) RETURN count(n) |
| PDF export empty | ReportLab missing fonts | Install reportlab[full] not bare reportlab |
| CORS error in browser | Missing CORS headers | Add CORSMiddleware to FastAPI with allow_origins=["*"] |
| Duplicate nodes on replay | Non-idempotent consumer | Use MERGE not CREATE; commit offset AFTER processing |
| Hash mismatch on evidence | MinIO corruption | Re-hash on read; verify SHA-256 matches DB record |
| Docker compose network error | Stale network | docker compose down --remove-orphans && docker network prune |

---

**Document Version:** 1.0  
**Binding Reference:** architecture.md 
**Classification:** National Security Grade  
**Distribution:** Restricted — NTRO / Authorized Personnel Only  
