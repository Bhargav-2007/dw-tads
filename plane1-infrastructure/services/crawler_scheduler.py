"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

PRIORITY_MAP = {
    "marketplace": 1,
    "ransomware": 1,
    "forum": 2,
    "drugs": 2,
    "hacking": 3,
    "general": 4,
}

class CrawlerScheduler(BaseService):
    NAME = "crawler-scheduler"
    PLANE = 1
    TIER = "Foundation"
    INPUT_TOPICS = ["onion.discovery"]
    OUTPUT_TOPICS = ["crawl.raw"]
    HTTP_PORT = 8012
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        onion = message["onion_address"] if "onion_address" in message else ""
        title = message["title"] if "title" in message else ""
        keyword = message["keyword"] if "keyword" in message else "general"

        if not onion or len(onion) < 10:
            logger.warning("crawler_scheduler_skip", reason="empty_onion", correlation_id=cid)
            return []

        priority = PRIORITY_MAP.get(keyword.lower(), PRIORITY_MAP["general"])
        title_lower = title.lower()
        if any(w in title_lower for w in ("market", "shop", "buy", "sell")):
            priority = min(priority, PRIORITY_MAP["marketplace"])
        if any(w in title_lower for w in ("ransomware", "ransom", "encrypt")):
            priority = min(priority, PRIORITY_MAP["ransomware"])

        crawl_id = hashlib.sha256(f"{onion}{cid}".encode()).hexdigest()[:16]

        out = [{
            "crawl_id": crawl_id,
            "target": onion,
            "title": title,
            "priority": priority,
            "keyword": keyword,
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("crawl_scheduled", onion=onion[:32], priority=priority, correlation_id=cid)
        return out
