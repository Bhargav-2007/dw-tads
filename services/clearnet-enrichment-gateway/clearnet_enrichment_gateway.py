"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import httpx
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

IPV4_RE = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)

class ClearnetEnrichmentGateway(BaseService):
    NAME = "clearnet-enrichment-gateway"
    PLANE = 2
    TIER = "Foundation"
    INPUT_TOPICS = ["infra.indicators"]
    OUTPUT_TOPICS = ["infra.indicators"]
    HTTP_PORT = 8035
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        onion_address = message["onion_address"] if "onion_address" in message else ""
        finding_type = message["finding_type"] if "finding_type" in message else "unknown"
        matched_ip = message["matched_clearnet_ip"] if "matched_clearnet_ip" in message else ""
        matched_domain = message["matched_clearnet_domain"] if "matched_clearnet_domain" in message else ""

        if not onion_address:
            return []

        # Validate and classify IP if present
        ip_valid = bool(matched_ip and IPV4_RE.match(matched_ip))
        if matched_domain and matched_domain.endswith(".onion"):
            domain_valid = False
        elif matched_domain and "." in matched_domain:
            domain_valid = True
        else:
            domain_valid = False

        if ip_valid and domain_valid:
            confidence = 0.95
            enrichment_type = "ip_and_domain"
        elif ip_valid:
            confidence = 0.80
            enrichment_type = "ip_only"
        elif domain_valid:
            confidence = 0.70
            enrichment_type = "domain_only"
        else:
            confidence = 0.40
            enrichment_type = "no_clearnet_match"

        out = [{
            "onion_address": onion_address,
            "finding_type": finding_type,
            "confidence": confidence,
            "matched_clearnet_ip": matched_ip if ip_valid else None,
            "matched_clearnet_domain": matched_domain if domain_valid else None,
            "match_type": enrichment_type,
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("clearnet_enriched", onion=onion_address[:32], enrichment=enrichment_type,
                    confidence=confidence, correlation_id=cid)
        return out
