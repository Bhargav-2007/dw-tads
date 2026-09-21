# DW-TADS — Implementation Checklist

**Binding Contract:** `architecture.md` v2.0
**Legend:** [ ] not started · [~] in progress · [x] complete · [!] blocked

---

## Plane 1 — Infrastructure & Security (12 services)

### Tor Proxy Manager
- [ ] Circuit rotation every CIRCUIT_ROTATION_SECONDS
- [ ] SOCKS5h endpoint
- [ ] No circuit reuse across targets
- [ ] /health, /ready, /metrics

### Crawler Scheduler
- [ ] Task prioritization and scheduling
- [ ] Domain gap and pacing enforcement
- [ ] Kafka publisher to crawl.raw
- [ ] /health, /ready, /metrics

### Evidence Pipeline
- [ ] SHA-256 hashing, signing, Merkle anchoring
- [ ] Postgres evidence table with UNIQUE(sha256)
- [ ] MinIO immutable evidence upload
- [ ] /health, /ready, /metrics

### Blockchain Node
- [ ] Node ingestion adapter (BTC, ETH, XMR)
- [ ] Block parser to Kafka chain.tx
- [ ] /health, /ready, /metrics

### Internal CA
- [ ] Vault + CFSSL deployment
- [ ] Root CA and mTLS service certs
- [ ] 90-day cert TTL, 60-day rotation
- [ ] /health, /ready, /metrics

### Secrets Manager
- [ ] Vault HSM-sealed secrets and key storage
- [ ] Key shares and access policy
- [ ] Transit engine for signing
- [ ] /health, /ready, /metrics

### Audit Ledger
- [ ] Postgres audit_log append-only table
- [ ] Merkle tree anchoring and prev_hash chaining
- [ ] Immutability trigger enforcement
- [ ] /health, /ready, /metrics

### Data Diode
- [ ] Hardware one-way ingest isolation
- [ ] Quarantine signal handling
- [ ] /health, /ready, /metrics

### Calico Policy Manager
- [ ] 7 Calico network policies (one per plane)
- [ ] Micro-segmentation enforcement
- [ ] /health, /ready, /metrics

### Chaos Engineering
- [ ] Internal fault injection framework
- [ ] Recovery time measurement and resilience
- [ ] /health, /ready, /metrics

### Cost Governance
- [ ] Per-case cost and resource attribution
- [ ] Storage growth and query tracking
- [ ] /health, /ready, /metrics

### SBOM Signer
- [ ] SBOM per container image
- [ ] Image signature and integrity verification
- [ ] /health, /ready, /metrics

---

## Plane 2 — Collection & Ingestion (14 services)

### Onion Crawler
- [ ] Scrapy stealth crawler for hidden services
- [ ] Evidence hashing and MinIO storage
- [ ] Kafka publish to crawl.raw
- [ ] /health, /ready, /metrics

### Forum Crawler
- [ ] XenForo, IPB, MyBB, vBulletin parsers
- [ ] Post extraction and raw crawl packaging
- [ ] /health, /ready, /metrics

### Marketplace Crawler
- [ ] Marketplace listing extractor
- [ ] Seller and wallet attribution extraction
- [ ] /health, /ready, /metrics

### Onion Discovery
- [ ] Hidden service discovery and cataloging
- [ ] Publish to onion.discovery
- [ ] /health, /ready, /metrics

### Ahmia Crawler
- [ ] Ahmia search index scraping and monitoring
- [ ] Dark web market and forum discovery
- [ ] /health, /ready, /metrics

### OnionScan Runner
- [ ] OnionScan vulnerability and leak runner
- [ ] Apache mod_status and SSL cert correlation
- [ ] /health, /ready, /metrics

### Forum Loader
- [ ] Ingest forum dumps and breach archives
- [ ] Entity extraction and post normalization
- [ ] /health, /ready, /metrics

### Threat Feed Loader
- [ ] ThreatFox, URLhaus, Feodo Tracker loader
- [ ] IOC normalization to threat.iocs
- [ ] /health, /ready, /metrics

