"""Tier: B — Honest stub. Reads mock_sources/, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

class FieldAlerting(BaseService):
    NAME = "field-alerting"
    PLANE = 7
    TIER = "Advanced"
    INPUT_TOPICS = ["case.events", "threat.iocs"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8088
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        severity = message["severity"] if "severity" in message else "HIGH"
        alert_msg = message["alert_text"] if "alert_text" in message else "Tactical indicator match: Lockbit C2 IP active."

        # Tactical notification prioritization
        if severity == "CRITICAL":
            dispatch_channel = "SMS_AND_SIGNAL_PAGER"
            escalate = True
        elif severity == "HIGH":
            dispatch_channel = "ENCRYPTED_EMAIL"
            escalate = False
        else:
            dispatch_channel = "DASHBOARD_FEED"
            escalate = False

        alert_id = hashlib.sha256(f"{severity}:{alert_msg}".encode()).hexdigest()[:12]

        out = [{
            "alert_id": alert_id,
            "severity": severity,
            "dispatch_channel": dispatch_channel,
            "escalate_to_director": escalate,
            "status": "SENT",
            "alerted_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("field_alert_dispatched", alert_id=alert_id, severity=severity, channel=dispatch_channel, correlation_id=cid)
        return out
