"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

MALICIOUS_PATTERNS = [
    re.compile(r"<script", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"\x00"),
    re.compile(r"\.{200,}"),  # very long strings may be exploits
]

class DataDiode(BaseService):
    NAME = "data-diode"
    PLANE = 1
    TIER = "Foundation"
    INPUT_TOPICS = ["quarantine.signals"]
    OUTPUT_TOPICS = ["scan.raw"]
    HTTP_PORT = 8018
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        raw_content = message["raw_content"] if "raw_content" in message else ""
        source = message["source"] if "source" in message else "unknown"
        onion_address = message["onion_address"] if "onion_address" in message else ""

        if not raw_content:
            return []

        # One-way sanitisation: strip known injection patterns
        cleaned = raw_content
        threats_found = []
        for pat in MALICIOUS_PATTERNS:
            if pat.search(cleaned):
                threats_found.append(pat.pattern)
                cleaned = pat.sub("[REDACTED]", cleaned)

        content_sha = hashlib.sha256(cleaned.encode()).hexdigest()
        risk_level = "high" if len(threats_found) > 1 else ("medium" if threats_found else "low")

        out = [{
            "onion_address": onion_address,
            "finding_type": "data_diode_sanitized",
            "match_text": f"threats_found:{len(threats_found)}",
            "http_status": 200,
            "headers": {"x-diode-risk": risk_level},
            "content_sha256": content_sha,
            "risk_level": risk_level,
            "threats": threats_found,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("data_diode_processed", onion=onion_address[:32], risk=risk_level,
                    threats=len(threats_found), correlation_id=cid)
        return out