### Blockchain Loader
- [ ] Historical blockchain transaction loader
- [ ] Ingestion to chain.tx
- [ ] /health, /ready, /metrics

### I2P Collector
- [ ] I2P network and eepsite collector
- [ ] Ingestion to crawl.raw
- [ ] /health, /ready, /metrics

### ZeroNet Collector
- [ ] ZeroNet / ZeroNetX decentralized collector
- [ ] Ingestion to crawl.raw
- [ ] /health, /ready, /metrics

### Telegram OSINT
- [ ] Telegram public channel/group OSINT collector
- [ ] Media capture and message parsing
- [ ] /health, /ready, /metrics

### Clearnet Enrichment Gateway
- [ ] Clearnet OSINT and enrichment mirror gateway
- [ ] Correlation with dark web indicators
- [ ] /health, /ready, /metrics

### Raw Storage
- [ ] Ingested raw artifact storage in MinIO
- [ ] Audit event generation
- [ ] /health, /ready, /metrics

---

## Plane 3 — Analytics & AI (18 services)

### Misconfig Analyzer
- [ ] mod_status / stub_status detection
- [ ] Default banner detection
- [ ] SSL reuse detection
- [ ] Descriptor inconsistency checks
- [ ] Publish to infra.indicators

### Clearnet Correlator
- [ ] Favicon hash matching
- [ ] SSL cert serial matching
- [ ] ETag matching
- [ ] Google Analytics ID matching
- [ ] Publish to infra.indicators

### Blockchain Clusterer
- [ ] Common-input-ownership
- [ ] Change-address detection
- [ ] CoinJoin detection
- [ ] Mixer tracing

### Privacy Coin Analyzer (NEW — CRITICAL)
- [ ] Monero: view-key tracing
- [ ] Monero: ring signature analysis
- [ ] Monero: decoy elimination
- [ ] Zcash: shielded pool analytics
- [ ] Zcash: t-address ↔ z-address correlation
- [ ] Dash: PrivateSend mixing analysis
- [ ] Atomic swap detection (BTC ↔ XMR)
- [ ] Exchange deposit heuristics for privacy coins

### VASP Attributor
- [ ] Local VASP database
- [ ] Cross-chain tracing
- [ ] KYC-traceable endpoint flagging

### Multilingual NLP (NEW — CRITICAL)
- [ ] NLLB-200 offline translation
- [ ] M2M-100 fallback
- [ ] fastText language detection
- [ ] CLD3 language detection
- [ ] Code-switching detection
- [ ] Cyrillic → Latin transliteration
- [ ] Arabic → Latin transliteration
- [ ] Transliteration-aware entity extraction

### Stylometry Engine
- [ ] XLM-RoBERTa + SBERT
- [ ] Character n-grams (2–5)
- [ ] Word n-grams (1–3)
- [ ] Punctuation signatures
- [ ] Syntactic constructions
- [ ] Translation quirk detection
- [ ] Cross-lingual stylometry
- [ ] Weighted ensemble (0.60 + 0.25 + 0.15)
- [ ] Model card published

### Behavioral Profiler
- [ ] Time-of-day analysis
- [ ] Time-zone estimation
- [ ] Posting frequency anomaly
- [ ] Account takeover detection

### Cognitive Fingerprint Analyzer
- [ ] Content-blind attribution
- [ ] Interaction-style behavioral analysis
- [ ] Operates under LLM obfuscation

### Adversarial ML Defense
- [ ] LLM-generated text detection
- [ ] GAN-text detection
- [ ] Stylometric evasion heuristics
- [ ] Quarantine action

### Malware Sandbox (NEW — CRITICAL)
- [ ] QEMU/KVM isolated detonation
- [ ] No network from sandbox
- [ ] PE header analysis
- [ ] Import table analysis
- [ ] String extraction
- [ ] Packing detection
- [ ] API call tracing
- [ ] Registry change capture
- [ ] Network IOC extraction
- [ ] SSDEEP / TLSH fuzzy hashing
- [ ] imphash computation
- [ ] YARA rule generation
- [ ] C2 infrastructure extraction

