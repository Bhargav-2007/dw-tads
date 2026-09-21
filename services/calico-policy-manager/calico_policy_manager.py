"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

POLICY_ACTIONS = {"allow", "deny", "log", "quarantine"}

class CalicoPolicyManager(BaseService):
    NAME = "calico-policy-manager"
    PLANE = 1
    TIER = "Foundation"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8019
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        src_ip = message["src_ip"] if "src_ip" in message else ""
        dst_ip = message["dst_ip"] if "dst_ip" in message else ""
        dst_port = int(message["dst_port"]) if "dst_port" in message else 0
        protocol = message["protocol"] if "protocol" in message else "tcp"

        if not src_ip or not dst_ip:
            return []

        # Port-based policy classification
        if dst_port in (9050, 9051, 9150):
            action = "allow"
            policy_name = "tor-allow"
        elif dst_port in (22, 23, 3389):
            action = "deny"
            policy_name = "admin-deny"
        elif dst_port < 1024 and protocol == "udp":
            action = "log"
            policy_name = "udp-privileged-log"
        else:
            action = "allow"
            policy_name = "default-allow"

        flow_id = hashlib.sha256(f"{src_ip}:{dst_ip}:{dst_port}:{protocol}".encode()).hexdigest()[:16]

        out = [{
            "event_type": "network_policy_evaluated",
            "flow_id": flow_id,
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "dst_port": dst_port,
            "protocol": protocol,
            "action": action,
            "policy_name": policy_name,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("calico_policy_eval", flow_id=flow_id, action=action,
                    policy=policy_name, correlation_id=cid)
        return out
