param([ValidateSet('start','refresh','test','status','stop')][string]$Action='start')
$ErrorActionPreference='Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$composeArgs=@('compose','-f','docker-compose.airgap.yml','-f','docker-compose.online.yml')
if ($Action -eq 'start') {
    python scripts/generate_online_env.py
    if ($LASTEXITCODE) { exit $LASTEXITCODE }
    docker @composeArgs build
    if ($LASTEXITCODE) { exit $LASTEXITCODE }
    docker @composeArgs up -d --wait --wait-timeout 120
    if ($LASTEXITCODE) { docker @composeArgs ps -a; exit 1 }
} elseif ($Action -eq 'refresh') {
    docker @composeArgs exec -T collector python -m intel.collector
} elseif ($Action -eq 'test') {
    docker @composeArgs exec -T demo python -m pytest -q -p no:cacheprovider tests/online
} elseif ($Action -eq 'stop') {
    docker @composeArgs stop
} else {
    docker @composeArgs ps -a
}
exit $LASTEXITCODE
