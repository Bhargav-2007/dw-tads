# DW-TADS — Dark Web Threat Actor De-Anonymization System

**National-security-grade, air-gapped, on-premise intelligence platform for NTRO.**

Conforms to: NCIIPC · CERT-In · ISO 27001 · NIST CSF · NIST SP 800-207 ·  
ISO 27037 · DPDPA 2023 · Indian Evidence Act Section 65B · IT Act Section 69/69A · NIST PQC

**Architecture Reference:** [`architecture.md`](./architecture.md) — binding contract; all code, infrastructure, and tests must conform.

---

## What It Does

DW-TADS continuously collects threat actor footprints across seven intelligence planes, fuses them into a temporal relationship graph, produces court-admissible attribution with calibrated confidence scores, and supports the full investigation lifecycle from intelligence requirement to prosecution.

### Seven Planes

| Plane | Purpose |
|-------|---------|
| 1. Infrastructure and Security | Air-gap, CA, Vault, audit ledger, PQC |
| 2. Collection and Ingestion | Tor, I2P, ZeroNet, Telegram, Discord, Matrix, SimpleX, blockchain |
| 3. Analytics and AI | Stylometry, malware sandbox, privacy coin, multilingual NLP |
| 4. Intelligence Fusion | Graph, GNN, autonomous agent, ZKP, temporal reasoning |
| 5. Legal and Compliance | Section 65B certificates, legal intercept, DPDPA, oversight |
| 6. Case and Operations | Case manager, PIR, peer review, wellness, HUMINT, insider threat |
| 7. Presentation and Dissemination | Analyst dashboard, inter-agency, field alerting |

### 78 Services Across 4 Tiers

- **Tier 1 — Foundation:** 19 services (collection, storage, messaging, basic query)
- **Tier 2 — Intermediate:** 12 services (correlation, clustering, case management)
- **Tier 3 — Advanced:** 25 services (stylometry, malware, temporal, retention)
- **Tier 4 — Expert:** 22 services (GNN, autonomous agent, ZKP, PQC, HUMINT, legal)

---

## Data Flow Summary

Seven parallel intelligence streams (infrastructure, actor, blockchain, stylometry, malware, media, HUMINT) converge into a single temporal relationship graph, feed intelligence fusion, flow through case management and legal admissibility, and reach the analyst dashboard.

---

## Critical Capabilities Often Missed in Dark Web Systems

DW-TADS explicitly includes:

1. Section 65B legal admissibility — every attribution is court-ready
2. Privacy coin de-anonymization — Monero, Zcash, Dash (not just Bitcoin)
3. Multilingual NLP — Russian, Chinese, Arabic, Farsi, Hindi, Bengali, Tamil
4. Non-Tor network coverage — I2P, ZeroNet, Telegram, Discord, Matrix, SimpleX
5. Malware sandbox — code fingerprints as attribution signal
6. HUMINT / covert persona manager — active operations support
7. Legal intercept framework — lawful warrants, subscriber data, Section 69 orders
8. Case management — structured, auditable investigations
9. Insider threat detection — behavioral analytics + honeytokens
10. Analyst wellness — trauma exposure tracking, rotation, counseling
11. Judicial oversight interface — independent oversight as a feature
12. Data retention automation — DPDPA compliance by design
13. Deepfake and synthetic media detection — AI-generated content
14. Temporal reasoning — time-travel queries, actor lifecycle
15. Source reliability (Admiralty Code) — A–F / 1–6 scoring
16. Model drift monitoring — silent accuracy decay prevention
17. Explainability engine — SHAP/LIME + graph path explanations
18. Inter-agency sharing — IB, RAW, CBI, NIA, state police
19. Field officer alerting — encrypted push, no external providers
20. Chaos engineering — internal fault injection

---

## System Architecture

> **Implementation status:** This diagram describes the target architecture. The running build is the online public technical-intelligence backend, not the complete 78-service system. See [architecture implementation review](ARCHITECTURE-IMPLEMENTATION-REVIEW.md) for implemented database/evidence features and remaining gaps, and [backend handoff](HANDOFF-BACKEND.md) for current startup/API instructions. Production security and compliance claims below are design targets, not verified certifications.

Full end-to-end architecture covering all seven planes, service tiers, Kafka-mediated data flows, and cross-cutting security controls.

