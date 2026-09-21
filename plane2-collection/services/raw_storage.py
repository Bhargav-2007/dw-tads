"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

MAX_CONTENT_BYTES = 10_000_000  # 10MB limit

class RawStorage(BaseService):
    NAME = "raw-storage"
    PLANE = 2
    TIER = "Foundation"
    INPUT_TOPICS = ["crawl.raw", "scan.raw"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8036
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        raw_content = str(message.get("raw_content") or message.get("match_text") or "")
        target = str(message.get("target") or message.get("onion_address") or "")
        source_type = "crawl.raw" if "target" in message else "scan.raw"

        if not raw_content:
            return []

        raw_bytes = raw_content.encode("utf-8")
        content_sha = hashlib.sha256(raw_bytes).hexdigest()
        byte_size = len(raw_bytes)

        # Size-based storage tier
        if byte_size > MAX_CONTENT_BYTES:
            storage_status = "rejected_too_large"
        elif byte_size == 0:
            storage_status = "rejected_empty"
        else:
            storage_status = "stored"
            if self.minio is not None:
                try:
                    bucket = "raw-crawl"
                    key = f"raw/{source_type}/{content_sha[:2]}/{content_sha}.bin"
                    self.minio.ensure_bucket(bucket)
                    self.minio.upload_with_hash(bucket, key, raw_bytes)
                except Exception as e:
                    storage_status = "minio_error"
                    logger.warning("raw_storage_minio_error", error=str(e), correlation_id=cid)

        out = [{
            "event_type": "raw_content_stored",
            "target": target,
            "content_sha256": content_sha,
            "byte_size": byte_size,
            "source_type": source_type,
            "storage_status": storage_status,
            "stored_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("raw_storage_processed", target=target[:32], sha=content_sha[:16],
                    status=storage_status, size=byte_size, correlation_id=cid)
        return out
