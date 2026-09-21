"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

CATEGORIES = {
    "drugs":       ["drug", "weed", "cocaine", "heroin", "mdma", "pill", "vendor", "gram", "oz"],
    "weapons":     ["gun", "firearm", "rifle", "pistol", "ammo", "suppressor", "weapon"],
    "hacking":     ["exploit", "vuln", "cve", "0day", "shellcode", "payload", "hack", "breach"],
    "fraud":       ["cc", "card", "dumps", "fullz", "cvv", "cloned", "bank", "wire", "paypal"],
    "ransomware":  ["ransom", "encrypt", "decrypt", "bitcoin", "victim", "data leak", "extort"],
    "marketplace": ["listing", "shop", "vendor", "buy", "price", "btc", "xmr", "escrow", "pgp"],
}

class CategoryClassifier(BaseService):
    NAME = "category-classifier"
    PLANE = 3
    TIER = "Intermediate"
    INPUT_TOPICS = ["content.clean"]
    OUTPUT_TOPICS = ["category.signals"]
    HTTP_PORT = 8042
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        text = message["text"] if "text" in message else ""
        handle_id = message["handle_id"] if "handle_id" in message else "anon"
        platform = message["platform"] if "platform" in message else "unknown"
        source_sha = message["source_sha256"] if "source_sha256" in message else ""

        if not text:
            return []

        text_lower = text.lower()
        word_count = max(len(text.split()), 1)
        normalize = max(word_count / 50.0, 1.0)

        scores = {}
        for cat, keywords in CATEGORIES.items():
            count = sum(text_lower.count(kw) for kw in keywords)
            scores[cat] = round(min(1.0, count / normalize), 4)

        total = sum(scores.values())
        if total > 0:
            norm_scores = {k: round(v / total, 4) for k, v in scores.items()}
        else:
            norm_scores = scores

        top_cat = max(norm_scores, key=norm_scores.get)
        top_score = norm_scores[top_cat]
        confidence = min(1.0, top_score * 2.5) if total > 0 else 0.0

        out = [{
            "handle_id": handle_id,
            "platform": platform,
            "source_sha256": source_sha,
            "category_scores": norm_scores,
            "top_category": top_cat,
            "top_score": round(top_score, 4),
            "confidence": round(confidence, 4),
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("category_classified", handle_id=handle_id, top=top_cat,
                    score=top_score, correlation_id=cid)
        return out
