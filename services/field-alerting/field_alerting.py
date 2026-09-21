"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService
logger = structlog.get_logger()
ALERT_CHANNELS = {"critical": ["pager", "sms", "email", "siem"],
                   "high": ["email", "siem"], "medium": ["siem"], "low": []}
class FieldAlerting(BaseService):
    NAME = "field-alerting"
    PLANE = 6
    TIER = "Intermediate"
    INPUT_TOPICS = ["confidence.scores", "audit.events"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8079
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]
    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        subject_id = message.get("subject_id") or message.get("handle_id") or "unknown"
        tier = message.get("confidence_tier") or message.get("risk_level") or "low"
        score = float(message.get("confidence_score") or message.get("risk_score") or 0.0)
        channels = ALERT_CHANNELS.get(tier, [])
        if not channels:
            return []
        alert_id = hashlib.sha256(f"{subject_id}:{tier}:{cid}".encode()).hexdigest()[:12]
        out = [{"event_type": "field_alert", "alert_id": alert_id, "subject_id": subject_id,
                "confidence_tier": tier, "confidence_score": score,
                "alert_channels": channels, "action": "ALERT_DISPATCHED",
                "resource": alert_id, "actor_user": "field_alerting",
                "alerted_at": datetime.now(timezone.utc).isoformat(), "correlation_id": cid}]
        logger.info("field_alert_dispatched", subject=subject_id, tier=tier,
                    channels=channels, correlation_id=cid)
        return out
