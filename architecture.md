# DW-TADS — Dark Web Threat Actor De-Anonymization System
## System Architecture (Binding Contract)

**Codename:** DW-TADS  
**Version:** 2.0 — Production  
**Classification:** National Security Grade / Air-Gapped Deployment  
**Target Agency:** NTRO (National Technical Research Organisation)  
**Compliance:** NCIIPC CAF · CERT-In · ISO/IEC 27001:2022 · NIST CSF 2.0 ·  
NIST SP 800-207 · ISO/IEC 27037 · DPDPA 2023 · Indian Evidence Act Section 65B ·  
IT Act Section 69/69A · CrPC Section 91 · IC3S (MeitY) · Common Criteria EAL 2–4 ·  
NIST PQC · Admiralty Code · STRIDE / LINDDUN  

---

## 1. System Mission

DW-TADS is an air-gapped, event-driven, graph-centric intelligence platform that de-anonymizes dark web threat actors by continuously collecting their footprints across seven planes of operation, fusing them into a single temporal relationship graph, producing court-admissible, confidence-scored attributions, and supporting end-to-end investigation lifecycle from intelligence requirement to prosecution.

### Design Axioms

1. Assume the target environment is hostile.
2. Assume the network is compromised.
3. Assume future quantum decryption.
4. Assume insider threat is possible.
5. Assume every output will be challenged in court.
6. Every inference must be auditable and reproducible.
7. Every output is probabilistic, never binary.
8. Every analyst action is subject to oversight.
9. Every data item has a legal retention limit.
10. Every attribution must be explainable.

---

## 2. Seven-Plane Architecture

```
+--------------------------------------------------------------------------------------+
|                     DW-TADS — AIR-GAPPED ENCLAVE (NTRO)                              |
+--------------------------------------------------------------------------------------+
|                                                                                      |
|  PLANE 7 — PRESENTATION AND DISSEMINATION                                            |
|  Analyst Dashboard · Graph Viz · Reports · Admin Console · Timeline Query ·          |
|  Inter-Agency Gateway · Field Officer Alerting · Classification Marking · Redaction  |
|                                                                                      |
|  PLANE 6 — CASE AND OPERATIONS                                                       |
|  Case Manager · PIR/EEI Tracker · Peer Review · Bias Mitigation · Analyst Wellness · |
|  Insider Threat Detection · HUMINT/Covert Persona Manager · Takedown Coordinator     |
|                                                                                      |
|  PLANE 5 — LEGAL AND COMPLIANCE                                                      |
|  Legal Admissibility (Section 65B) · Legal Intercept Framework · Judicial Oversight ·|
|  Data Retention Automation (DPDPA) · Classification Handler · Court Exhibit Packager |
|                                                                                      |
|  PLANE 4 — INTELLIGENCE FUSION                                                       |
|  Entity Resolver · Confidence Scorer · GNN De-Anon · Autonomous AI Agent · ZKP ·     |
|  Temporal Reasoning · Source Reliability (Admiralty) · Model Drift Monitor ·         |
|  Model Provenance/Explainability                                                     |
|                                                                                      |
|  PLANE 3 — ANALYTICS AND AI                                                          |
|  Misconfig · Clearnet Correlator · Blockchain Clusterer · VASP · Stylometry ·        |
|  Behavioral Profiler · Adversarial Defense · Evidence Anchor · Cognitive Fingerprint ·|
|  Multilingual NLP · Privacy Coin Analyzer · Malware Sandbox · Image/Video Forensics ·|
|  Deepfake Detection                                                                  |
|                                                                                      |
|  PLANE 2 — COLLECTION AND INGESTION                                                  |
|  Tor Proxy · Crawlers (Onion/Forum/Market) · I2P Collector · ZeroNet Collector ·     |
|  Telegram OSINT · Discord OSINT · Matrix OSINT · SimpleX Collector ·                 |
|  Blockchain Nodes (BTC/ETH/XMR/ZEC/DASH) · Clearnet Gateway · Evidence Pipeline      |
|                                                                                      |
|  PLANE 1 — INFRASTRUCTURE AND SECURITY                                               |
|  Docker Swarm · Internal CA · Vault (HSM) · Audit Ledger · Data Diode · Calico ·     |
|  PQC Layer · Key Fragmentation · Chaos Engineering · Cost Governance · Threat Model  |
|                                                                                      |
+--------------------------------------------------------------------------------------+
```

---

## 3. End-to-End Data Flow

