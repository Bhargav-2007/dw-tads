param([ValidateSet('start','load','verify','test','seed','dump','stop')][string]$Action='start')
$ErrorActionPreference='Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
if ($Action -eq 'start') {
    python scripts/preflight.py
    if ($LASTEXITCODE) { exit $LASTEXITCODE }
    if (-not (Test-Path .env)) { python scripts/generate_env.py; if ($LASTEXITCODE) { exit $LASTEXITCODE } }
    docker compose -f docker-compose.airgap.yml build
    if ($LASTEXITCODE) { exit $LASTEXITCODE }
    docker compose -f docker-compose.airgap.yml up -d --wait --wait-timeout 120
    if ($LASTEXITCODE) { docker compose -f docker-compose.airgap.yml ps -a; exit 1 }
} elseif ($Action -eq 'stop') {
    docker compose -f docker-compose.airgap.yml stop
} elseif ($Action -eq 'test') {
    docker compose -f docker-compose.airgap.yml exec -T demo python -m pytest -q -p no:cacheprovider tests/integration
} else {
    docker compose -f docker-compose.airgap.yml exec -T demo python -m demo.cli $Action
}
exit $LASTEXITCODE
