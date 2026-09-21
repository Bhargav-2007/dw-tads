#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Resetting DW-TADS Demo Environment ==="

python3 - <<'EOF'
import sys, os
from common.db import get_pg_conn, get_neo4j_driver

# Reset Postgres
try:
    with get_pg_conn() as conn:
        conn.execute("TRUNCATE TABLE evidence, audit_log, source_fetches, processed, outbox CASCADE;")
        conn.commit()
        print("Postgres tables truncated successfully.")
except Exception as e:
    print(f"Notice: Postgres truncate skipped ({e})")

# Reset Neo4j
try:
    driver = get_neo4j_driver()
    with driver.session() as s:
        s.run("MATCH (n) DETACH DELETE n")
        print("Neo4j graph cleared successfully.")
    driver.close()
except Exception as e:
    print(f"Notice: Neo4j reset skipped ({e})")

print("Reset complete.")
EOF