> **View this diagram:** It renders automatically on GitHub. For an interactive full-screen view, copy the diagram below into [mermaid.live](https://mermaid.live).

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "primaryColor": "#1e3a8a",
    "primaryTextColor": "#ffffff",
    "primaryBorderColor": "#1e40af",
    "lineColor": "#64748b",
    "secondaryColor": "#0f766e",
    "tertiaryColor": "#7c2d12",
    "background": "#0f172a",
    "mainBkg": "#1e293b",
    "nodeBorder": "#334155",
    "clusterBkg": "#111827",
    "clusterBorder": "#475569",
    "titleColor": "#f1f5f9",
    "edgeLabelBackground": "#1e293b",
    "fontFamily": "Inter, Segoe UI, Roboto, sans-serif",
    "fontSize": "13px"
  },
  "flowchart": {
    "curve": "basis",
    "padding": 20,
    "nodeSpacing": 55,
    "rankSpacing": 75,
    "htmlLabels": true,
    "useMaxWidth": false
  }
}}%%
flowchart TD
    subgraph Collection["PLANE 2 — COLLECTION AND INGESTION"]
        direction TB
        A1["External Sources<br/>.onion, I2P, ZeroNet<br/>Telegram, Discord, Matrix<br/>SimpleX, Forums, Markets"]
        A2["Tor Proxy Manager<br/>Tier 1 — Foundation<br/>Circuit rotation, SOCKS5h"]
        A3["Crawler Scheduler<br/>Tier 1 — Foundation<br/>Celery + Redis priority queue"]
        A4["Onion Crawler<br/>Tier 1 — Foundation<br/>Scrapy stealth, honeypot-aware"]
        A5["Forum Crawler<br/>Tier 1 — Foundation<br/>XenForo, IPB, MyBB, vBulletin"]
        A6["Marketplace Crawler<br/>Tier 1 — Foundation<br/>Plugin adapter SDK"]
        A7["I2P Collector<br/>Tier 3 — Advanced"]
        A8["ZeroNet Collector<br/>Tier 3 — Advanced"]
        A9["Telegram OSINT<br/>Tier 3 — Advanced<br/>Public channel monitoring"]
        A10["Discord OSINT<br/>Tier 3 — Advanced<br/>Public guild monitoring"]
        A11["Matrix OSINT<br/>Tier 3 — Advanced<br/>Element room monitoring"]
        A12["SimpleX Collector<br/>Tier 4 — Expert<br/>Metadata-free protocol"]
        A13["Blockchain Nodes<br/>Tier 1 — Foundation<br/>bitcoind, geth, XMR, ZEC, DASH"]
        A14["Clearnet Enrichment Gateway<br/>Tier 1 — Foundation<br/>Shodan, Censys local mirrors"]
        A15["Evidence Ingestion Pipeline<br/>Tier 1 — Foundation<br/>SHA-256, sign, Merkle anchor"]
        A16[("MinIO Raw Storage<br/>Tier 1 — Foundation<br/>Immutable versioning")]
        A17["Kafka Event Bus<br/>Tier 1 — Foundation<br/>3-broker KRaft, RF=3"]
    end
    subgraph Analytics["PLANE 3 — ANALYTICS AND ARTIFICIAL INTELLIGENCE"]
        direction TB
        B1["Misconfiguration Analyzer<br/>Tier 2 — Intermediate"]
        B2["Clearnet Correlation Engine<br/>Tier 2 — Intermediate"]
        B3["Blockchain Clustering Engine<br/>Tier 2 — Intermediate"]
        B4["Privacy Coin Analyzer<br/>Tier 4 — Expert<br/>XMR, ZEC, DASH"]
        B5["VASP Attribution Service<br/>Tier 2 — Intermediate"]
        B6["Multilingual NLP Engine<br/>Tier 3 — Advanced<br/>NLLB-200, fastText, CLD3"]
        B7["Stylometry Engine<br/>Tier 3 — Advanced<br/>XLM-R + SBERT cross-lingual"]
        B8["Behavioral Profiler<br/>Tier 3 — Advanced"]
        B9["Cognitive Fingerprint Analyzer<br/>Tier 4 — Expert"]
        B10["Adversarial ML Defense<br/>Tier 4 — Expert<br/>LLM-wall, GAN-text detection"]
        B11["Malware Sandbox<br/>Tier 4 — Expert<br/>QEMU/KVM, YARA, SSDEEP"]
        B12["Image Forensics<br/>Tier 4 — Expert<br/>EXIF, PRNU, geolocation"]
        B13["Deepfake Detector<br/>Tier 4 — Expert<br/>Image, video, voice, AI-text"]
        B14["Synthetic Media Analyzer<br/>Tier 4 — Expert"]
        B15["Evidence Anchor Service<br/>Tier 3 — Advanced<br/>Merkle tree construction"]
        B16["Language Detector<br/>Tier 3 — Advanced"]
        B17["Transliteration Normalizer<br/>Tier 3 — Advanced<br/>Cyrillic, Arabic to Latin"]
        B18["YARA Generator<br/>Tier 4 — Expert"]
    end
    subgraph Fusion["PLANE 4 — INTELLIGENCE FUSION"]
        direction TB
        C1[("Unified Relationship Graph<br/>Neo4j 5 Enterprise<br/>17 node types, 20 edge types<br/>Temporal properties")]
        C2["Entity Resolution Service<br/>Tier 2 — Intermediate<br/>Louvain, PageRank"]
        C3["Confidence Scorer<br/>Tier 3 — Advanced<br/>Bayesian log-odds fusion"]
        C4["GNN De-Anonymization<br/>Tier 4 — Expert<br/>GraphSAGE, PyG/DGL"]
        C5["Autonomous AI Agent<br/>Tier 4 — Expert<br/>Llama-3 13B, RAG, tools"]
        C6["ZKP Query Layer<br/>Tier 4 — Expert<br/>zk-STARK, BLS"]
        C7["Temporal Reasoner<br/>Tier 3 — Advanced<br/>Time-travel queries"]
        C8["Source Reliability<br/>Tier 3 — Advanced<br/>Admiralty Code A-F, 1-6"]
        C9["Model Drift Monitor<br/>Tier 3 — Advanced<br/>Accuracy, bias tracking"]
        C10["Explainability Engine<br/>Tier 4 — Expert<br/>SHAP, LIME, graph paths"]
    end
    subgraph Legal["PLANE 5 — LEGAL AND COMPLIANCE"]
        direction TB
        F1["Legal Admissibility<br/>Tier 4 — Expert<br/>Section 65B certificates"]
        F2["Legal Intercept Framework<br/>Tier 4 — Expert<br/>Warrants, 69, 69A, CrPC 91"]
        F3["Judicial Oversight Portal<br/>Tier 4 — Expert<br/>Read-only judge access"]
        F4["Data Retention Engine<br/>Tier 3 — Advanced<br/>DPDPA aging, deletion"]
        F5["Classification Handler<br/>Tier 3 — Advanced<br/>Auto-marking, downgrade"]
        F6["Court Exhibit Packager<br/>Tier 4 — Expert<br/>Sealed, tamper-evident"]
        F7["DPIA Engine<br/>Tier 3 — Advanced"]
        F8["Oversight Audit Log<br/>Tier 4 — Expert<br/>Separate from system audit"]
        F9["MLAT Coordinator<br/>Tier 4 — Expert<br/>Cross-border legal"]
    end
    subgraph Case["PLANE 6 — CASE AND OPERATIONS"]
        direction TB
        G1["Case Manager<br/>Tier 2 — Intermediate<br/>Lifecycle, task board"]
        G2["PIR Tracker<br/>Tier 3 — Advanced<br/>Priority Intel Requirements"]
        G3["Peer Review<br/>Tier 3 — Advanced<br/>Blind re-analysis"]
        G4["Bias Mitigation<br/>Tier 4 — Expert<br/>Devil's advocate"]
        G5["Analyst Wellness<br/>Tier 3 — Advanced<br/>Trauma exposure, rotation"]
        G6["Insider Threat Detection<br/>Tier 4 — Expert<br/>Behavioral, honeytokens"]
        G7["HUMINT Manager<br/>Tier 4 — Expert<br/>Covert persona, burn protocol"]
        G8["Takedown Coordinator<br/>Tier 3 — Advanced<br/>LE coordination"]
    end
    subgraph Presentation["PLANE 7 — PRESENTATION AND DISSEMINATION"]
        direction TB
        H1["Analyst API Gateway<br/>Tier 1 — Foundation<br/>FastAPI, OAuth2, JWT, MFA, RBAC"]
        H2["Analyst Dashboard<br/>Tier 1 — Foundation<br/>React, TypeScript"]
        H3["Graph Visualization<br/>Tier 2 — Intermediate<br/>Cytoscape.js, D3.js"]
        H4["Report Generator<br/>Tier 3 — Advanced<br/>PDF with Section 65B"]
        H5["Admin Console<br/>Tier 1 — Foundation"]
        H6["Inter-Agency Gateway<br/>Tier 4 — Expert<br/>IB, RAW, CBI, NIA"]
        H7["Field Alerting<br/>Tier 3 — Advanced<br/>Encrypted push"]
    end
    subgraph Infra["PLANE 1 — INFRASTRUCTURE AND SECURITY (CROSS-CUTTING)"]
        direction TB
        D1["Docker Swarm<br/>Tier 1 — Foundation<br/>12-node, 7 plane labels"]
        D2["Internal CA<br/>Tier 1 — Foundation<br/>Vault + CFSSL, mTLS"]
        D3["Secrets Manager<br/>Tier 1 — Foundation<br/>Vault HSM, 3-of-5 shares"]
        D4["Audit Ledger<br/>Tier 3 — Advanced<br/>Merkle, append-only"]
        D5["Data Diode<br/>Tier 1 — Foundation"]
        D6["Calico Policies<br/>Tier 1 — Foundation<br/>7 zone segmentation"]
        D7["PQC Layer<br/>Tier 4 — Expert<br/>CRYSTALS-Kyber"]
        D8["Key Fragmentation<br/>Tier 4 — Expert<br/>N-of-M Tor circuits"]
        D9["Chaos Engineering<br/>Tier 3 — Advanced"]
        D10["Cost Governance<br/>Tier 2 — Intermediate"]
        D11["Threat Model Engine<br/>Tier 2 — Intermediate<br/>STRIDE, LINDDUN"]
        D12["SBOM Signer<br/>Tier 3 — Advanced<br/>syft + cosign"]
    end
    A1 ==>|"target seeds"| A2
    A1 ==>|"forum sources"| A5
    A1 ==>|"market sources"| A6
    A1 ==>|"i2p sources"| A7
    A1 ==>|"zeronet sources"| A8
    A1 ==>|"telegram channels"| A9
    A1 ==>|"discord guilds"| A10
    A1 ==>|"matrix rooms"| A11
    A1 ==>|"simplex groups"| A12
    A1 ==>|"chain data"| A13
    A1 ==>|"clearnet indexes"| A14
    A2 ==>|"isolated circuit"| A3
    A3 ==>|"task dispatch"| A4
    A3 ==>|"task dispatch"| A5
    A3 ==>|"task dispatch"| A6
    A3 ==>|"task dispatch"| A7
    A3 ==>|"task dispatch"| A8
    A3 ==>|"task dispatch"| A9
    A3 ==>|"task dispatch"| A10
    A3 ==>|"task dispatch"| A11
    A3 ==>|"task dispatch"| A12
    A4 ==>|"raw HTML, certs"| A15
    A5 ==>|"raw posts"| A15
    A6 ==>|"raw listings"| A15
    A7 ==>|"i2p content"| A15
    A8 ==>|"zeronet content"| A15
    A9 ==>|"telegram msgs"| A15
    A10 ==>|"discord msgs"| A15
    A11 ==>|"matrix msgs"| A15
    A12 ==>|"simplex msgs"| A15
    A13 ==>|"blocks, TXs"| A15
    A14 ==>|"favicon, SSL, ETag"| A15
    A15 ==>|"immutable artifacts"| A16
    A15 ==>|"scan.raw<br/>crawl.raw<br/>chain.tx"| A17
    A17 -->|"scan.raw"| B1
    A17 -->|"scan.raw"| B2
    A17 -->|"chain.tx"| B3
    A17 -->|"chain.tx"| B4
    A17 -->|"chain.tx"| B5
    A17 -->|"crawl.raw"| B6
    A17 -->|"content.clean"| B7
    A17 -->|"content.clean"| B8
    A17 -->|"behavioral corpus"| B9
    A17 -->|"crawl.raw"| B10
    A17 -->|"malware samples"| B11
    A17 -->|"media artifacts"| B12
    A17 -->|"media artifacts"| B13
    A17 -->|"media artifacts"| B14
    A17 -->|"all evidence"| B15
    A17 -->|"crawl.raw"| B16
    A17 -->|"crawl.raw"| B17
    A17 -->|"malware samples"| B18
    B1 -->|"infra.indicators"| A17
    B2 -->|"infra.indicators"| A17
    B3 -->|"wallet.attribution"| A17
    B4 -->|"wallet.attribution"| A17
    B5 -->|"wallet.attribution"| A17
    B6 -->|"content.translated"| A17
    B7 -->|"persona.links"| A17
    B8 -->|"behavior.profile"| A17
    B9 -->|"cognitive.fingerprint"| A17
    B10 -->|"quarantine.signals"| A17
    B11 -->|"malware.family"| A17
    B12 -->|"media.forensics"| A17
    B13 -->|"synthetic.media"| A17
    B14 -->|"synthetic.media"| A17
    B15 -->|"merkle.root"| A17
    B16 -->|"lang.detected"| A17
    B17 -->|"transliteration"| A17
    B18 -->|"yara.rules"| A17
    A17 ==>|"all topics"| C1
    C1 <-->|"actor graph"| C2
    C1 <-->|"confidence"| C3
    C1 <-->|"GNN links"| C4
    C1 <-->|"AI hypotheses"| C5
    C1 <-->|"ZKP queries"| C6
    C1 <-->|"temporal queries"| C7
    C1 <-->|"source scores"| C8
    C1 <-->|"drift signals"| C9
    C1 <-->|"explanations"| C10
    C1 ==>|"attributions<br/>with evidence"| F1
    C1 ==>|"targets for<br/>intercept"| F2
    C1 ==>|"investigation<br/>summaries"| F3
    C1 ==>|"data subjects"| F4
    C1 ==>|"classification<br/>required"| F5
    C1 ==>|"evidence for<br/>court package"| F6
    C1 ==>|"PI data flows"| F7
    C1 ==>|"legal actions"| F8
    C1 ==>|"cross-border<br/>cases"| F9
    F1 -.->|"65B certs"| C1
    F2 -.->|"warrants"| C1
    F4 -.->|"retention tags"| C1
    F5 -.->|"classification"| C1
    F6 -.->|"sealed exhibits"| C1
    F8 -.->|"audit trail"| C1
    C1 ==>|"findings"| G1
    C1 ==>|"gaps"| G2
    C1 ==>|"high-confidence<br/>attributions"| G3
    C1 ==>|"bias risks"| G4
    C1 ==>|"analyst actions"| G5
    C1 ==>|"access patterns"| G6
    C1 ==>|"OSINT context<br/>for HUMINT"| G7
    C1 ==>|"takedown targets"| G8
    G1 -.->|"case tags"| C1
    G2 -.->|"collection<br/>tasking"| C1
    G3 -.->|"review status"| C1
    G4 -.->|"bias flags"| C1
    G5 -.->|"exposure data"| C1
    G6 -.->|"threat alerts"| C1
    G7 -.->|"HUMINT intel"| C1
    G8 -.->|"LE feedback"| C1
    C1 ==>|"graph reads<br/>mTLS"| H1
    F1 ==>|"court exports"| H4
    F3 ==>|"judicial view"| H5
    G1 ==>|"case context"| H2
    G8 ==>|"takedown<br/>status"| H7
    H1 ==>|"authenticated<br/>session"| H2
    H2 ==>|"graph render"| H3
    H2 ==>|"report request"| H4
    H2 ==>|"admin ops"| H5
    H2 ==>|"inter-agency<br/>share"| H6
    H2 ==>|"field alert"| H7
    H3 -.->|"visual data"| H2
    H4 -.->|"generated<br/>report"| H2
    H5 -.->|"admin<br/>confirmations"| H2
    H6 -.->|"shared intel<br/>redacted"| H2
    H7 -.->|"delivery<br/>receipt"| H2
    D1 -.->|"container<br/>scheduling"| Collection
    D1 -.->|"container<br/>scheduling"| Analytics
    D1 -.->|"container<br/>scheduling"| Fusion
    D1 -.->|"container<br/>scheduling"| Legal
    D1 -.->|"container<br/>scheduling"| Case
    D1 -.->|"container<br/>scheduling"| Presentation
    D2 -.->|"mTLS certs"| A2
    D2 -.->|"mTLS certs"| B7
    D2 -.->|"mTLS certs"| C1
    D2 -.->|"mTLS certs"| F1
    D2 -.->|"mTLS certs"| G1
    D2 -.->|"mTLS certs"| H1
    D3 -.->|"secrets"| A15
    D3 -.->|"secrets"| B7
    D3 -.->|"secrets"| C1
    D3 -.->|"secrets"| F1
    D3 -.->|"secrets"| G1
    D3 -.->|"secrets"| H1
    D4 -.->|"evidence<br/>anchoring"| A15
    D4 -.->|"query/export<br/>hashing"| H1
    D4 -.->|"agent action<br/>logging"| C5
    D4 -.->|"ZKP proof<br/>verification"| C6
    D4 -.->|"legal action<br/>logging"| F8
    D5 -.->|"threat feeds"| A14
    D5 -.->|"model weights"| B7
    D5 -.->|"GNN checkpoints"| C4
    D6 -.->|"collection<br/>egress policy"| Collection
    D6 -.->|"processing<br/>no-internet"| Analytics
    D6 -.->|"storage<br/>lockdown"| Fusion
    D6 -.->|"legal<br/>isolation"| Legal
    D6 -.->|"case<br/>isolation"| Case
    D6 -.->|"presentation<br/>RBAC"| Presentation
    D7 -.->|"PQC evidence"| B15
    D7 -.->|"PQC audit"| D4
    D7 -.->|"PQC ZKP"| C6
    D8 -.->|"key shares"| A2
    D8 -.->|"reconstruction"| D3
    D8 -.->|"signing shares"| A15
    classDef tier1 fill:#1e40af,stroke:#93c5fd,stroke-width:2px,color:#ffffff,rx:8,ry:8
    classDef tier2 fill:#0f766e,stroke:#5eead4,stroke-width:2px,color:#ffffff,rx:8,ry:8
    classDef tier3 fill:#b45309,stroke:#fcd34d,stroke-width:2px,color:#ffffff,rx:8,ry:8
    classDef tier4 fill:#991b1b,stroke:#fca5a5,stroke-width:2px,color:#ffffff,rx:8,ry:8
    class A2,A3,A4,A5,A6,A13,A14,A15,A16,A17 tier1
    class A7,A8,A9,A10,A11 tier3
    class A12 tier4
    class B1,B2,B3,B5 tier2
    class B6,B7,B8,B15,B16,B17 tier3
    class B4,B9,B10,B11,B12,B13,B14,B18 tier4
    class C1,C2 tier2
    class C3,C7,C8,C9 tier3
    class C4,C5,C6,C10 tier4
    class F4,F5,F7 tier3
    class F1,F2,F3,F6,F8,F9 tier4
    class G1 tier2
    class G2,G3,G5,G8 tier3
    class G4,G6,G7 tier4
    class H1,H2,H5 tier1
    class H3 tier2
    class H4,H7 tier3
    class H6 tier4
    class D1,D2,D3,D5,D6 tier1
    class D10,D11 tier2
    class D4,D9,D12 tier3
    class D7,D8 tier4
    classDef external fill:#334155,stroke:#94a3b8,stroke-width:2px,color:#f1f5f9,stroke-dasharray: 5 5
    class A1 external
    style Collection fill:#0c1a3a,stroke:#3b82f6,stroke-width:3px,color:#dbeafe
    style Analytics fill:#0c2a2a,stroke:#14b8a6,stroke-width:3px,color:#ccfbf1
    style Fusion fill:#2a1a3a,stroke:#a855f7,stroke-width:3px,color:#e9d5ff
    style Legal fill:#2a1a1a,stroke:#ef4444,stroke-width:3px,color:#fee2e2
    style Case fill:#1a2a1a,stroke:#84cc16,stroke-width:3px,color:#ecfccb
    style Presentation fill:#0c2a1a,stroke:#22c55e,stroke-width:3px,color:#dcfce7
    style Infra fill:#1a1a1a,stroke:#6b7280,stroke-width:3px,color:#e5e7eb

