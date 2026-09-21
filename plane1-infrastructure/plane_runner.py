"""Plane 1 runner (FastAPI + asynccontextmanager lifespan)."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shared", "python"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from services import SERVICES


@asynccontextmanager
async def lifespan(app: FastAPI):
    kafka = pg = neo4j = minio = None
    # Attempt real client startup; degrade gracefully on failure
    try:
        from dwtds_common.kafka_client import KafkaProducer
        from dwtds_common.pg_client import PgClient
        from dwtds_common.neo4j_client import Neo4jClient
        from dwtds_common.minio_client import MinioClient

        kafka = KafkaProducer([os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")])
        await kafka.start()

        pg = PgClient(os.getenv("POSTGRES_DSN", "postgresql://dwtads:dwtads@postgres:5432/dwtads"))
        await pg.start()

        neo4j = Neo4jClient(
            os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
            os.getenv("NEO4J_USER", "neo4j"),
            os.getenv("NEO4J_PASS", "dwtads"),
        )
        await neo4j.start()

        minio = MinioClient(
            os.getenv("MINIO_ENDPOINT", "minio:9000"),
            os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        )
    except Exception as e:
        print(f"[WARN] Infrastructure client init failed: {e} — degraded mode")

    # Instantiate and start all services
    svc_instances = []
    for cls in SERVICES:
        try:
            svc = cls(kafka=kafka, pg=pg, neo4j=neo4j, minio=minio)
            await svc.start()
            svc_instances.append(svc)
            app.state.services = svc_instances
        except Exception as e:
            print(f"[WARN] Service {cls.NAME} start failed: {e}")

    yield

    for svc in svc_instances:
        try:
            await svc.stop()
        except Exception:
            pass
    if kafka:
        await kafka.stop()
    if pg:
        await pg.stop()
    if neo4j:
        await neo4j.stop()


app = FastAPI(title="DW-TADS Plane 1 — Infrastructure", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok", "plane": 1, "name": "plane1-infrastructure"}


@app.get("/ready")
async def ready():
    svcs = getattr(app.state, "services", [])
    return {"status": "ready", "services_running": len(svcs), "plane": 1}


@app.get("/services")
async def list_services():
    svcs = getattr(app.state, "services", [])
    return {"count": len(svcs), "services": [s.NAME for s in svcs]}


@app.get("/metrics")
async def metrics():
    svcs = getattr(app.state, "services", [])
    lines = ["# HELP dwtads_messages_total Total messages processed",
             "# TYPE dwtads_messages_total counter"]
    for s in svcs:
        lines.append(f'dwtads_messages_total{{service="{s.NAME}",plane="1"}} {s.metrics_count}')
    return "\n".join(lines)


if __name__ == "__main__":
    port = int(os.getenv("PLANE_PORT", "8001"))
    uvicorn.run("plane_runner:app", host="0.0.0.0", port=port, reload=False)
