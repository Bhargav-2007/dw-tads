# Online backend verification

Verified 2026-09-20 after the README architecture data-layer update.

| Check | Result |
|---|---|
| Deployed services | Eight containers healthy |
| CISA KEV | 1,716 active vulnerability records |
| MITRE ATT&CK | 730 malware and 697 technique records |
| Technical relationships | 10,493 |
| Retained record versions | 3,143 |
| Retained relationship versions | 10,493 |
| Merkle anchors | Two; retained snapshots backfilled and verified |
| MinIO versioning | Enabled; previous-version recovery tested |
| Schema migrations | 001_history_and_integrity.sql applied and checksummed |
| Audit chain | Valid after migration/backfill and tests |
| Authentication | Existing required-token checks pass |
| Full active online suite | 24 passed in 17.58 seconds |
| Diagnostics | One Starlette/AnyIO deprecation warning; no failures |

Run `.\scripts\online.ps1 test` to repeat the active suite. The historical tests/integration suite targets the earlier synthetic-only deployment and is not the active online pipeline suite.

The new tests independently construct Merkle trees for single, even, and odd leaf counts; reject altered payloads; check deployed proofs; verify as-of time boundaries and historical graph/export; enforce append-only rows; reject modified applied migrations; exercise idempotent backfill and transaction rollback; and recover original object-version bytes. Recovery test objects use unique temporary keys, and only those test-created versions are removed. No source evidence was deleted.

Existing tests additionally cover live source processing, auth, filters/pagination, source hashes, replay, exports, technical-object restrictions, audit integrity, and Kafka dead-letter routing. Repeated test runs add malformed Kafka test events without changing indexed records.

Observed runtime counts and source/snapshot metadata are in tests/data/online_observed.json. Remaining gaps against the original README diagram are in ARCHITECTURE-IMPLEMENTATION-REVIEW.md. This verifies the public technical-intelligence scope, not the original 78-service system or production certification.