```

**Tier color legend**

| Color | Tier | Meaning |
|-------|------|---------|
| Blue | Tier 1 — Foundation | Required core services |
| Teal | Tier 2 — Intermediate | Intelligence and case services |
| Amber | Tier 3 — Advanced | AI-driven and retention services |
| Red | Tier 4 — Expert | Next-generation and legal services |
| Slate (dashed) | External | Sources outside the enclave |

---

## Repository Layout

```
dw-tads/
├── README.md
├── CHECKLIST.md
├── architecture.md
├── Makefile
├── docker-compose.airgap.yml
├── swarm/                 # 7 stack files (one per plane)
├── infra/                 # Vault, CA, Kafka, Postgres, Neo4j, MinIO, Calico
├── services/              # 78 services across 7 planes
├── frontend/              # analyst-dashboard, admin-console, oversight-portal
├── models/                # stylometry, gnn, adversarial, llm, multilingual
├── shared/                # dwtds_common library, Avro schemas
├── scripts/               # build, transfer, enclave, deploy, verify, ci
├── compliance/            # NCIIPC, CERT-In, ISO, DPDPA packages
├── training/              # operator, analyst, IC, auditor handbooks
├── tests/                 # integration, security, e2e, chaos
└── docs/                  # architecture, runbooks, model cards, ADRs
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Orchestration | Docker Swarm (RKE2 alt.) |
| Message Bus | Apache Kafka 3.7 (KRaft, 3-broker) |
| Relational DB | PostgreSQL 16 |
| Graph DB | Neo4j 5 Enterprise |
| Object Storage | MinIO |
| Search | OpenSearch (for malware/forensics) |
| Backend | FastAPI (Python 3.11+) |
| ML/NLP | PyTorch, Transformers, spaCy, NLLB-200 |
| GNN | PyTorch Geometric / DGL |
| LLM | Llama-3-13B-Instruct (GGUF) |
| Blockchain | bitcoind, geth, Monero, Zcash, Dash |
| Anonymity Networks | Tor, I2P, ZeroNet |
| Messaging OSINT | Telegram Bot API, Discord, Matrix |
| Malware | QEMU/KVM sandbox, YARA, SSDEEP |
| Forensics | ExifTool, PRNU, image forensics |
| Frontend | React + TypeScript + Cytoscape.js |
| Secrets | HashiCorp Vault (HSM-sealed) |
| Network Policies | Calico / Cilium |
| Audit | Merkle tree, append-only Postgres |
| PQC | CRYSTALS-Kyber |

