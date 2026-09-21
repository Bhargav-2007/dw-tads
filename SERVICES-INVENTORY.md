# DW-TADS Services Inventory (78 Services)

Comprehensive inventory of all 78 microservices distributed across the 7 operational planes of the Dark Web Threat Actor De-Anonymization System (DW-TADS).

## Operational Implementation Tiers

- **Tier A — Real Algorithmic Execution (18 Services)**: Full production-grade business logic, mathematical calculations, graph algorithms, cryptographic hashing, vector similarity, and real variance on all inputs.
- **Tier B — Honest Stubs with Real Logic (60 Services)**: Standalone services executing real Python logic, reading mocked data sources from `mock_sources/`, extracting fields, logging structured audit events with correlation IDs, and returning dynamic outputs varying with input.
- **Tier C — Future Aspirational Capabilities (0 in active codebase)**: Advanced distributed/external capabilities relocated to [`docs/ROADMAP.md`](file:///c:/Users/BHARGAV/Desktop/DW-TADS/docs/ROADMAP.md).

---

## Complete 78-Service Inventory

| # | NAME | PLANE | ARCH TIER | OP TIER | INPUT_TOPICS | OUTPUT_TOPICS | HTTP_PORT |
|---|------|-------|-----------|---------|--------------|---------------|-----------|
| 1 | tor-proxy-manager | 1 (Infrastructure & Security) | Foundation | Tier B | [] | infra.indicators | 8011 |
| 2 | crawler-scheduler | 1 (Infrastructure & Security) | Foundation | Tier B | onion.discovery | crawl.raw | 8012 |
| 3 | evidence-pipeline | 1 (Infrastructure & Security) | Foundation | **Tier A** | crawl.raw, scan.raw | content.clean, merkle.root, audit.events | 8013 |
| 4 | blockchain-node | 1 (Infrastructure & Security) | Foundation | Tier B | [] | chain.tx | 8014 |
| 5 | internal-ca | 1 (Infrastructure & Security) | Foundation | Tier B | [] | audit.events | 8015 |
| 6 | secrets-manager | 1 (Infrastructure & Security) | Foundation | Tier B | [] | audit.events | 8016 |
| 7 | audit-ledger | 1 (Infrastructure & Security) | Advanced | **Tier A** | audit.events | merkle.root | 8017 |
| 8 | data-diode | 1 (Infrastructure & Security) | Foundation | Tier B | quarantine.signals | scan.raw | 8018 |
| 9 | calico-policy-manager | 1 (Infrastructure & Security) | Foundation | Tier B | [] | audit.events | 8019 |
| 10 | chaos-engineering | 1 (Infrastructure & Security) | Advanced | Tier B | [] | service.errors | 8020 |
| 11 | cost-governance | 1 (Infrastructure & Security) | Intermediate | Tier B | audit.events | audit.events | 8021 |
| 12 | sbom-signer | 1 (Infrastructure & Security) | Advanced | Tier B | [] | audit.events | 8022 |
| 13 | onion-crawler | 2 (Collection & Ingestion) | Foundation | Tier B | onion.discovery | crawl.raw | 8023 |
| 14 | forum-crawler | 2 (Collection & Ingestion) | Foundation | Tier B | onion.discovery | crawl.raw | 8024 |
| 15 | marketplace-crawler | 2 (Collection & Ingestion) | Foundation | Tier B | onion.discovery | crawl.raw | 8025 |
| 16 | onion-discovery | 2 (Collection & Ingestion) | Foundation | **Tier A** | [] | onion.discovery | 8026 |
| 17 | ahmia-crawler | 2 (Collection & Ingestion) | Advanced | Tier B | [] | onion.discovery | 8027 |
| 18 | onionscan-runner | 2 (Collection & Ingestion) | Advanced | **Tier A** | onion.discovery | scan.raw | 8028 |
| 19 | forum-loader | 2 (Collection & Ingestion) | Foundation | **Tier A** | [] | crawl.raw, actor.entities | 8029 |
| 20 | threat-feed-loader | 2 (Collection & Ingestion) | Intermediate | **Tier A** | [] | threat.iocs | 8030 |
| 21 | blockchain-loader | 2 (Collection & Ingestion) | Foundation | **Tier A** | [] | chain.tx | 8031 |
| 22 | i2p-collector | 2 (Collection & Ingestion) | Advanced | Tier B | [] | crawl.raw | 8032 |
| 23 | zeronet-collector | 2 (Collection & Ingestion) | Advanced | Tier B | [] | crawl.raw | 8033 |
| 24 | telegram-osint | 2 (Collection & Ingestion) | Advanced | Tier B | [] | crawl.raw | 8034 |
| 25 | clearnet-enrichment-gateway | 2 (Collection & Ingestion) | Foundation | Tier B | infra.indicators | infra.indicators | 8035 |
| 26 | raw-storage | 2 (Collection & Ingestion) | Foundation | Tier B | crawl.raw, scan.raw | audit.events | 8036 |
| 27 | misconfig-analyzer | 3 (Analytics & AI) | Intermediate | **Tier A** | scan.raw | infra.indicators | 8037 |
| 28 | clearnet-correlator | 3 (Analytics & AI) | Intermediate | **Tier A** | scan.raw | infra.indicators | 8038 |
| 29 | blockchain-clusterer | 3 (Analytics & AI) | Intermediate | **Tier A** | chain.tx | wallet.attribution | 8039 |
| 30 | privacy-coin-analyzer | 3 (Analytics & AI) | Expert | Tier B | chain.tx | wallet.attribution | 8040 |
| 31 | vasp-attributor | 3 (Analytics & AI) | Intermediate | **Tier A** | chain.tx | wallet.attribution | 8041 |
| 32 | entity-extractor | 3 (Analytics & AI) | Intermediate | **Tier A** | content.clean | actor.entities | 8042 |
| 33 | category-classifier | 3 (Analytics & AI) | Intermediate | **Tier A** | content.clean | category.signals | 8043 |
| 34 | multilingual-nlp | 3 (Analytics & AI) | Advanced | Tier B | content.clean | content.translated | 8044 |
| 35 | stylometry-engine | 3 (Analytics & AI) | Advanced | **Tier A** | content.clean | persona.links | 8045 |
| 36 | behavioral-profiler | 3 (Analytics & AI) | Advanced | **Tier A** | content.clean | behavior.profile | 8046 |
| 37 | cognitive-fingerprint | 3 (Analytics & AI) | Expert | Tier B | content.clean | cognitive.fingerprint | 8047 |
| 38 | adversarial-defense | 3 (Analytics & AI) | Expert | Tier B | content.clean | quarantine.signals | 8048 |
| 39 | malware-sandbox | 3 (Analytics & AI) | Expert | Tier B | threat.iocs | malware.family | 8049 |
| 40 | image-forensics | 3 (Analytics & AI) | Expert | Tier B | crawl.raw | media.forensics | 8050 |
| 41 | deepfake-detector | 3 (Analytics & AI) | Expert | Tier B | crawl.raw | synthetic.media | 8051 |
| 42 | synthetic-media-analyzer | 3 (Analytics & AI) | Expert | Tier B | synthetic.media | media.forensics | 8052 |
| 43 | evidence-anchor | 3 (Analytics & AI) | Advanced | Tier B | merkle.root | audit.events | 8053 |
| 44 | yara-generator | 3 (Analytics & AI) | Expert | Tier B | malware.family | threat.iocs | 8054 |
| 45 | unified-graph | 4 (Intelligence Fusion) | Intermediate | Tier B | actor.entities, wallet.attribution, infra.indicators, persona.links | audit.events | 8055 |
| 46 | entity-resolver | 4 (Intelligence Fusion) | Intermediate | **Tier A** | actor.entities, infra.indicators, wallet.attribution, persona.links, behavior.profile | persona.links | 8056 |
| 47 | confidence-scorer | 4 (Intelligence Fusion) | Advanced | **Tier A** | persona.links, wallet.attribution, infra.indicators | audit.events | 8057 |
| 48 | gnn-deanon | 4 (Intelligence Fusion) | Expert | Tier B | persona.links | persona.links | 8058 |
| 49 | autonomous-agent | 4 (Intelligence Fusion) | Expert | Tier B | case.events | agent.actions | 8059 |
| 50 | zkp-query-layer | 4 (Intelligence Fusion) | Expert | Tier B | [] | audit.events | 8060 |
| 51 | temporal-reasoner | 4 (Intelligence Fusion) | Advanced | Tier B | behavior.profile | audit.events | 8061 |
| 52 | source-reliability | 4 (Intelligence Fusion) | Advanced | Tier B | actor.entities, threat.iocs | audit.events | 8062 |
| 53 | model-drift-monitor | 4 (Intelligence Fusion) | Advanced | Tier B | persona.links | audit.events | 8063 |
| 54 | explainability-engine | 4 (Intelligence Fusion) | Expert | Tier B | persona.links | audit.events | 8064 |
| 55 | legal-admissibility | 5 (Legal & Compliance) | Expert | Tier B | merkle.root | legal.orders | 8065 |
| 56 | legal-intercept | 5 (Legal & Compliance) | Expert | Tier B | legal.orders | audit.events | 8066 |
| 57 | judicial-oversight | 5 (Legal & Compliance) | Expert | Tier B | audit.events | audit.events | 8067 |
| 58 | data-retention | 5 (Legal & Compliance) | Advanced | Tier B | audit.events | audit.events | 8068 |
| 59 | classification-handler | 5 (Legal & Compliance) | Advanced | Tier B | case.events | audit.events | 8069 |
| 60 | court-exhibit-packager | 5 (Legal & Compliance) | Expert | Tier B | legal.orders | audit.events | 8070 |
| 61 | dpia-engine | 5 (Legal & Compliance) | Advanced | Tier B | audit.events | audit.events | 8071 |
| 62 | oversight-audit-log | 5 (Legal & Compliance) | Expert | Tier B | audit.events | audit.events | 8072 |
| 63 | mlat-coordinator | 5 (Legal & Compliance) | Expert | Tier B | legal.orders | audit.events | 8073 |
| 64 | case-manager | 6 (Case & Operations) | Intermediate | Tier B | case.events | case.events | 8074 |
| 65 | pir-tracker | 6 (Case & Operations) | Advanced | Tier B | case.events | onion.discovery | 8075 |
| 66 | peer-review | 6 (Case & Operations) | Advanced | Tier B | case.events | audit.events | 8076 |
| 67 | bias-mitigation | 6 (Case & Operations) | Expert | Tier B | persona.links | audit.events | 8077 |
| 68 | analyst-wellness | 6 (Case & Operations) | Advanced | Tier B | audit.events | audit.events | 8078 |
| 69 | insider-threat | 6 (Case & Operations) | Expert | Tier B | audit.events | service.errors | 8079 |
| 70 | humint-manager | 6 (Case & Operations) | Expert | Tier B | humint.intel | case.events | 8080 |
| 71 | takedown-coordinator | 6 (Case & Operations) | Advanced | Tier B | legal.orders | case.events | 8081 |
| 72 | analyst-api | 7 (Presentation & Dissemination) | Foundation | **Tier A** | [] | audit.events | 8082 |
| 73 | analyst-dashboard | 7 (Presentation & Dissemination) | Foundation | Tier B | [] | [] | 8083 |
| 74 | graph-visualization | 7 (Presentation & Dissemination) | Intermediate | Tier B | [] | [] | 8084 |
| 75 | report-generator | 7 (Presentation & Dissemination) | Advanced | Tier B | case.events | audit.events | 8085 |
| 76 | admin-console | 7 (Presentation & Dissemination) | Foundation | Tier B | [] | audit.events | 8086 |
| 77 | inter-agency-gateway | 7 (Presentation & Dissemination) | Expert | Tier B | case.events | audit.events | 8087 |
| 78 | field-alerting | 7 (Presentation & Dissemination) | Advanced | Tier B | case.events, threat.iocs | audit.events | 8088 |

---

## Tier A Services Deep-Dive (18 Services)

Every Tier A service implements full algorithmic execution verified by `scripts/verify_input_variance.py`.

| # | Service Name | Plane | Port | 1-Line Algorithm Summary | Key Libraries |
|---|--------------|-------|------|--------------------------|---------------|
| 3 | `evidence-pipeline` | 1 | 8013 | SHA-256 binary-tree Merkle root calculation + RFC3161 ISO-8601 timestamp anchoring for forensic chain-of-custody. | `hashlib`, `datetime` |
| 7 | `audit-ledger` | 1 | 8017 | Linear cryptographic hash chain: `sha256(prev_hash + sequence_id + payload_bytes)` with sequence validation. | `hashlib`, `datetime` |
| 16 | `onion-discovery` | 2 | 8026 | Ahima seed parser + RFC-compliant v3 onion regex extraction (`[a-z2-7]{56}\.onion`) + in-memory deduplication. | `re`, `hashlib` |
| 18 | `onionscan-runner` | 2 | 8028 | Multi-port network probe simulator (80, 443, 8080, 22, 21), EXIF parser, and server banner leak analyzer. | `hashlib`, `datetime` |
| 19 | `forum-loader` | 2 | 8029 | High-throughput forum dump parser extracting thread structure, user handles, timestamps, and message payloads. | `hashlib`, `datetime` |
| 20 | `threat-feed-loader` | 2 | 8030 | ThreatFox and Feodo Tracker IOC parser normalizing IP, domain, and file hashes into structured threat signals. | `hashlib`, `datetime` |
| 21 | `blockchain-loader` | 2 | 8031 | UTXO transaction parser extracting inputs, outputs, satoshi values, and transaction hashes into streaming events. | `hashlib`, `datetime` |
| 27 | `misconfig-analyzer` | 3 | 8037 | Server header banner parsing, Apache/Nginx status page exposure detection, and open directory indexing heuristic checks. | `re`, `hashlib` |
| 28 | `clearnet-correlator` | 3 | 8038 | Multi-attribute Jaccard similarity across SSL certificate fingerprints, SSH host keys, and Google Analytics tracker IDs. | `re`, `hashlib` |
| 29 | `blockchain-clusterer` | 3 | 8039 | Multi-input heuristic clustering (common-input ownership) with deterministic cluster ID assignment and wallet graph mapping. | `hashlib`, `datetime` |
| 31 | `vasp-attributor` | 3 | 8041 | Prefix and deposit address matching against known VASP exchange registries (Binance, Coinbase, Kraken, Huobi). | `hashlib`, `datetime` |
| 32 | `entity-extractor` | 3 | 8042 | Deterministic regex entity extraction for BTC addresses (Base58check), Monero (Base58), PGP keys, emails, Onion URLs, and handles. | `re`, `hashlib` |
| 33 | `category-classifier` | 3 | 8043 | Multi-class keyword frequency scoring across drugs, weapons, stolen data, terror, and financial fraud categories. | `re`, `hashlib` |
| 35 | `stylometry-engine` | 3 | 8045 | Function-word frequency vectorizer (30 English stopwords) + punctuation profile + cosine similarity thresholding (>=0.75). | `numpy`, `re` |
| 36 | `behavioral-profiler` | 3 | 8046 | 24-bin UTC posting activity histogram, timezone offset estimation from posting peaks, and word count mean + variance. | `numpy`, `datetime` |
| 46 | `entity-resolver` | 4 | 8056 | Exact-match identifier resolution across handles, cryptocurrency wallets, and infrastructure fingerprints with deterministic UUIDv5 generation. | `hashlib`, `datetime` |
| 47 | `confidence-scorer` | 4 | 8057 | Weighted multi-signal confidence computation (source reliability 30%, direct match 40%, temporal proximity 30%) with confidence tier binning. | `hashlib`, `datetime` |
| 72 | `analyst-api` | 7 | 8082 | REST API query router with JWT-based authentication validation, role-based access control, query filtering, and audit event dispatch. | `hashlib`, `datetime` |

---

## Breakdown by Plane

| Plane | Total Services | Tier A (Real Algorithmic) | Tier B (Honest Logic Stub) |
|-------|----------------|---------------------------|----------------------------|
| Plane 1 (Infrastructure & Security) | 12 | 2 (`evidence-pipeline`, `audit-ledger`) | 10 |
| Plane 2 (Collection & Ingestion) | 14 | 5 (`onion-discovery`, `onionscan-runner`, `forum-loader`, `threat-feed-loader`, `blockchain-loader`) | 9 |
| Plane 3 (Analytics & AI) | 18 | 8 (`misconfig-analyzer`, `clearnet-correlator`, `blockchain-clusterer`, `vasp-attributor`, `entity-extractor`, `category-classifier`, `stylometry-engine`, `behavioral-profiler`) | 10 |
| Plane 4 (Intelligence Fusion) | 10 | 2 (`entity-resolver`, `confidence-scorer`) | 8 |
| Plane 5 (Legal & Compliance) | 9 | 0 | 9 |
| Plane 6 (Case & Operations) | 8 | 0 | 8 |
| Plane 7 (Presentation & Dissemination) | 7 | 1 (`analyst-api`) | 6 |
| **TOTAL** | **78** | **18** | **60** |

**Grand Total**: 78 Services.
