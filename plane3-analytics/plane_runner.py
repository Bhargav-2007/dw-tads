"""Plane 3 runner (FastAPI + asynccontextmanager lifespan)."""
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
    try:
        from dwtds_common.kafka_client import KafkaProducer
        from dwtds_common.pg_client import PgClient
        from dwtds_common.neo4j_client import Neo4jClient
        from dwtds_common.minio_client import MinioClient
        kafka = KafkaProducer([os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")])
        await kafka.start()
        pg = PgClient(os.getenv("POSTGRES_DSN", "postgresql://dwtads:dwtads@postgres:5432/dwtads"))
        await pg.start()
        neo4j = Neo4jClient(os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
                            os.getenv("NEO4J_USER", "neo4j"),
                            os.getenv("NEO4J_PASS", "dwtads"))
        await neo4j.start()
        minio = MinioClient(os.getenv("MINIO_ENDPOINT", "minio:9000"),
                            os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
                            os.getenv("MINIO_SECRET_KEY", "minioadmin"))
    except Exception as e:
        print(f"[WARN] Infrastructure init: {e} — degraded mode")

    svc_instances = []
    for cls in SERVICES:
        try:
            svc = cls(kafka=kafka, pg=pg, neo4j=neo4j, minio=minio)
            await svc.start()
            svc_instances.append(svc)
        except Exception as e:
            print(f"[WARN] Service {getattr(cls, 'NAME', cls.__name__)} start failed: {e}")
    app.state.services = svc_instances

    yield

    for svc in svc_instances:
        try:
            await svc.stop()
        except Exception:
            pass
    for client in [kafka, pg, neo4j]:
        if client:
            try:
                await client.stop()
            except Exception:
                pass


app = FastAPI(title="DW-TADS Plane 3 — Analytics", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok", "plane": 3, "name": "plane3-analytics"}


@app.get("/ready")
async def ready():
    svcs = getattr(app.state, "services", [])
    return {"status": "ready", "services_running": len(svcs), "plane": 3}


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
        lines.append(
            f'dwtads_messages_total{service="{s.NAME}",plane="3"} {s.metrics_count}'
        )
    return "\n".join(lines)


if __name__ == "__main__":
    port = int(os.getenv("PLANE_PORT", "8003"))
    uvicorn.run("plane_runner:app", host="0.0.0.0", port=port, reload=False)
