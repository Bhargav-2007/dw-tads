"""Tier: B — Honest stub. Reads message, applies real logic."""
import re
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService
logger = structlog.get_logger()
class TemporalReasoner(BaseService):
    NAME = "temporal-reasoner"
    PLANE = 4
    TIER = "Intermediate"
    INPUT_TOPICS = ["content.clean"]
    OUTPUT_TOPICS = ["confidence.scores"]
    HTTP_PORT = 8057
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]
    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        posted_at = message.get("posted_at") or datetime.now(timezone.utc).isoformat()
        handle_id = message.get("handle_id") or "anon"
        try:
            dt = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age_days = (now - dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else now - dt).days
        except Exception:
            age_days = 0
        recency_score = max(0.0, 1.0 - age_days / 365.0)
        if age_days == 0: urgency = "immediate"
        elif age_days < 7: urgency = "recent"
        elif age_days < 30: urgency = "current"
        elif age_days < 90: urgency = "aging"
        else: urgency = "historical"
        out = [{"subject_id": handle_id, "confidence_score": round(recency_score, 4),
                "confidence_tier": "high" if recency_score > 0.8 else "medium" if recency_score > 0.4 else "low",
                "signals": {"recency_score": round(recency_score, 4), "age_days": age_days},
                "n_signals": 2, "signal_coverage": 0.4, "urgency": urgency,
                "raw_score": round(recency_score, 4), "calibrated_score": round(recency_score, 4),
                "scored_at": datetime.now(timezone.utc).isoformat(), "correlation_id": cid}]
        logger.info("temporal_reasoned", handle=handle_id, age_days=age_days, urgency=urgency, correlation_id=cid)
        return out