### Image Forensics (NEW)
- [ ] EXIF extraction
- [ ] GPS coordinate parsing
- [ ] PRNU camera fingerprinting
- [ ] Reverse image search (local mirror)
- [ ] Landmark/geolocation inference
- [ ] Chronolocation (shadows, weather)
- [ ] CSAM detection + mandatory reporting workflow

### Deepfake Detector (NEW)
- [ ] Image deepfake detection
- [ ] Video deepfake detection
- [ ] Voice clone detection
- [ ] AI-text detection
- [ ] Synthetic media metadata analysis

### Evidence Anchor
- [ ] Merkle tree construction
- [ ] Append-only anchoring
- [ ] Merkle proof generation

### YARA Generator
- [ ] Auto-generate rules from sandbox samples
- [ ] Rule versioning
- [ ] Rule validation

### Language Detector
- [ ] fastText integration
- [ ] CLD3 integration
- [ ] Confidence scoring

### Transliteration Normalizer
- [ ] Cyrillic → Latin
- [ ] Arabic → Latin
- [ ] Handle deduplication across scripts

---

## Plane 4 — Intelligence Fusion (10 services)

### Unified Graph
- [ ] Neo4j 5 Enterprise
- [ ] All 17 node types with constraints
- [ ] All 20 edge types
- [ ] Temporal properties (valid_from, valid_until, recorded_at)
- [ ] Causal clustering for failover

### Entity Resolver
- [ ] Louvain community detection
- [ ] PageRank actor ranking
- [ ] merge_personas()
- [ ] link_wallet_to_actor()
- [ ] link_onion_to_clearnet()
- [ ] Multi-script handle unification

### Confidence Scorer
- [ ] Bayesian log-odds fusion
- [ ] Calibrated weights
- [ ] Tier classification (HIGH/MEDIUM/LOW/INSUFFICIENT)

### GNN De-Anonymization
- [ ] GraphSAGE encoder (128→256→256→128)
- [ ] Link prediction decoder
- [ ] Training loop (200 epochs)
- [ ] GPU inference
- [ ] Model card published

### Autonomous AI Agent
- [ ] Llama-3-13B-Instruct Q5 GGUF
- [ ] Tool registry
- [ ] Agent loop (max 20 iterations)
- [ ] Strict JSON schema
- [ ] Evidence citation required
- [ ] All actions logged

### ZKP Query Layer
- [ ] Commitment scheme H(query || salt)
- [ ] BLS-based binding proof
- [ ] execute_and_prove()
- [ ] Audit log entry per query
- [ ] ADR-006 for zk-STARK upgrade

### Temporal Reasoner (NEW)
- [ ] Time-travel queries
- [ ] Actor lifecycle tracking
- [ ] Behavior change detection
- [ ] Historical attribution re-evaluation

### Source Reliability (NEW)
- [ ] Admiralty Code implementation (A–F source, 1–6 info)
- [ ] Automated source scoring from historical accuracy
- [ ] Confidence weighting in graph edges
- [ ] False information detection

### Model Drift Monitor (NEW)
- [ ] Accuracy tracking per model
- [ ] Bias monitoring
- [ ] Retraining triggers
- [ ] Shadow mode deployment
- [ ] A/B testing framework

### Explainability Engine (NEW)
- [ ] SHAP/LIME for ML models
- [ ] Graph path explanation
- [ ] Counterfactual analysis
- [ ] Explanation export for court

---

## Plane 5 — Legal & Compliance (9 services)

### Legal Admissibility (NEW — CRITICAL)
- [ ] Section 65B certificate generator
- [ ] Signed by designated NTRO officer
- [ ] Hash chain attached to certificate
- [ ] Court-format certificate template
- [ ] Witness statement template
- [ ] Sealed exhibit packaging

