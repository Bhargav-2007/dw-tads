"""Tier: A — Real. Algorithms: RFC-3161 timestamp simulation (SHA-256 + UTC
ISO), MinIO object storage with SHA-256 verification, Postgres insert."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService, sha256_hex

logger = structlog.get_logger()


class EvidenceAnchor(BaseService):
    NAME = "evidence-anchor"
    PLANE = 5
    TIER = "Advanced"
    INPUT_TOPICS = ["merkle.root"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8063
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        merkle = message.get("merkle_root") or ""
        leaf_sha = message.get("leaf_sha256") or ""
        source_url = message.get("source_url") or ""

        if not merkle and not leaf_sha:
            return []

        # RFC-3161 style timestamp token: sha256(merkle || utc_ts || cid)
        ts_str = datetime.now(timezone.utc).isoformat()
        token_input = f"{merkle}{ts_str}{cid}"
        timestamp_token = sha256_hex(token_input.encode())

        anchor_sha = sha256_hex(f"{merkle}:{leaf_sha}:{timestamp_token}".encode())

        # Upload anchor to MinIO
        if self.minio is not None:
            try:
                bucket = "audit-anchors"
                key = f"anchors/{anchor_sha[:2]}/{anchor_sha}.json"
                import json
                anchor_bytes = json.dumps({
                    "merkle_root": merkle,
                    "leaf_sha256": leaf_sha,
                    "timestamp_token": timestamp_token,
                    "anchored_at": ts_str,
                    "correlation_id": cid,
                }).encode()
                self.minio.ensure_bucket(bucket)
                self.minio.upload_with_hash(bucket, key, anchor_bytes,
                                            content_type="application/json")
            except Exception as e:
                logger.warning("evidence_anchor_minio_error", error=str(e), correlation_id=cid)

        # Write to Postgres
        if self.pg is not None:
            try:
                await self.pg.execute(
                    """INSERT INTO evidence(sha256, source_url, source_type, captured_at,
                       minio_bucket, minio_key, merkle_root, ingested_by)
                       VALUES($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT (sha256) DO NOTHING""",
                    anchor_sha, source_url, "anchor", ts_str,
                    "audit-anchors", f"anchors/{anchor_sha[:2]}/{anchor_sha}.json",
                    merkle, self.NAME,
                )
            except Exception as e:
                logger.warning("evidence_anchor_pg_error", error=str(e), correlation_id=cid)

        out = [{
            "event_type": "evidence_anchored",
            "anchor_sha256": anchor_sha,
            "merkle_root": merkle,
            "leaf_sha256": leaf_sha,
            "timestamp_token": timestamp_token,
            "anchored_at": ts_str,
            "resource": anchor_sha,
            "correlation_id": cid,
        }]
        logger.info("evidence_anchored", merkle=merkle[:16], anchor=anchor_sha[:16],
                    correlation_id=cid)
        return out
