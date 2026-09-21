"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import httpx
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

I2P_B32_RE = re.compile(r"[a-z2-7]{52}\.b32\.i2p")

class I2pCollector(BaseService):
    NAME = "i2p-collector"
    PLANE = 2
    TIER = "Advanced"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["crawl.raw"]
    HTTP_PORT = 8032
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        i2p_address = message["i2p_address"] if "i2p_address" in message else ""
        content = message["content"] if "content" in message else ""

        if not i2p_address:
            return []

        is_valid_b32 = bool(I2P_B32_RE.match(i2p_address))
        addr_hash = hashlib.sha256(i2p_address.encode()).hexdigest()

        if is_valid_b32:
            quality = "high"
        elif ".i2p" in i2p_address:
            quality = "medium"
        else:
            quality = "low"

        out = [{
            "target": i2p_address,
            "platform": "i2p",
            "raw_content": content or f"[i2p_collect:{addr_hash[:16]}]",
            "content_sha256": addr_hash,
            "address_quality": quality,
            "is_valid_b32": is_valid_b32,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("i2p_collected", address=i2p_address[:32], quality=quality,
                    correlation_id=cid)
        return out