### Legal Intercept (NEW — CRITICAL)
- [ ] Order tracking (issuance → execution → return)
- [ ] Subscriber data request workflow (ISP, telco, exchange)
- [ ] Section 69 IT Act decryption order workflow
- [ ] Section 69A blocking order coordination
- [ ] Interception warrant workflow (MHA approval chain)
- [ ] Expiration enforcement
- [ ] Independent oversight logging

### Judicial Oversight
- [ ] Read-only judge access
- [ ] Parliamentary committee access
- [ ] Audit log for oversight actions (separate from system audit)
- [ ] Civil liberties impact assessment
- [ ] Redress mechanism

### Data Retention (NEW)
- [ ] DPDPA automated aging
- [ ] Retention schedule per data category
- [ ] Deletion approval workflow
- [ ] Deletion audit trail
- [ ] Legal hold override
- [ ] Right-to-erasure workflow

### Classification Handler
- [ ] Auto-marking of every output
- [ ] Downgrade workflow
- [ ] Declassification schedule
- [ ] Dissemination controls
- [ ] Handling caveats

### Court Exhibit Packager
- [ ] Sealed, tamper-evident exhibit
- [ ] Section 65B certificate attached
- [ ] Chain of custody form
- [ ] Hash manifest
- [ ] Witness statement

### DPIA Engine
- [ ] Data Protection Impact Assessment
- [ ] Data flow diagrams
- [ ] Purpose limitation statement
- [ ] Breach notification procedure

### Oversight Audit Log
- [ ] Separate from system audit
- [ ] Judicial access log
- [ ] Investigation summary log
- [ ] Legal basis tracking

### MLAT Coordinator
- [ ] Mutual Legal Assistance Treaty workflow
- [ ] Cross-border evidence request
- [ ] Budapest Convention compliance

---

## Plane 6 — Case & Operations (8 services)

### Case Manager
- [ ] Case creation, assignment, escalation
- [ ] Analyst task board
- [ ] Case timeline
- [ ] Case linking
- [ ] Case notes with cryptographic timestamps
- [ ] Case closure workflow
- [ ] Deconfliction across agencies

### PIR Tracker
- [ ] Priority Intelligence Requirements
- [ ] Essential Elements of Information (EEI)
- [ ] Collection tasking based on gaps
- [ ] Feedback loop

### Peer Review (NEW)
- [ ] Mandatory review of HIGH-confidence attributions
- [ ] Devil's advocate assignment
- [ ] Alternative hypothesis tracking
- [ ] Analyst disagreement logging
- [ ] Blind re-analysis workflow
- [ ] Analyst calibration scoring

### Bias Mitigation
- [ ] Confirmation bias detection
- [ ] Anchoring detection
- [ ] Groupthink prevention
- [ ] Blind re-analysis triggers

### Analyst Wellness (NEW — CRITICAL)
- [ ] Content warning tags on evidence
- [ ] Mandatory rotation schedules (max 6 months violent content)
- [ ] Break enforcement
- [ ] Confidential counseling integration (external, sealed)
- [ ] Wellness check workflow
- [ ] Cumulative trauma load tracking
- [ ] Post-incident support

### Insider Threat (NEW — CRITICAL)
- [ ] Behavioral analytics on analyst activity
- [ ] Data exfiltration detection
- [ ] Honeytokens in graph (fake actors, wallets)
- [ ] Separation of duties enforcement
- [ ] Mandatory leave policy
- [ ] Peer review of sensitive access
- [ ] Two-person rule for high-risk exports
- [ ] Access anomaly alerts

### HUMINT Manager (NEW — CRITICAL)
- [ ] Undercover persona lifecycle
- [ ] Separate infrastructure (independent Tor circuits)
- [ ] Communication OPSEC
- [ ] Sting operation workflow (analyst → senior → legal → ops)
- [ ] Controlled purchase tracking
- [ ] Burn protocol
- [ ] Integration with legal intercept
- [ ] Strict separation from OSINT data