---

## Compliance

**Indian:** NCIIPC CAF · CERT-In · IC3S · SPDI · DPDPA 2023 ·  
Evidence Act Section 65B · IT Act Section 69/69A · CrPC Section 91 · NIA Act · UAPA

**Global:** ISO 27001:2022 · ISO 27017/27018 · ISO 27037 · NIST CSF 2.0 ·  
NIST SP 800-207 · NIST SP 800-57 · OWASP ASVS · Common Criteria EAL 2–4 ·  
NIST PQC · Admiralty Code · Budapest Convention

---

## Build and Deploy

```bash
make bundle                    # Clearnet build host
./scripts/transfer/02-transfer-log.sh    # Two-person integrity
./scripts/enclave/00-baseline-hardening.sh
./scripts/infra/10-initialize-vault.sh
./scripts/deploy/00-preflight.sh
./scripts/deploy/10-deploy-all-planes.sh
./scripts/verify/50-verify-compliance-controls.sh
```

Full procedure: `docs/deployment-runbook.md`

---

## Testing

```bash
pytest tests/integration -v
pytest tests/security -v
pytest tests/e2e -v
pytest tests/chaos -v
./tests/security/test_airgap.sh
```

---

## Contributing

1. Read `architecture.md` — binding contract.
2. Pick an unchecked item in `CHECKLIST.md`.
3. Branch: `feat/<plane>/<service>`.
4. Include tests + model cards + ADRs if deviating.
5. Update `CHECKLIST.md` before merge.

---

## Classification

**National Security Grade**  
**Distribution:** Restricted — NTRO / Authorized Personnel Only  
**Document Version:** 2.0  
