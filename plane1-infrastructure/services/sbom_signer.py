"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

ALLOWED_FORMATS = {"cyclonedx", "spdx", "swid"}

class SbomSigner(BaseService):
    NAME = "sbom-signer"
    PLANE = 1
    TIER = "Advanced"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8022
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        service_name = message["service_name"] if "service_name" in message else ""
        sbom_format = message["sbom_format"] if "sbom_format" in message else "cyclonedx"
        component_count = int(message["component_count"]) if "component_count" in message else 0

        if not service_name:
            return []

        if sbom_format not in ALLOWED_FORMATS:
            status = "format_rejected"
            signature = ""
        elif component_count == 0:
            status = "empty_sbom"
            signature = ""
        else:
            status = "signed"
            sbom_hash = hashlib.sha256(
                f"{service_name}:{sbom_format}:{component_count}:{cid}".encode()
            ).hexdigest()
            signature = hashlib.sha256(sbom_hash.encode()).hexdigest()

        out = [{
            "event_type": "sbom_signed",
            "service_name": service_name,
            "sbom_format": sbom_format,
            "component_count": component_count,
            "status": status,
            "signature": signature,
            "signed_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("sbom_signed", service=service_name, format=sbom_format,
                    status=status, components=component_count, correlation_id=cid)
        return out
