"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import math
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()


class ModelDriftMonitor(BaseService):
    NAME = "model-drift-monitor"
    PLANE = 3
    TIER = "Advanced"
    INPUT_TOPICS = ["behavior.profile"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8046
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model_scores: dict = {}

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        model_name = message["model_name"] if "model_name" in message else "default"
        current_score = float(message["anomaly_score"]) if "anomaly_score" in message else 0.0

        prev_scores = self._model_scores.setdefault(model_name, [])
        prev_scores.append(current_score)

        if len(prev_scores) < 2:
            drift = 0.0
            drift_alert = False
        else:
            # PSI-like drift: mean absolute deviation from previous mean
            prev_mean = sum(prev_scores[:-1]) / len(prev_scores[:-1])
            drift = abs(current_score - prev_mean)
            drift_alert = drift > 0.15  # 15% drift threshold

        if len(prev_scores) > 100:
            prev_scores.pop(0)

        out = [{
            "event_type": "model_drift_report",
            "model_name": model_name,
            "current_score": round(current_score, 4),
            "drift": round(drift, 4),
            "drift_alert": drift_alert,
            "samples": len(prev_scores),
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("model_drift_checked", model=model_name, drift=round(drift, 4),
                    alert=drift_alert, correlation_id=cid)
        return out
