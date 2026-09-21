# README System Architecture — implementation review

Reviewed the System Architecture diagram in README.md against the running public technical-intelligence backend and PostgreSQL, Neo4j, Kafka and MinIO implementation.

The README is a target architecture, not an inventory of deployed or certified capabilities. Its operational person-attribution components remain outside the agreed public technical-intelligence scope. This review does not mark that original architecture complete.

## Gaps implemented in this update

| README component | Implementation |
|---|---|
| A16: MinIO versioning | Enabled versioning for public-intelligence. New snapshot rows preserve object version IDs. Identical content-addressed objects are verified and reused rather than overwritten. Versioning is not Object Lock/WORM retention. |
| B15 / D4: Evidence anchoring | Per-snapshot domain-separated SHA-256 Merkle trees over normalized records; append-only stored anchors; authenticated inclusion proofs and a standalone proof verifier. Original raw snapshot SHA-256 remains the evidence hash. No external signing/notarization or legal-admissibility claim. |
| C1 / C7: Temporal properties and historical queries | Append-only normalized record and relationship versions, backfilled from verified retained snapshots. As-of queries, graph queries, and exports select the latest retained snapshot per source at or before the requested time. |
| C1: Provenance/classification metadata | Technical graph nodes/edges carry observation and recording times and public classification U. Relational classification defaults to U; Admiralty source/information confidence fields are nullable and remain unassessed. |
| Database evolution | Checksummed transactional migration registry with advisory locking; changed applied migrations fail startup; idempotent backfill preserves existing data. |

Historical valid_from/valid_until are observation intervals between retained source snapshots, not assertions of real-world event validity. No data is fabricated for times before the first collection. Historical first_seen/last_seen in the view identify the selected snapshot observation. Current record first_seen retains the initial ingestion time. The Neo4j projection stores current technical records; historical graph queries use retained relational versions.

## Remaining architecture differences

| Plane | Present in current scope | Still absent or different |
|---|---|---|
| 1 Infrastructure/security | Compose, Postgres 16, Kafka KRaft, MinIO, internal backend network, generated credentials, audit chain | Single broker/RF1, single-node databases; no 12-node Swarm, HA, Vault/HSM, internal CA/mTLS, Calico, hardware diode, PQC, SBOM signing or certification |
| 2 Collection | Two fixed official HTTPS feeds, scheduled refresh, object verification, Kafka snapshot events | No Tor/I2P/ZeroNet/messaging collectors, live dark-web crawlers, blockchain nodes or origin-server discovery |
| 3 Analytics | Public technical record normalization, exclusion of identity objects, integrity anchors | No personal stylometry/behavioral profiling, privacy-coin analysis, VASP attribution, malware execution sandbox, media forensics or language models |
| 4 Fusion | Technical graph, provenance, observation history, inclusion proofs | No personal entity resolution, confidence attribution, GNN deanonymization, autonomous targeting, ZKP or model drift system |
| 5 Legal | Audit and provenance support | No warrants/interception, legal certificate generation, judicial portal, retention-policy enforcement or legal-compliance certification |
| 6 Operations | Operator refresh/status/test commands | No case/task/PIR platform, HUMINT/covert operations, insider profiling or takedown orchestration |
| 7 Presentation | Authenticated API, local search page, technical graph JSON, CSV/JSON/HTML exports | Static bearer keys instead of OAuth/JWT/MFA; no React dashboard, Cytoscape UI, PDF/65B reports, inter-agency gateway or push alerts |

Eight containers serve the current public-intelligence scope. They must not be reported as implementation of the README's original 78-service system. Existing historical CHECKLIST-AUDIT.md describes the earlier synthetic build and is not a current online deployment inventory.

## Verification

New tests cover Merkle roots for odd/even trees, altered-record rejection, deployed inclusion proofs, as-of boundary behavior, historical graph/export, append-only history/anchor enforcement, repeatable migrations/backfill, and recovery of older object-version bytes. The test version-recovery objects use unique verification keys and are removed after checking; source evidence is untouched.

Current test results and counts are recorded in ONLINE-VERIFICATION.md and tests/data/online_observed.json after deployment.
