"""Tier: A — Real. Algorithms: RFC-6962 Merkle tree, SHA-256 content addressing,
advisory-lock audit chain write, MinIO object storage upload."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService, merkle_root, sha256_hex

logger = structlog.get_logger()


class EvidencePipeline(BaseService):
    NAME = "evidence-pipeline"
    PLANE = 1
    TIER = "Foundation"
    INPUT_TOPICS = ["crawl.raw", "scan.raw"]
    OUTPUT_TOPICS = ["content.clean", "merkle.root", "audit.events"]
    HTTP_PORT = 8013
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        raw_text = (message.get("text") or message.get("raw_content")
                    or message.get("body") or "")
        source_url = (message.get("target") or message.get("source_url")
                      or message.get("onion_address") or "")
        handle_id = message["handle_id"] if "handle_id" in message else "unknown"
        platform = message["platform"] if "platform" in message else "darkweb"
        captured_at = message["captured_at"] if "captured_at" in message else datetime.now(timezone.utc).isoformat()

        raw_bytes = raw_text.encode("utf-8")
        content_sha256 = sha256_hex(raw_bytes)
        url_sha256 = sha256_hex(source_url.encode("utf-8"))
        byte_size = len(raw_bytes)

        # RFC-6962 Merkle root over [content_sha256, url_sha256]
        mroot = merkle_root([content_sha256, url_sha256])

        clean_text = raw_text.replace("\x00", "").strip()

        # Upload to MinIO if client is available
        minio_key = f"evidence/{content_sha256[:2]}/{content_sha256}.bin"
        minio_bucket = "raw-crawl"
        if self.minio is not None:
            try:
                self.minio.ensure_bucket(minio_bucket)
                self.minio.upload_with_hash(minio_bucket, minio_key, raw_bytes)
            except Exception as e:
                logger.warning("minio_upload_failed", error=str(e), correlation_id=cid)

        # Write to Postgres evidence table if pg client available
        if self.pg is not None:
            try:
                await self.pg.execute(
                    """INSERT INTO evidence(sha256, source_url, source_type,
                       captured_at, minio_bucket, minio_key, merkle_root, ingested_by)
                       VALUES($1,$2,$3,$4,$5,$6,$7,$8)
                       ON CONFLICT (sha256) DO NOTHING""",
                    content_sha256, source_url, platform,
                    captured_at, minio_bucket, minio_key, mroot,
                    self.NAME,
                )
                await self.pg.write_audit(
                    event_type="evidence_ingested",
                    actor_user=handle_id,
                    action="INGEST",
                    resource=content_sha256,
                    result_hash=mroot,
                    metadata={"source_url": source_url, "byte_size": byte_size},
                )
            except Exception as e:
                logger.warning("pg_write_failed", error=str(e), correlation_id=cid)

        clean_event = {
            "handle_id": handle_id,
            "platform": platform,
            "text": clean_text,
            "posted_at": captured_at,
            "source_sha256": content_sha256,
            "byte_size": byte_size,
            "correlation_id": cid,
        }
        merkle_event = {
            "merkle_root": mroot,
            "leaf_sha256": content_sha256,
            "source_url": source_url,
            "anchored_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }
        audit_event = {
            "event_type": "evidence_anchored",
            "resource": content_sha256,
            "merkle_root": mroot,
            "action": "EVIDENCE_INGESTED",
            "correlation_id": cid,
        }
        logger.info("evidence_processed", sha256=content_sha256, merkle_root=mroot,
                    byte_size=byte_size, correlation_id=cid)
        return [clean_event, merkle_event, audit_event]
