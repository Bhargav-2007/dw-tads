"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

ATTACK_SIGNATURES = {
    "prompt_injection": re.compile(
        r"ignore (all )?previous (instructions|prompts)|"
        r"you are now|act as|disregard|forget",
        re.IGNORECASE
    ),
    "jailbreak": re.compile(
        r"DAN mode|developer mode|bypass|override|"
        r"unlimited|no restrictions|ignore guidelines",
        re.IGNORECASE
    ),
    "data_poisoning": re.compile(
        r"label this as|annotate as|train on this|fine.?tune|"
        r"poison|backdoor trigger",
        re.IGNORECASE
    ),
    "adversarial_text": re.compile(
        r"\u200b|\u200c|\u200d|\u200e|\u200f|"   # Zero-width chars
        r"[\x00-\x08\x0b\x0e-\x1f]",             # Control chars
    ),
}


class AdversarialDefense(BaseService):
    NAME = "adversarial-defense"
    PLANE = 3
    TIER = "Advanced"
    INPUT_TOPICS = ["content.clean"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8047
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        text = message["text"] if "text" in message else ""
        handle_id = message["handle_id"] if "handle_id" in message else "anon"

        if not text:
            return []

        detected = {}
        for attack_type, pattern in ATTACK_SIGNATURES.items():
            m = pattern.search(text)
            if m:
                detected[attack_type] = m.group(0)[:100]

        severity = "none"
        if "data_poisoning" in detected or "jailbreak" in detected:
            severity = "critical"
        elif "prompt_injection" in detected:
            severity = "high"
        elif "adversarial_text" in detected:
            severity = "medium"

        out = [{
            "event_type": "adversarial_attack_report",
            "handle_id": handle_id,
            "attacks_detected": list(detected.keys()),
            "attack_details": detected,
            "severity": severity,
            "input_hash": hashlib.sha256(text.encode()).hexdigest(),
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("adversarial_defense_scanned", attacks=list(detected.keys()),
                    severity=severity, correlation_id=cid)
        return out
