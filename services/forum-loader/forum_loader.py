"""Tier: A — Real. Algorithms: live fetch from VECERTUSA/DarkForumCTI GitHub repo,
parse darkforums_users.json structure, extract handle/platform/text tuples,
compute SHA-256 for deduplication."""
import hashlib
import json
from datetime import datetime, timezone
import httpx
import structlog
from common.base_service import BaseService, fetch_with_cache

logger = structlog.get_logger()

DARKFORUMCTI_USERS_URL = (
    "https://raw.githubusercontent.com/VECERTUSA/DarkForumCTI/"
    "main/darkforums_users.json"
)

def _parse_users(body: bytes) -> list[dict]:
    try:
        data = json.loads(body)
        if isinstance(data, list):
            return data
        return data.get("users", data.get("data", []))
    except Exception:
        return []

class ForumLoader(BaseService):
    NAME = "forum-loader"
    PLANE = 2
    TIER = "Foundation"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["crawl.raw", "actor.entities"]
    HTTP_PORT = 8029
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        forum_name = message["forum_name"] if "forum_name" in message else "unknown"
        max_users = int(message["max_users"]) if "max_users" in message else 100

        users = await fetch_with_cache(
            DARKFORUMCTI_USERS_URL, "darkforumcti", 720, _parse_users
        )
        if not users:
            logger.warning("forum_loader_no_data", forum=forum_name, correlation_id=cid)
            return []

        # Filter by forum name if specified
        if forum_name and forum_name.lower() != "all":
            users = [u for u in users
                     if forum_name.lower() in str(u.get("forum", "")).lower()
                     or forum_name.lower() in str(u.get("source", "")).lower()]

        users = users[:max_users]
        results = []
        for u in users:
            handle = str(u.get("username") or u.get("handle") or u.get("user_id") or "")
            if not handle:
                continue
            bio = str(u.get("bio") or u.get("description") or u.get("about") or "")
            post_count = int(u.get("post_count") or u.get("posts") or 0)
            joined = str(u.get("joined") or u.get("registered") or "")
            platform = str(u.get("forum") or u.get("source") or forum_name)

            uid = hashlib.sha256(f"{platform}:{handle}".encode()).hexdigest()
            results.append({
                "handle_id": uid[:16],
                "handle": handle,
                "platform": platform,
                "text": bio,
                "posted_at": joined or datetime.now(timezone.utc).isoformat(),
                "source_sha256": uid,
                "post_count": post_count,
                "correlation_id": cid,
            })

        logger.info("forum_loader_parsed", forum_name=forum_name, user_count=len(results),
                    correlation_id=cid)
        return results
