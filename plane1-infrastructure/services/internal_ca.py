"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

class InternalCa(BaseService):
    NAME = "internal-ca"
    PLANE = 1
    TIER = "Foundation"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8015
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        service_name = message["service_name"] if "service_name" in message else ""
        action = message["action"] if "action" in message else "sign"

        if not service_name:
            return []

        cert_fingerprint = hashlib.sha256(
            f"{service_name}:{action}:{cid}".encode()
        ).hexdigest()

        if action == "sign":
            status = "cert_issued"
            validity_days = 365
        elif action == "revoke":
            status = "cert_revoked"
            validity_days = 0
        else:
            status = "cert_renewed"
            validity_days = 180

        out = [{
            "event_type": "ca_operation",
            "service_name": service_name,
            "action": action,
            "status": status,
            "cert_fingerprint": cert_fingerprint,
            "validity_days": validity_days,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("internal_ca_op", service_name=service_name, action=action,
                    status=status, correlation_id=cid)
        return out
