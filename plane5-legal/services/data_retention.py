"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone, timedelta
import structlog
from common.base_service import BaseService
logger = structlog.get_logger()
RETENTION_DAYS = {"evidence": 3650, "audit_log": 3650, "behavior_profile": 730,
                   "crawl_raw": 90, "threat_ioc": 365}
class DataRetention(BaseService):
    NAME = "data-retention"
    PLANE = 5
    TIER = "Intermediate"
    INPUT_TOPICS = ["audit.events"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8069
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]
    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        data_type = message.get("resource_type") or message.get("event_type") or "unknown"
        created_at = message.get("ts") or message.get("captured_at") or datetime.now(timezone.utc).isoformat()
        retention_days_key = next((k for k in RETENTION_DAYS if k in data_type.lower()), "crawl_raw")
        days = RETENTION_DAYS[retention_days_key]
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            expiry = (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt) + timedelta(days=days)
            is_expired = expiry < datetime.now(timezone.utc)
        except Exception:
            expiry = datetime.now(timezone.utc) + timedelta(days=days)
            is_expired = False
        out = [{"event_type": "retention_evaluated", "data_type": data_type,
                "retention_days": days, "expiry_date": expiry.isoformat(),
                "is_expired": is_expired, "action": "delete" if is_expired else "retain",
                "evaluated_at": datetime.now(timezone.utc).isoformat(), "correlation_id": cid}]
        logger.info("data_retention_evaluated", data_type=data_type, days=days,
                    expired=is_expired, correlation_id=cid)
        return out
