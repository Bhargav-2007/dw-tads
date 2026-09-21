"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService
logger = structlog.get_logger()
ALLOWED_ADMIN_ACTIONS = {"create_user", "delete_user", "change_role", "view_audit",
                          "export_report", "manage_retention", "manage_warrant"}
class AdminConsole(BaseService):
    NAME = "admin-console"
    PLANE = 7
    TIER = "Foundation"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8086
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]
    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        actor = message.get("actor") or "unknown"
        action = message.get("action") or ""
        target = message.get("target") or ""
        role = message.get("actor_role") or "analyst"
        if action not in ALLOWED_ADMIN_ACTIONS:
            return [{"event_type": "admin_action_rejected", "reason": "unknown_action",
                     "actor": actor, "action": action, "correlation_id": cid}]
        if role != "admin" and action in ("delete_user", "change_role", "manage_warrant"):
            return [{"event_type": "admin_action_rejected", "reason": "insufficient_role",
                     "actor": actor, "action": action, "correlation_id": cid}]
        op_hash = hashlib.sha256(f"{actor}:{action}:{target}:{cid}".encode()).hexdigest()[:12]
        out = [{"event_type": "admin_action_executed", "operation_hash": op_hash,
                "actor": actor, "action": action, "target": target,
                "role": role, "resource": target, "actor_user": actor,
                "executed_at": datetime.now(timezone.utc).isoformat(), "correlation_id": cid}]
        logger.info("admin_action_executed", actor=actor, action=action, hash=op_hash, correlation_id=cid)
        return out
