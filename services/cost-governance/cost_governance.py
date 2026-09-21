"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

RESOURCE_COSTS = {
    "kafka_message": 0.000001,
    "postgres_query": 0.0001,
    "neo4j_query": 0.0002,
    "minio_put": 0.00005,
    "http_fetch": 0.001,
    "ml_inference": 0.01,
}

class CostGovernance(BaseService):
    NAME = "cost-governance"
    PLANE = 1
    TIER = "Intermediate"
    INPUT_TOPICS = ["audit.events"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8021
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        service_name = message["service_name"] if "service_name" in message else "unknown"
        resource_type = message["resource_type"] if "resource_type" in message else "kafka_message"
        usage_count = int(message["usage_count"]) if "usage_count" in message else 1

        unit_cost = RESOURCE_COSTS.get(resource_type, 0.0001)
        total_cost = unit_cost * usage_count
        alert = total_cost > 1.0

        out = [{
            "event_type": "cost_governance_report",
            "service_name": service_name,
            "resource_type": resource_type,
            "usage_count": usage_count,
            "unit_cost_usd": unit_cost,
            "total_cost_usd": round(total_cost, 6),
            "budget_alert": alert,
            "period": datetime.now(timezone.utc).strftime("%Y-%m"),
            "correlation_id": cid,
        }]
        logger.info("cost_governance_evaluated", service=service_name, resource=resource_type,
                    total=round(total_cost, 6), alert=alert, correlation_id=cid)
        return out