### Stream A — Hidden Service Infrastructure Reconnaissance
Tor to Onion Crawler to Misconfig Analyzer + Clearnet Correlator to infra.indicators

### Stream B — Threat Actor Footprint Collection
Multi-network collectors to Content Extractor to Entity Extractor to actor.entities

### Stream C — Blockchain Intelligence
BTC/ETH/XMR/ZEC/DASH nodes to Clustering + Privacy Coin Analyzer + VASP to wallet.attribution

### Stream D — Stylometric and Behavioral Profiling
Multilingual NLP to Stylometry (cross-lingual) + Behavioral + Cognitive to persona.links + behavior.profile

### Stream E — Malware Intelligence
Forum attachments to Sandbox to YARA/SSDEEP to malware.family

### Stream F — Media Forensics
Images/Videos to EXIF + PRNU + Geolocation + Deepfake Detection to media.forensics

### Stream G — HUMINT and Covert Operations
Undercover personas to Controlled interactions to HUMINT signals to covert.intel

**Convergence:** All streams to Unified Relationship Graph to Intelligence Fusion to Case Manager to Legal Admissibility to Analyst Dashboard to Court / Takedown

---

## 4. Service Inventory (78 Services)

### Plane 1 — Infrastructure and Security (12 services)

| Service | Tier | Purpose |
|---------|------|---------|
| tor-proxy-manager | Foundation | Circuit rotation, SOCKS5h proxy management |
| crawler-scheduler | Foundation | Priority task scheduling and pacing |
| evidence-pipeline | Foundation | SHA-256 hashing, signing, Merkle anchoring |
| blockchain-node | Foundation | Multi-chain node ingestion (BTC, ETH, XMR) |
| internal-ca | Foundation | Vault + CFSSL mTLS issuance, 90-day rotation |
| secrets-manager | Foundation | Vault HSM-sealed secrets and key storage |
| audit-ledger | Advanced | Merkle tree, append-only immutable Postgres ledger |
| data-diode | Foundation | Hardware one-way ingest isolation |
| calico-policy-manager | Foundation | Micro-segmentation network policy enforcement |
| chaos-engineering | Advanced | Internal fault injection, game days |
| cost-governance | Intermediate | Per-case resource and cost attribution |
| sbom-signer | Advanced | Software Bill of Materials signing and verification |

### Plane 2 — Collection and Ingestion (14 services)

| Service | Tier | Purpose |
|---------|------|---------|
| onion-crawler | Foundation | Scrapy stealth crawler for hidden services |
| forum-crawler | Foundation | XenForo/IPB/MyBB forum parser |
| marketplace-crawler | Foundation | Dark web marketplace-specific scrapers |
| onion-discovery | Foundation | Hidden service discovery and cataloging |
| ahmia-crawler | Advanced | Ahmia search index scraping and monitoring |
| onionscan-runner | Advanced | OnionScan vulnerability and leak runner |
| forum-loader | Foundation | Forum dump ingestion and parsing |
| threat-feed-loader | Intermediate | ThreatFox, URLhaus, Feodo Tracker feed loader |
| blockchain-loader | Foundation | Raw blockchain transaction loader |
| i2p-collector | Advanced | I2P eepsite and network collector |
| zeronet-collector | Advanced | ZeroNet / ZeroNetX decentralized collector |
| telegram-osint | Advanced | Telegram public channel/group OSINT collector |
| clearnet-enrichment-gateway | Foundation | Clearnet OSINT and enrichment mirror gateway |
| raw-storage | Foundation | Ingested raw artifact storage in MinIO |

### Plane 3 — Analytics and AI (18 services)

| Service | Tier | Purpose |
|---------|------|---------|
| misconfig-analyzer | Intermediate | .onion server misconfiguration detector |
| clearnet-correlator | Intermediate | Favicon/SSL/ETag clearnet correlator |
| blockchain-clusterer | Intermediate | Multi-input heuristic wallet clusterer |
| privacy-coin-analyzer | Expert | Privacy coin tracing and heuristics |
| vasp-attributor | Intermediate | KYC-traceable VASP and exchange attributor |
| entity-extractor | Intermediate | Regex + NER entity extraction from text |
| category-classifier | Intermediate | Dark web listing and post category classifier |
| multilingual-nlp | Advanced | NLLB-200 translation and language processing |
| stylometry-engine | Advanced | Stylometric authorship verification and link analysis |
| behavioral-profiler | Advanced | Posting schedule and timezone profiler |
| cognitive-fingerprint | Expert | Content-blind cognitive fingerprinting |
| adversarial-defense | Expert | LLM/GAN text detection and poison filtering |
| malware-sandbox | Expert | Static and dynamic malware analysis |
| image-forensics | Expert | EXIF, PRNU, geolocation forensics |
| deepfake-detector | Expert | Visual deepfake and synthetic detection |
| synthetic-media-analyzer | Expert | Synthetic audio and multimodal media analyzer |
| evidence-anchor | Advanced | Merkle tree anchor computation |
| yara-generator | Expert | Automated YARA rule generator from samples |

