"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService
logger = structlog.get_logger()
class ExplainabilityEngine(BaseService):
    NAME = "explainability-engine"
    PLANE = 4
    TIER = "Advanced"
    INPUT_TOPICS = ["confidence.scores"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8056
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]
    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        subject_id = message.get("subject_id") or "unknown"
        confidence = float(message.get("confidence_score") or 0.0)
        signals = message.get("signals") or {}
        tier = message.get("confidence_tier") or "low"
        sorted_signals = sorted(signals.items(), key=lambda x: abs(x[1]), reverse=True)
        top_factors = [{"signal": k, "contribution": round(float(v), 4), "direction": "positive" if float(v) > 0.5 else "negative"}
                       for k, v in sorted_signals[:5]]
        narrative = (f"Confidence {tier} ({confidence:.2f}) based on {len(signals)} signals. "
                     f"Top driver: {top_factors[0]['signal'] if top_factors else 'none'}.")
        out = [{"event_type": "explanation_generated", "subject_id": subject_id,
                "confidence_score": confidence, "confidence_tier": tier,
                "top_factors": top_factors, "narrative": narrative,
                "explanation_hash": hashlib.sha256(narrative.encode()).hexdigest()[:16],
                "generated_at": datetime.now(timezone.utc).isoformat(), "correlation_id": cid}]
        logger.info("explanation_generated", subject=subject_id, tier=tier, correlation_id=cid)
        return out
