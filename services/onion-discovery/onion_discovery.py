"""Tier: A — Real. Algorithms: cache-first HTTP fetch from Ahmia search index,
RFC-compliant v3 onion regex extraction ([a-z2-7]{56}\.onion),
in-memory deduplication via sha256 seen-set."""
import re
import hashlib
from datetime import datetime, timezone
import httpx
import structlog
from common.base_service import BaseService, fetch_with_cache

logger = structlog.get_logger()

ONION_V3_RE = re.compile(r"\b([a-z2-7]{56}\.onion)\b")
ONION_V2_RE = re.compile(r"\b([a-z2-7]{16}\.onion)\b")

def _parse_ahmia_html(body: bytes) -> list[dict]:
    """Extract .onion addresses and titles from Ahmia search result HTML."""
    html = body.decode("utf-8", errors="replace")
    results = []
    # Extract result blocks: <li class="result">
    blocks = re.findall(
        r'<li[^>]+class="result"[^>]*>(.*?)</li>',
        html, re.DOTALL | re.IGNORECASE
    )
    for block in blocks:
        # Title from <h4> or <a>
        title_m = re.search(r'<h4[^>]*>(.*?)</h4>', block, re.DOTALL | re.IGNORECASE)
        title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else ""
        # .onion address from href or cite
        addr_m = ONION_V3_RE.search(block) or ONION_V2_RE.search(block)
        if addr_m:
            results.append({"onion": addr_m.group(1), "title": title})
    return results


class OnionDiscovery(BaseService):
    NAME = "onion-discovery"
    PLANE = 2
    TIER = "Foundation"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["onion.discovery"]
    HTTP_PORT = 8026
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._seen: set[str] = set()

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        keyword = message["keyword"] if "keyword" in message else "market"

        from urllib.parse import quote
        url = f"https://ahmia.fi/search/?q={quote(keyword)}"

        raw = await fetch_with_cache(url, "ahmia", 168, lambda b: b)
        if raw is None:
            logger.warning("onion_discovery_no_data", keyword=keyword, correlation_id=cid)
            return []

        parsed = _parse_ahmia_html(raw)

        results = []
        for item in parsed:
            onion = item["onion"]
            addr_hash = hashlib.sha256(onion.encode()).hexdigest()
            if addr_hash in self._seen:
                continue
            self._seen.add(addr_hash)
            results.append({
                "onion_address": onion,
                "title": item.get("title", ""),
                "keyword": keyword,
                "source_url": url,
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "correlation_id": cid,
            })

        logger.info("onion_discovery_completed", keyword=keyword, count=len(results),
                    correlation_id=cid)
        return results
