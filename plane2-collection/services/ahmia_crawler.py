"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import httpx
import structlog
from common.base_service import BaseService, fetch_with_cache

logger = structlog.get_logger()

ONION_RE = re.compile(r"\b([a-z2-7]{56}\.onion|[a-z2-7]{16}\.onion)\b")

def _parse_body(body: bytes) -> list[str]:
    html = body.decode("utf-8", errors="replace")
    return list(set(ONION_RE.findall(html)))

class AhmiaCrawler(BaseService):
    NAME = "ahmia-crawler"
    PLANE = 2
    TIER = "Advanced"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["onion.discovery"]
    HTTP_PORT = 8027
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        query = message["query"] if "query" in message else "market"

        safe_q = re.sub(r"[^a-zA-Z0-9_-]", "", query)
        if not safe_q:
            return []

        from urllib.parse import quote
        url = f"https://ahmia.fi/search/?q={quote(safe_q)}"
        onions = await fetch_with_cache(url, "ahmia", 168, _parse_body)

        if not onions:
            logger.warning("ahmia_crawler_no_results", query=safe_q, correlation_id=cid)
            return []

        out = [{
            "onion_address": onion,
            "title": "",
            "keyword": safe_q,
            "source_url": url,
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        } for onion in onions]

        logger.info("ahmia_crawled", query=safe_q, count=len(out), correlation_id=cid)
        return out
