"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import httpx
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

MARKET_KEYWORDS = ["shop", "vendor", "listing", "buy", "price", "bitcoin", "monero", "escrow", "pgp"]

class MarketplaceCrawler(BaseService):
    NAME = "marketplace-crawler"
    PLANE = 2
    TIER = "Foundation"
    INPUT_TOPICS = ["onion.discovery"]
    OUTPUT_TOPICS = ["crawl.raw"]
    HTTP_PORT = 8025
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        onion_address = message["onion_address"] if "onion_address" in message else ""
        title = message["title"] if "title" in message else ""
        keyword = message["keyword"] if "keyword" in message else ""

        if not onion_address:
            return []

        combined = f"{title} {keyword}".lower()
        market_score = sum(1 for kw in MARKET_KEYWORDS if kw in combined)

        if market_score >= 4:
            category = "high_confidence_market"
            priority = 1
        elif market_score >= 2:
            category = "possible_market"
            priority = 2
        else:
            category = "general"
            priority = 3

        crawl_id = hashlib.sha256(f"{onion_address}:market:{cid}".encode()).hexdigest()[:16]

        out = [{
            "target": onion_address,
            "title": title,
            "category": category,
            "market_score": market_score,
            "priority": priority,
            "crawl_id": crawl_id,
            "raw_content": f"[market_crawl:{crawl_id}]",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "platform": "tor",
            "correlation_id": cid,
        }]
        logger.info("marketplace_crawled", onion=onion_address[:32], category=category,
                    priority=priority, correlation_id=cid)
        return out
