"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import httpx
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

BTC_ADDR_RE = re.compile(r"^[13][a-zA-Z0-9]{25,34}$")

class ZeronetCollector(BaseService):
    NAME = "zeronet-collector"
    PLANE = 2
    TIER = "Advanced"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["crawl.raw"]
    HTTP_PORT = 8033
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        site_address = message["site_address"] if "site_address" in message else ""
        content = message["content"] if "content" in message else ""

        if not site_address:
            return []

        # ZeroNet sites use Bitcoin addresses as identifiers
        is_valid_btc = bool(BTC_ADDR_RE.match(site_address))
        addr_hash = hashlib.sha256(site_address.encode()).hexdigest()

        if is_valid_btc:
            platform_confidence = 0.95
        elif len(site_address) > 20:
            platform_confidence = 0.60
        else:
            platform_confidence = 0.30

        out = [{
            "target": f"zeronet:{site_address}",
            "platform": "zeronet",
            "site_address": site_address,
            "raw_content": content or f"[zeronet_collect:{addr_hash[:16]}]",
            "content_sha256": addr_hash,
            "is_valid_btc_addr": is_valid_btc,
            "platform_confidence": platform_confidence,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("zeronet_collected", site=site_address[:32],
                    confidence=platform_confidence, correlation_id=cid)
        return out
