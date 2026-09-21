#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Verifying DW-TADS Services Count Across All 7 Planes ==="

if command -v python.exe &>/dev/null; then
    python.exe scripts/verify_services_count.py
elif command -v python &>/dev/null; then
    python scripts/verify_services_count.py
else
    python3 scripts/verify_services_count.py
fi
