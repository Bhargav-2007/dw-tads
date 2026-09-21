"""Tier: A — Real. Algorithms: Jaccard similarity over favicon SHA-256, TLS serial,
ETag fingerprints; crt.sh CT log lookup; SQLite clearnet_index.db query."""
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import httpx
import structlog
from common.base_service import BaseService, fetch_with_cache

logger = structlog.get_logger()

CRTSH_URL = "https://crt.sh/?q={domain}&output=json"
INDEX_DB = Path("/var/lib/dwtds/clearnet_index.db")


def _parse_crtsh(body: bytes) -> list[dict]:
    try:
        return json.loads(body)
    except Exception:
        return []


def _jaccard(set_a: set, set_b: set) -> float:
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


class ClearnetCorrelator(BaseService):
    NAME = "clearnet-correlator"
    PLANE = 3
    TIER = "Advanced"
    INPUT_TOPICS = ["scan.raw"]
    OUTPUT_TOPICS = ["infra.indicators"]
    HTTP_PORT = 8040
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        onion = message["onion_address"] if "onion_address" in message else ""
        favicon_sha = message.get("favicon_sha256") or ""
        ssl_serial = message.get("ssl_serial") or ""
        etag = message.get("etag") or ""
        finding_type = message.get("finding_type", "unknown")

        if not onion:
            return []

        probe_set = set(filter(None, [favicon_sha, ssl_serial, etag]))
        matched_domain = None
        matched_ip = None
        confidence = 0.0
        match_type = "none"

        # SQLite index lookup (if DB exists)
        if INDEX_DB.exists():
            try:
                conn = sqlite3.connect(str(INDEX_DB))
                cur = conn.cursor()
                cur.execute(
                    "SELECT domain, ip, fingerprints FROM clearnet_index WHERE "
                    "favicon_sha=? OR ssl_serial=? OR etag=? LIMIT 1",
                    (favicon_sha or "", ssl_serial or "", etag or "")
                )
                row = cur.fetchone()
                conn.close()
                if row:
                    matched_domain = row[0]
                    matched_ip = row[1]
                    try:
                        known_fps = set(json.loads(row[2] or "[]"))
                    except Exception:
                        known_fps = set()
                    sim = _jaccard(probe_set, known_fps)
                    confidence = round(min(1.0, 0.6 + sim * 0.4), 3)
                    match_type = "index_hit"
            except Exception as e:
                logger.warning("clearnet_correlator_db_error", error=str(e), correlation_id=cid)

        # crt.sh fallback for domain correlation
        if not matched_domain and ssl_serial:
            # Use ssl_serial as domain hint (first 8 hex chars as query)
            domain_guess = ssl_serial[:8]
            url = CRTSH_URL.format(domain=domain_guess)
            certs = await fetch_with_cache(url, "crtsh", 168, _parse_crtsh)
            if certs:
                matched_domain = str(certs[0].get("name_value", "")).split("\n")[0]
                confidence = 0.60
                match_type = "crtsh_ssl"

        out = [{
            "onion_address": onion,
            "finding_type": finding_type,
            "confidence": confidence,
            "matched_clearnet_domain": matched_domain,
            "matched_clearnet_ip": matched_ip,
            "match_type": match_type,
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("clearnet_correlated", onion=onion[:32], match_type=match_type,
                    confidence=confidence, correlation_id=cid)
        return out
