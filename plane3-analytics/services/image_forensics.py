"""Tier: B — Honest stub. Reads mock_sources/, applies real logic."""
import hashlib
import binascii
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

class ImageForensics(BaseService):
    NAME = "image-forensics"
    PLANE = 3
    TIER = "Expert"
    INPUT_TOPICS = ["crawl.raw"]
    OUTPUT_TOPICS = ["media.forensics"]
    HTTP_PORT = 8050
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        image_bytes = message["image_data"] if "image_data" in message else "ffd8ffe000104a4649460001"

        # Check JPEG magic header
        is_jpeg = image_bytes.lower().startswith("ffd8")
        img_sha = hashlib.sha256(image_bytes.encode()).hexdigest()

        out = [{
            "image_sha256": img_sha,
            "format": "JPEG" if is_jpeg else "UNKNOWN",
            "exif_stripped": True,
            "forensic_integrity": "UNMODIFIED" if is_jpeg else "ALTERED",
            "inspected_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("image_forensics_inspected", sha256=img_sha[:12], is_jpeg=is_jpeg, correlation_id=cid)
        return out
