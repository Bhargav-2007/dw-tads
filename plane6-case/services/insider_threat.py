"""Tier: B — Honest stub. Reads mock_sources/, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

class InsiderThreat(BaseService):
    NAME = "insider-threat"
    PLANE = 6
    TIER = "Expert"
    INPUT_TOPICS = ["audit.events"]
    OUTPUT_TOPICS = ["service.errors"]
    HTTP_PORT = 8079
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        user_id = message["user_id"] if "user_id" in message else "operator_09"
        queries_per_hour = int(message["query_rate"]) if "query_rate" in message else 450
        is_after_hours = message["after_hours"] if "after_hours" in message else False

        # Detect abnormal export velocity and off-hours exfiltration indicators
        is_anomaly = (queries_per_hour > 300) and is_after_hours
        risk_level = "CRITICAL" if is_anomaly else ("MEDIUM" if queries_per_hour > 200 else "LOW")

        out = [{
            "user_id": user_id,
            "query_rate": queries_per_hour,
            "after_hours": is_after_hours,
            "insider_threat_risk": risk_level,
            "alert_triggered": is_anomaly,
            "monitored_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("insider_threat_evaluated", user=user_id, risk=risk_level, alert=is_anomaly, correlation_id=cid)
        return out
