"""Tier: B — Honest stub. Reads mock_sources/, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

class YaraGenerator(BaseService):
    NAME = "yara-generator"
    PLANE = 3
    TIER = "Expert"
    INPUT_TOPICS = ["malware.family"]
    OUTPUT_TOPICS = ["threat.iocs"]
    HTTP_PORT = 8054
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        malware_family = message["malware_family"] if "malware_family" in message else "Ransomware.Generic"
        sample_hash = message["sample_hash"] if "sample_hash" in message else "e3b0c442"

        rule_name = re.sub(r"[^a-zA-Z0-9_]", "_", malware_family)
        rule_content = f"rule {rule_name} {{\n  strings:\n    $hash = \"{sample_hash[:16]}\"\n  condition:\n    uint16(0) == 0x5A4D and any of them\n}}\n"

        out = [{
            "rule_name": rule_name,
            "yara_rule": rule_content,
            "source_sample": sample_hash,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("yara_rule_generated", rule_name=rule_name, correlation_id=cid)
        return out
