"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService
logger = structlog.get_logger()
class OversightAuditLog(BaseService):
    NAME = "oversight-audit-log"
    PLANE = 5
    TIER = "Intermediate"
    INPUT_TOPICS = ["audit.events"]
    OUTPUT_TOPICS = []
    HTTP_PORT = 8070
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]
    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        event_type = message.get("event_type") or "unknown"
        actor = message.get("actor_user") or "system"
        resource = message.get("resource") or ""
        review_hash = hashlib.sha256(f"{event_type}:{actor}:{resource}:{cid}".encode()).hexdigest()
        if self.pg is not None:
            try:
                await self.pg.write_audit(event_type=event_type, actor_user=actor,
                                           action="OVERSIGHT_LOG", resource=resource,
                                           metadata={"review_hash": review_hash, "cid": cid})
            except Exception as e:
                logger.warning("oversight_audit_log_pg_error", error=str(e), correlation_id=cid)
        logger.info("oversight_audit_logged", event=event_type, actor=actor,
                    review_hash=review_hash[:16], correlation_id=cid)
        return []
