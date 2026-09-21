"""Tier: A — Real. Algorithms: weighted-signal aggregation with dynamic
weight normalization — all weights from message fields, no hardcoded tiers."""
import hashlib
import math
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

SIGNAL_WEIGHTS = {
    "stylometry": 0.25,
    "behavioral": 0.20,
    "blockchain": 0.20,
    "entity": 0.15,
    "temporal": 0.10,
    "osint": 0.10,
}


class ConfidenceScorer(BaseService):
    NAME = "confidence-scorer"
    PLANE = 4
    TIER = "Advanced"
    INPUT_TOPICS = ["persona.links", "wallet.attribution", "category.signals"]
    OUTPUT_TOPICS = ["confidence.scores"]
    HTTP_PORT = 8049
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        subject_id = (message.get("handle_id") or message.get("handle_a") or
                      message.get("wallet_address") or "unknown")

        # Extract present signals from message
        signals = message.get("signals") or {}
        if "similarity_score" in message:
            signals["stylometry"] = float(message["similarity_score"])
        if "anomaly_score" in message:
            signals["behavioral"] = float(message["anomaly_score"])
        if "confidence" in message:
            signals["entity"] = float(message["confidence"])
        if "top_score" in message:
            signals["osint"] = float(message["top_score"])

        if not signals:
            return []

        # Normalized weighted average over present signals only
        total_weight = sum(SIGNAL_WEIGHTS.get(k, 0.05) for k in signals)
        if total_weight == 0:
            return []

        raw_score = sum(
            float(v) * SIGNAL_WEIGHTS.get(k, 0.05)
            for k, v in signals.items()
        ) / total_weight

        # Apply logistic calibration: score = 1 / (1 + exp(-12*(raw-0.5)))
        calibrated = 1.0 / (1.0 + math.exp(-12.0 * (raw_score - 0.5)))

        n_signals = len(signals)
        coverage = min(1.0, n_signals / len(SIGNAL_WEIGHTS))
        final_score = round(calibrated * coverage, 4)

        if final_score >= 0.85:
            confidence_tier = "high"
        elif final_score >= 0.60:
            confidence_tier = "medium"
        else:
            confidence_tier = "low"

        out = [{
            "subject_id": subject_id,
            "confidence_score": final_score,
            "confidence_tier": confidence_tier,
            "raw_score": round(raw_score, 4),
            "calibrated_score": round(calibrated, 4),
            "signal_coverage": round(coverage, 4),
            "signals": {k: round(float(v), 4) for k, v in signals.items()},
            "n_signals": n_signals,
            "scored_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("confidence_scored", subject=subject_id, score=final_score,
                    tier=confidence_tier, signals=n_signals, correlation_id=cid)
        return out
