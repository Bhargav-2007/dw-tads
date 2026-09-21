#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f docker-compose.airgap.yml exec -T demo python -m demo.cli dump
