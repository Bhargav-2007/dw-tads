"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import httpx
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

ONION_V3_RE = re.compile(r"[a-z2-7]{56}\.onion")
ONION_V2_RE = re.compile(r"[a-z2-7]{16}\.onion")

class OnionCrawler(BaseService):
    NAME = "onion-crawler"
    PLANE = 2
    TIER = "Foundation"
    INPUT_TOPICS = ["onion.discovery"]
    OUTPUT_TOPICS = ["crawl.raw"]
    HTTP_PORT = 8023
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        onion_address = message["onion_address"] if "onion_address" in message else ""
        title = message["title"] if "title" in message else ""

        if not onion_address:
            return []

        # Classify onion address version
        if ONION_V3_RE.search(onion_address):
            version = "v3"
            confidence = 0.95
        elif ONION_V2_RE.search(onion_address):
            version = "v2"
            confidence = 0.70  # v2 deprecated
        else:
            version = "unknown"
            confidence = 0.3

        # Deterministic content hash from address (no fabricated body)
        crawl_hash = hashlib.sha256(onion_address.encode()).hexdigest()

        out = [{
            "target": onion_address,
            "title": title,
            "onion_version": version,
            "crawl_confidence": confidence,
            "raw_content": f"[crawl_pending:{onion_address[:32]}]",
            "content_sha256": crawl_hash,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "platform": "tor",
            "correlation_id": cid,
        }]
        logger.info("onion_crawled", onion=onion_address[:32], version=version,
                    confidence=confidence, correlation_id=cid)
        return out
