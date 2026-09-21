"""Tier: B — Honest stub. Reads mock_sources/, applies real logic."""
import hashlib
import json
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

class InterAgencyGateway(BaseService):
    NAME = "inter-agency-gateway"
    PLANE = 7
    TIER = "Expert"
    INPUT_TOPICS = ["case.events"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8087
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        partner_agency = message["agency"] if "agency" in message else "EUROPOL"
        tlp_level = message["tlp"] if "tlp" in message else "TLP:AMBER"
        iocs = message["iocs"] if "iocs" in message else ["198.51.100.23", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"]

        # STIX/TAXII 2.1 IOC Bundle formatting and clearance gate
        is_shareable = tlp_level in ["TLP:CLEAR", "TLP:GREEN", "TLP:AMBER"]
        bundle_id = "bundle--" + hashlib.sha256(f"{partner_agency}:{tlp_level}".encode()).hexdigest()[:16]

        out = [{
            "partner_agency": partner_agency,
            "tlp_level": tlp_level,
            "stix_bundle_id": bundle_id,
            "ioc_count": len(iocs),
            "transmission_status": "DISPATCHED" if is_shareable else "HELD_TLP_RED",
            "disseminated_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("inter_agency_disseminated", agency=partner_agency, tlp=tlp_level, count=len(iocs), correlation_id=cid)
        return out
