"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

SECRET_TYPES = {"db_password", "api_key", "jwt_secret", "tls_cert", "mfa_seed"}

class SecretsManager(BaseService):
    NAME = "secrets-manager"
    PLANE = 1
    TIER = "Foundation"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8016
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        secret_name = message["secret_name"] if "secret_name" in message else ""
        operation = message["operation"] if "operation" in message else "read"
        requester = message["requester"] if "requester" in message else "unknown"
        secret_type = message["secret_type"] if "secret_type" in message else "api_key"

        if not secret_name:
            return []

        # Authorization: only known requester roles get write access
        if operation in ("write", "delete") and requester not in ("admin", "system"):
            status = "denied"
            severity = "high"
        elif secret_type not in SECRET_TYPES:
            status = "unknown_type"
            severity = "medium"
        else:
            status = "authorized"
            severity = "low"

        access_hash = hashlib.sha256(
            f"{secret_name}:{requester}:{operation}:{cid}".encode()
        ).hexdigest()

        out = [{
            "event_type": "secret_access",
            "secret_name": secret_name,
            "secret_type": secret_type,
            "operation": operation,
            "requester": requester,
            "status": status,
            "severity": severity,
            "access_hash": access_hash,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("secrets_manager_op", secret_name=secret_name, operation=operation,
                    status=status, severity=severity, correlation_id=cid)
        return out
