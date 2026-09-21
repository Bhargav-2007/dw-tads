"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

CASE_PRIORITIES = {"critical": 1, "high": 2, "medium": 3, "low": 4}

class CaseManager(BaseService):
    NAME = "case-manager"
    PLANE = 6
    TIER = "Foundation"
    INPUT_TOPICS = ["confidence.scores"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8072
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        subject_id = message.get("subject_id") or "unknown"
        score = float(message.get("confidence_score") or 0.0)
        tier = message.get("confidence_tier") or "low"

        case_priority = tier if tier in CASE_PRIORITIES else "low"
        case_id = hashlib.sha256(f"{subject_id}:{cid}".encode()).hexdigest()[:12]

        assigned_to = {
            "critical": "senior_analyst",
            "high": "senior_analyst",
            "medium": "analyst",
            "low": "analyst",
        }.get(case_priority, "analyst")

        out = [{
            "event_type": "case_created",
            "case_id": case_id,
            "subject_id": subject_id,
            "confidence_score": score,
            "case_priority": case_priority,
            "assigned_to": assigned_to,
            "action": "CASE_OPENED",
            "resource": case_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("case_opened", case_id=case_id, priority=case_priority,
                    assigned=assigned_to, correlation_id=cid)
        return out
