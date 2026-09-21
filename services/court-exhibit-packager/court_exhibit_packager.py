"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import json
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService, sha256_hex
logger = structlog.get_logger()
class CourtExhibitPackager(BaseService):
    NAME = "court-exhibit-packager"
    PLANE = 5
    TIER = "Advanced"
    INPUT_TOPICS = ["audit.events"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8068
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]
    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        case_id = message.get("case_id") or hashlib.sha256(cid.encode()).hexdigest()[:8]
        evidence_hashes = message.get("evidence_hashes") or []
        verdict = message.get("verdict") or "pending"
        exhibit_content = json.dumps({"case_id": case_id, "evidence": evidence_hashes,
                                       "verdict": verdict, "packaged_at": datetime.now(timezone.utc).isoformat()})
        exhibit_hash = sha256_hex(exhibit_content.encode())
        if self.minio is not None:
            try:
                bucket = "court-exhibits"
                key = f"exhibits/{case_id}/{exhibit_hash[:8]}.json"
                self.minio.ensure_bucket(bucket)
                self.minio.upload_with_hash(bucket, key, exhibit_content.encode(), "application/json")
            except Exception as e:
                logger.warning("court_exhibit_minio_error", error=str(e), correlation_id=cid)
        out = [{"event_type": "court_exhibit_packaged", "case_id": case_id,
                "exhibit_hash": exhibit_hash, "evidence_count": len(evidence_hashes),
                "verdict": verdict, "packaged_at": datetime.now(timezone.utc).isoformat(),
                "correlation_id": cid}]
        logger.info("court_exhibit_packaged", case_id=case_id, exhibits=len(evidence_hashes), correlation_id=cid)
        return out
