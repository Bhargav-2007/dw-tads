"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

class ChaosEngineering(BaseService):
    NAME = "chaos-engineering"
    PLANE = 1
    TIER = "Advanced"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["service.errors"]
    HTTP_PORT = 8020
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        target_service = message["target_service"] if "target_service" in message else ""
        fault_type = message["fault_type"] if "fault_type" in message else "latency"
        intensity = float(message["intensity"]) if "intensity" in message else 0.1

        if not target_service:
            return []

        # Scale intensity to fault parameters
        if fault_type == "latency":
            delay_ms = int(intensity * 5000)
            impact = f"latency_injection_{delay_ms}ms"
        elif fault_type == "packet_loss":
            loss_pct = min(100, int(intensity * 100))
            impact = f"packet_loss_{loss_pct}pct"
        elif fault_type == "cpu_stress":
            cpu_pct = min(100, int(intensity * 100))
            impact = f"cpu_stress_{cpu_pct}pct"
        else:
            impact = f"unknown_fault_{fault_type}"

        experiment_id = hashlib.sha256(
            f"{target_service}:{fault_type}:{cid}".encode()
        ).hexdigest()[:16]

        out = [{
            "service": target_service,
            "fault_type": fault_type,
            "intensity": round(intensity, 3),
            "impact": impact,
            "experiment_id": experiment_id,
            "status": "injected",
            "injected_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("chaos_injected", target=target_service, fault=fault_type,
                    impact=impact, correlation_id=cid)
        return out
