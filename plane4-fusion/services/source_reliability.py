"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib, math
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService
logger = structlog.get_logger()
class SourceReliability(BaseService):
    NAME = "source-reliability"
    PLANE = 4
    TIER = "Intermediate"
    INPUT_TOPICS = ["crawl.raw"]
    OUTPUT_TOPICS = ["confidence.scores"]
    HTTP_PORT = 8054
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._history: dict = {}
    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        source_url = message["target"] if "target" in message else ""
        content_len = len(str(message.get("raw_content") or ""))
        is_reachable = content_len > 0
        h = self._history.setdefault(source_url, {"ok": 0, "fail": 0})
        if is_reachable: h["ok"] += 1
        else: h["fail"] += 1
        total = h["ok"] + h["fail"]
        success_rate = h["ok"] / total if total else 0.5
        reliability = round(success_rate * min(1.0, math.log1p(total) / math.log1p(10)), 4)
        out = [{"subject_id": source_url, "confidence_score": reliability,
                "confidence_tier": "high" if reliability > 0.8 else "medium" if reliability > 0.5 else "low",
                "signals": {"success_rate": round(success_rate, 4), "total_fetches": total,
                            "content_length": content_len},
                "n_signals": 3, "signal_coverage": 0.6,
                "raw_score": reliability, "calibrated_score": reliability,
                "scored_at": datetime.now(timezone.utc).isoformat(), "correlation_id": cid}]
        logger.info("source_reliability_scored", url=source_url[:32], reliability=reliability, correlation_id=cid)
        return out
