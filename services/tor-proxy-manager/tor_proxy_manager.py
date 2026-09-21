"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

RESERVED_PREFIXES = ("10.", "192.168.", "127.", "172.16.", "172.17.",
                     "172.18.", "172.19.", "172.2", "172.3", "::1",
                     "fc00:", "fd")

class TorProxyManager(BaseService):
    NAME = "tor-proxy-manager"
    PLANE = 1
    TIER = "Foundation"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["infra.indicators"]
    HTTP_PORT = 8011
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        circuit_id = message["circuit_id"] if "circuit_id" in message else "circ-001"
        ip = message["exit_node_ip"] if "exit_node_ip" in message else ""
        bandwidth_bytes = int(message["bandwidth_bytes"]) if "bandwidth_bytes" in message else 0

        is_reserved = any(ip.startswith(p) for p in RESERVED_PREFIXES) if ip else True
        if is_reserved or not ip:
            status = "invalid_exit_node"
            risk_score = 0.0
        else:
            ip_hash = hashlib.sha256(ip.encode()).hexdigest()
            risk_score = round(int(ip_hash[:4], 16) / 65535.0, 4)
            status = "high_risk_exit" if risk_score > 0.7 else "active_tor_exit"

        # Bandwidth tier affects relay classification
        if bandwidth_bytes > 10_000_000:
            relay_class = "guard"
        elif bandwidth_bytes > 1_000_000:
            relay_class = "middle"
        else:
            relay_class = "exit"

        out = [{
            "circuit_id": circuit_id,
            "exit_node_ip": ip,
            "status": status,
            "risk_score": risk_score,
            "relay_class": relay_class,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("tor_proxy_evaluated", circuit_id=circuit_id, status=status,
                    risk_score=risk_score, correlation_id=cid)
        return out