### Plane 4 — Intelligence Fusion (10 services)

| Service | Tier | Purpose |
|---------|------|---------|
| unified-graph | Intermediate | Neo4j relationship graph maintainer |
| entity-resolver | Intermediate | Multi-signal entity resolution and deduplication |
| confidence-scorer | Advanced | Bayesian log-odds attribution scorer |
| gnn-deanon | Expert | Graph neural network link prediction |
| autonomous-agent | Expert | Autonomous intelligence investigation agent |
| zkp-query-layer | Expert | Zero-knowledge proof query verification |
| temporal-reasoner | Advanced | Temporal graph evolution and reasoning |
| source-reliability | Advanced | Admiralty Code reliability scorer |
| model-drift-monitor | Advanced | Model accuracy and drift monitor |
| explainability-engine | Expert | Attribution path explainability and evidence tracing |

### Plane 5 — Legal and Compliance (9 services)

| Service | Tier | Purpose |
|---------|------|---------|
| legal-admissibility | Expert | Section 65B electronic certificate generation |
| legal-intercept | Expert | Lawful interception workflow manager |
| judicial-oversight | Expert | Judicial oversight and warrant verification |
| data-retention | Advanced | DPDPA retention and aging automation |
| classification-handler | Advanced | Security classification marking and redacting |
| court-exhibit-packager | Expert | Sealed, tamper-evident court exhibit packager |
| dpia-engine | Advanced | Data Protection Impact Assessment engine |
| oversight-audit-log | Expert | Dedicated judicial/oversight audit logging |
| mlat-coordinator | Expert | Mutual Legal Assistance Treaty workflow coordinator |

### Plane 6 — Case and Operations (8 services)

| Service | Tier | Purpose |
|---------|------|---------|
| case-manager | Intermediate | Case lifecycle, dossier, and assignment management |
| pir-tracker | Advanced | Priority Intelligence Requirements tracker |
| peer-review | Advanced | Multi-analyst peer review workflow |
| bias-mitigation | Expert | Cognitive bias mitigation and devil's advocate |
| analyst-wellness | Advanced | Analyst exposure and wellness monitoring |
| insider-threat | Expert | Honeytoken and insider threat detection |
| humint-manager | Expert | Covert persona and HUMINT asset lifecycle |
| takedown-coordinator | Advanced | Law enforcement takedown coordination |

### Plane 7 — Presentation and Dissemination (7 services)

| Service | Tier | Purpose |
|---------|------|---------|
| analyst-api | Foundation | FastAPI core REST API with RBAC and JWT |
| analyst-dashboard | Foundation | Analyst web UI and workflow portal |
| graph-visualization | Intermediate | Interactive relationship graph visualizer |
| report-generator | Advanced | Multi-format court and dossier report generator |
| admin-console | Foundation | System administration and user management |
| inter-agency-gateway | Expert | Secure inter-agency intelligence exchange |
| field-alerting | Advanced | Real-time encrypted field officer alerting |

---

## 5. Unified Data Model

### Node Types (17)

Actor · Handle · PGPKey · Wallet · VASP · OnionService · ClearnetIP ·  
SSLCert · Persona · TimeZoneProfile · BehaviorPattern · MalwareSample ·  
Case · Investigation · LegalOrder · HUMINT_Persona · Analyst  

### Edge Types (20)

HasHandle · UsesPGP · ControlsWallet · DepositsTo · ClustersWith ·  
ResolvesTo · SharesCert · StylometricMatch · SameTimeZone · Trusts ·  
AttributedTo · USES_MALWARE · PARTICIPATED_IN · SUBJECT_OF · AUTHORIZED_BY ·  
REVIEWED_BY · PROVIDED_HUMINT · SHARED_WITH · CLASSIFIED_AS · RETENTION_UNTIL  

### Temporal Extensions

