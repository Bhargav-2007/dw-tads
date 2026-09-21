#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Generating .env file for DW-TADS airgap deployment..."

POSTGRES_PASSWORD=$(openssl rand -hex 24)
NEO4J_PASSWORD=$(openssl rand -hex 24)
MINIO_ACCESS_KEY=$(openssl rand -hex 12)
MINIO_SECRET_KEY=$(openssl rand -hex 24)
JWT_SECRET=$(openssl rand -hex 48)
MOCK_MODE=true

cat <<EOF > .env
POSTGRES_USER=dwtds
POSTGRES_DB=dwtds
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
PGHOST=postgres
PGPORT=5432
PGUSER=dwtds
PGDATABASE=dwtds
PGPASSWORD=${POSTGRES_PASSWORD}

NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=${NEO4J_PASSWORD}

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY}

KAFKA_BOOTSTRAP=kafka:9092
KAFKA_HOST=kafka
KAFKA_PORT=9092

JWT_SECRET=${JWT_SECRET}
MOCK_MODE=${MOCK_MODE}
CIRCUIT_ROTATION_SECONDS=300
EOF

echo ".env created with cryptographically secure random secrets."
