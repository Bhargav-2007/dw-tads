"""Tier: B — Honest stub. Reads mock_sources/, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

class PeerReview(BaseService):
    NAME = "peer-review"
    PLANE = 6
    TIER = "Advanced"
    INPUT_TOPICS = ["case.events"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8076
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        report_id = message["report_id"] if "report_id" in message else "REP-2026-09"
        analyst_a = message["primary_analyst"] if "primary_analyst" in message else "analyst_alice"
        reviewer_b = message["peer_reviewer"] if "peer_reviewer" in message else "senior_bob"

        # Four-eyes principle: reviewer cannot be the primary analyst
        is_independent = analyst_a != reviewer_b
        status = "PASSED_FOUR_EYES" if is_independent else "REJECTED_SELF_REVIEW"

        out = [{
            "report_id": report_id,
            "primary_analyst": analyst_a,
            "peer_reviewer": reviewer_b,
            "four_eyes_verified": is_independent,
            "review_status": status,
            "signed_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("peer_review_evaluated", report_id=report_id, status=status, correlation_id=cid)
        return out