Every node and edge carries:
- `valid_from` (when the fact became true)
- `valid_until` (when it ceased to be true; NULL if current)
- `recorded_at` (when DW-TADS learned of it)
- `source_confidence` (Admiralty Code: A–F)
- `information_confidence` (Admiralty Code: 1–6)
- `classification` (U / RESTRICTED / SECRET / TOP_SECRET)

---

## 6. Security Architecture

### Network Segmentation (Calico)

| Segment | Plane(s) | Egress | Ingress |
|---------|----------|--------|---------|
| collection | 2 | Tor SOCKS5h + approved proxies + Telegram MTProto | Kafka only |
| processing | 3, 4 | NONE | Kafka from collection |
| storage | 1, 3, 4, 5, 6 | NONE | Processing + fusion + case + legal |
| presentation | 7 | NONE | Analyst workstations + inter-agency gateway |
| legal | 5 | NONE | Case manager + judicial oversight |
| humint | 6 | Tor (separate circuits) | HUMINT manager only |

### Security Controls

| Control | Implementation | Standard |
|---------|----------------|----------|
| mTLS between all services | Internal CA | NIST SP 800-207 |
| RBAC | JWT + role claims (analyst, senior_analyst, HUMINT_officer, legal_officer, admin, auditor) | ISO 27001 A.9 |
| MFA | TOTP + hardware token | CERT-In |
| Audit logging | Merkle tree, append-only | ISO 27037 |
| Evidence integrity | SHA-256 + Merkle anchor + Section 65B certificate | Indian Evidence Act Section 65B |
| Secrets management | HashiCorp Vault (HSM-sealed) | NIST SP 800-57 |
| Container hardening | Seccomp, AppArmor, CIS images | CIS Benchmarks |
| Network segmentation | Calico policies (7 zones) | NIST SP 800-207 |
| Post-quantum crypto | CRYSTALS-Kyber | NIST PQC |
| Insider threat monitoring | Behavioral analytics + honeytokens | ISO 27001 A.7.2.2 |
| Separation of duties | Two-person rule for critical ops | ISO 27001 A.6.1.2 |
| Data retention | DPDPA automated aging | DPDPA 2023 |
| Source reliability | Admiralty Code | NATO AJP-2.1 |

---

## 7. Compliance Matrix

### Indian Mandatory

- NCIIPC CAF
- CERT-In Empanelment (6-hour incident reporting)
- IC3S (MeitY Common Criteria EAL 2–4)
- SPDI Rules / ISO 27001
- DPDPA 2023 (data minimization, retention, breach notification, DPIA)
- Indian Evidence Act Section 65B (electronic records certificate)
- IT Act Section 69 / 69A (interception, blocking orders)
- CrPC Section 91 (subscriber data requests)
- NIA Act, UAPA (for terror-related cases)

### Global

- ISO/IEC 27001:2022
- ISO/IEC 27017 / 27018
- ISO/IEC 27037 (chain of custody)
- NIST CSF 2.0
- NIST SP 800-207 (zero trust)
- NIST SP 800-57 (key management)
- OWASP ASVS + Top 10
- Common Criteria EAL 2–4
- NIST PQC (CRYSTALS-Kyber)
- Admiralty Code (NATO AJP-2.1)
- Budapest Convention (cross-border)
- MLAT procedures

---

## 8. Deployment Model

**Target:** Linux-based, air-gapped, on-premise NTRO enclave  
**Nodes:** 12 (8 compute + 2 GPU + 2 HA)  
**OS:** Ubuntu 22.04 LTS CIS Level 2 hardened  
**Orchestration:** Docker Swarm (RKE2 alternative via ADR)  
**Deployment:** Two-person integrity, signed bundle, approved media  
**Verification:** Post-deployment compliance audit by CERT-In empanelled auditor  

---

## 9. Architecture Principles (15)

1. Air-gapped by design
2. Zero trust between services
3. Evidence-first data model
4. Confidence-driven attribution
5. Adversarial resilience
6. Sovereign AI stack
7. Modular intelligence streams
8. Audit-by-design
9. Quantum-resistant future-proofing
10. Human-in-the-loop
11. Legal-by-design (Section 65B from day one)
12. Oversight-by-design (judicial access is a feature, not a burden)
13. Multilingual-by-default (no English bias)
14. Multi-network coverage (Tor is one of many)
15. Analyst welfare as security control (burned-out analysts leak)


---

**Document Version:** 2.0  
**Binding:** All code, tests, and deployments MUST conform  
**Distribution:** Restricted — NTRO / Authorized Personnel Only  
