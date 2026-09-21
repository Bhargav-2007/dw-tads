"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService
logger = structlog.get_logger()
INSIDER_SIGNALS = ["off_hours_access", "bulk_download", "privilege_escalation",
                   "anomalous_query", "data_exfiltration", "vpn_usage", "encrypted_channel"]
class InsiderThreat(BaseService):
    NAME = "insider-threat"
    PLANE = 4
    TIER = "Advanced"
    INPUT_TOPICS = ["behavior.profile", "audit.events"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8058
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]
    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        handle_id = message.get("handle_id") or message.get("actor_user") or "unknown"
        is_anomaly = message.get("is_anomaly") or False
        anomaly_score = float(message.get("anomaly_score") or 0.0)
        event_type = message.get("event_type") or ""
        signals_detected = [s for s in INSIDER_SIGNALS if s in event_type.lower() or s in str(message).lower()]
        risk_score = min(1.0, anomaly_score + len(signals_detected) * 0.10)
        risk_level = "critical" if risk_score > 0.85 else "high" if risk_score > 0.65 else "medium" if risk_score > 0.40 else "low"
        out = [{"event_type": "insider_threat_assessment", "handle_id": handle_id,
                "risk_score": round(risk_score, 4), "risk_level": risk_level,
                "signals_detected": signals_detected, "is_anomaly": is_anomaly,
                "assessed_at": datetime.now(timezone.utc).isoformat(), "correlation_id": cid}]
        logger.info("insider_threat_assessed", handle=handle_id, risk=risk_level,
                    risk_score=risk_score, correlation_id=cid)
        return out