### Takedown Coordinator
- [ ] Law enforcement coordination
- [ ] Prosecution support package
- [ ] International takedown coordination
- [ ] Seizure warrant support
- [ ] Post-takedown intelligence exploitation
- [ ] Media/public disclosure coordination

---

## Plane 7 — Presentation & Dissemination (7 services)

### Analyst API
- [ ] FastAPI + OAuth2 + JWT
- [ ] Argon2 password hashing
- [ ] TOTP MFA
- [ ] 6 RBAC roles
- [ ] Audit logging on every request
- [ ] Endpoints: /auth/token, /query/timeline, /query/actor,
  /query/stylometric, /query/wallet-trace, /query/malware,
  /query/temporal, /case/{id}, /export

### Analyst Dashboard
- [ ] React + TypeScript + Tailwind
- [ ] Tabs: Timeline · Graph · Actor · Case · Admin
- [ ] Cytoscape.js graph visualization
- [ ] Confidence threshold filter
- [ ] Category filter
- [ ] Temporal slider (time-travel)

### Graph Visualization
- [ ] Force-directed layout
- [ ] Node color by type
- [ ] Edge thickness by confidence
- [ ] Click-to-expand
- [ ] Path finding
- [ ] Temporal playback

### Report Generator
- [ ] PDF via ReportLab
- [ ] CSV, JSON, GraphML export
- [ ] Audit-logged exports
- [ ] Section 65B certificate attachment

### Admin Console
- [ ] User management
- [ ] Role assignment
- [ ] MFA rotation
- [ ] Audit log viewer (read-only)
- [ ] IP whitelisting

### Inter-Agency Gateway (NEW)
- [ ] Secure API for IB, RAW, CBI, NIA, state police
- [ ] Classification handling
- [ ] Need-to-know compartmentalization
- [ ] Redaction engine
- [ ] Foreign liaison channel
- [ ] MLAT coordination

### Field Alerting (NEW)
- [ ] Encrypted push to field officers
- [ ] On-premise push (no Google FCM / Apple APNs)
- [ ] High-confidence attribution alerts
- [ ] Wallet movement alerts
- [ ] Stylometry match alerts

---

## Shared & Models

- [ ] dwtds_common library
- [ ] Avro schemas for all Kafka topics
- [ ] All model cards published
- [ ] Model signing and verification

---

## Testing

- [ ] Integration tests
- [ ] Security tests (network isolation, RBAC, evidence immutability)
- [ ] E2E tests (full investigation, legal admissibility)
- [ ] Chaos tests (fault injection)
- [ ] Red-team exercise

---

## Compliance Artifacts

- [ ] NCIIPC CAF package
- [ ] CERT-In audit package
- [ ] ISO 27001 ISMS
- [ ] DPDPA DPIA
- [ ] Chain of custody runbook
- [ ] Section 65B certificate template
- [ ] Judicial oversight protocol
- [ ] MLAT procedures

---

## Deployment

- [ ] Air-gap bundle build
- [ ] Two-person integrity transfer
- [ ] Enclave hardening
- [ ] Vault + CA init
- [ ] Plane deployment (7 planes)
- [ ] Post-deployment verification
- [ ] CERT-In auditor walkthrough
- [ ] NCIIPC certification
- [ ] NTRO sign-off

---

## Progress Dashboard

| Plane | Services | Complete | In Progress | Blocked |
|---|---|---|---|---|
| 1 — Infrastructure | 12 | 0 | 0 | 0 |
| 2 — Collection | 14 | 0 | 0 | 0 |
| 3 — Analytics | 18 | 0 | 0 | 0 |
| 4 — Fusion | 10 | 0 | 0 | 0 |
| 5 — Legal & Compliance | 9 | 0 | 0 | 0 |
| 6 — Case & Operations | 8 | 0 | 0 | 0 |
| 7 — Presentation | 7 | 0 | 0 | 0 |
| **TOTAL** | **78** | **0** | **0** | **0** |

---

**Document Version:** 2.0
**Classification:** National Security Grade
**Distribution:** Restricted