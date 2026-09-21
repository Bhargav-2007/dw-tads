"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import httpx
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

FORUM_INDICATORS = ["board", "thread", "post", "topic", "reply", "user", "profile"]

class ForumCrawler(BaseService):
    NAME = "forum-crawler"
    PLANE = 2
    TIER = "Foundation"
    INPUT_TOPICS = ["onion.discovery"]
    OUTPUT_TOPICS = ["crawl.raw"]
    HTTP_PORT = 8024
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        onion_address = message["onion_address"] if "onion_address" in message else ""
        title = message["title"] if "title" in message else ""

        if not onion_address:
            return []

        title_lower = title.lower()
        forum_score = sum(1 for ind in FORUM_INDICATORS if ind in title_lower)

        if forum_score >= 3:
            platform_type = "forum"
            crawl_depth = 3
        elif forum_score >= 1:
            platform_type = "forum_possible"
            crawl_depth = 2
        else:
            platform_type = "unknown"
            crawl_depth = 1

        crawl_id = hashlib.sha256(f"{onion_address}:forum:{cid}".encode()).hexdigest()[:16]

        out = [{
            "target": onion_address,
            "title": title,
            "platform_type": platform_type,
            "forum_score": forum_score,
            "crawl_depth": crawl_depth,
            "crawl_id": crawl_id,
            "raw_content": f"[forum_crawl:{crawl_id}]",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "platform": "tor",
            "correlation_id": cid,
        }]
        logger.info("forum_crawled", onion=onion_address[:32], platform=platform_type,
                    score=forum_score, correlation_id=cid)
        return out
