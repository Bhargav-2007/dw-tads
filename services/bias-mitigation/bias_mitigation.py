"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService
logger = structlog.get_logger()
PROTECTED_GROUPS = {"religion", "nationality", "race", "gender", "sexuality", "ethnicity"}
BIAS_TERMS = {
    "religion": ["christian", "muslim", "jewish", "hindu", "atheist"],
    "nationality": ["american", "chinese", "russian", "iranian", "north korean"],
    "race": ["black", "white", "asian", "latino", "arab"],
}
class BiasMitigation(BaseService):
    NAME = "bias-mitigation"
    PLANE = 4
    TIER = "Intermediate"
    INPUT_TOPICS = ["category.signals"]
    OUTPUT_TOPICS = ["confidence.scores"]
    HTTP_PORT = 8055
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]
    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        confidence = float(message.get("confidence") or 0.5)
        subject_id = message.get("subject_id") or message.get("handle_id") or "unknown"
        top_category = message.get("top_category") or ""
        signals = message.get("signals") or {}
        bias_detected = {}
        for grp, terms in BIAS_TERMS.items():
            hits = [t for t in terms if t in top_category.lower() or t in str(signals).lower()]
            if hits: bias_detected[grp] = hits
        penalty = min(0.20, len(bias_detected) * 0.05)
        adjusted = round(max(0.0, confidence - penalty), 4)
        out = [{"subject_id": subject_id, "confidence_score": adjusted,
                "confidence_tier": "high" if adjusted > 0.8 else "medium" if adjusted > 0.5 else "low",
                "signals": signals, "n_signals": len(signals), "signal_coverage": 0.5,
                "raw_score": confidence, "calibrated_score": adjusted,
                "bias_detected": bias_detected, "penalty": round(penalty, 4),
                "scored_at": datetime.now(timezone.utc).isoformat(), "correlation_id": cid}]
        logger.info("bias_mitigated", subject=subject_id, penalty=penalty, correlation_id=cid)
        return out
