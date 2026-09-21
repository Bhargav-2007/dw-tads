"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import httpx
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

CHANNEL_RE = re.compile(r"@([a-zA-Z][a-zA-Z0-9_]{3,30})")

class TelegramOsint(BaseService):
    NAME = "telegram-osint"
    PLANE = 2
    TIER = "Advanced"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["crawl.raw"]
    HTTP_PORT = 8034
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        channel = message["channel"] if "channel" in message else ""
        message_text = message["message_text"] if "message_text" in message else ""
        message_id = int(message["message_id"]) if "message_id" in message else 0

        if not channel:
            return []

        # Classify channel risk from channel name patterns
        channel_lower = channel.lower()
        if any(kw in channel_lower for kw in ("leak", "hack", "darkweb", "crypt", "ransom")):
            risk_level = "high"
        elif any(kw in channel_lower for kw in ("anon", "priv", "vpn", "tor")):
            risk_level = "medium"
        else:
            risk_level = "low"

        # Extract mentioned channels
        mentions = CHANNEL_RE.findall(message_text)
        content_hash = hashlib.sha256(f"{channel}:{message_id}:{message_text}".encode()).hexdigest()

        out = [{
            "target": f"telegram:{channel}",
            "platform": "telegram",
            "channel": channel,
            "message_id": message_id,
            "risk_level": risk_level,
            "mentioned_channels": mentions,
            "raw_content": message_text,
            "content_sha256": content_hash,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("telegram_osint_collected", channel=channel, risk=risk_level,
                    mentions=len(mentions), correlation_id=cid)
        return out
