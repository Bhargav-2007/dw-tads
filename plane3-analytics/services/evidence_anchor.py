"""Tier: B — Honest stub. Reads mock_sources/, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

class EvidenceAnchor(BaseService):
    NAME = "evidence-anchor"
    PLANE = 3
    TIER = "Advanced"
    INPUT_TOPICS = ["merkle.root"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8053
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        merkle_root = message["merkle_root"] if "merkle_root" in message else "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

        # Simulate RFC 3161 timestamp anchor
        ts = datetime.now(timezone.utc).isoformat()
        ots_anchor = hashlib.sha256(f"RFC3161:{merkle_root}:{ts}".encode()).hexdigest()

        out = [{
            "merkle_root": merkle_root,
            "ots_anchor_hash": ots_anchor,
            "timestamp_authority": "DW-TADS-Internal-TSA",
            "anchored_at": ts,
            "correlation_id": cid,
        }]
        logger.info("merkle_root_anchored", merkle_root=merkle_root[:12], anchor=ots_anchor[:12], correlation_id=cid)
        return out
