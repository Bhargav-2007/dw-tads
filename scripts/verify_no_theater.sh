#!/usr/bin/env bash
set -euo pipefail

FAIL=0
for svc_file in $(find services -name "*.py" -not -name "base_service.py" -not -name "__init__.py"); do
  svc=$(basename "$svc_file" .py)

  # Rule 1: must read message
  if ! grep -q "message\[" "$svc_file"; then
    echo "FAIL $svc: does not read message"
    FAIL=$((FAIL+1))
    continue
  fi

  # Rule 2: must import a real client
  if ! grep -qE "^(import|from) (requests|httpx|neo4j|psycopg|asyncpg|sqlalchemy|minio|aiokafka|kafka|sentence_transformers|transformers|torch|stem|sqlite3|re|hashlib|numpy)" "$svc_file"; then
    echo "FAIL $svc: no real client import"
    FAIL=$((FAIL+1))
    continue
  fi

  # Rule 3: output must vary with input (heuristic — must have conditional logic)
  if ! grep -qE "(if |elif |for |while |max\(|min\(|sum\(|np\.|numpy\.)" "$svc_file"; then
    echo "FAIL $svc: no conditional logic"
    FAIL=$((FAIL+1))
    continue
  fi

  # Rule 4: must declare tier
  if ! grep -q 'Tier: [AB]' "$svc_file"; then
    echo "FAIL $svc: no tier declaration"
    FAIL=$((FAIL+1))
  fi
done

if [ $FAIL -gt 0 ]; then
  echo "TOTAL FAILURES: $FAIL"
  exit 1
fi
echo "ALL SERVICES PASS"
exit 0
