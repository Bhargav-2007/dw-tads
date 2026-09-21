#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v node >/dev/null 2>&1; then
  export PATH="$(pwd)/../.tools/node-v20.19.0-linux-x64/bin:$PATH"
fi
exec npm run dev