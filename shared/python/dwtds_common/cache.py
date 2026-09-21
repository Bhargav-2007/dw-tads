"""Cache-first HTTP fetch with TTL, stale fallback, and source_fetches audit.

Directory layout:
    /var/lib/dwtds/cache/<source>/<sha256_of_url>.body
    /var/lib/dwtds/cache/<source>/<sha256_of_url>.meta.json

TTL policy (hours):
    ahmia=168, onionscan=24, threatfox=6, urlhaus=6, feodo=6,
    abuse_ssl=6, circl=12, blockchair=1, crtsh=168, graphsense=720,
    darkforumcti=720
"""

import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

from .logging import get_logger

log = get_logger("cache")

CACHE_ROOT = Path(os.getenv("CACHE_DIR", "/var/lib/dwtds/cache"))

TTL_HOURS: dict[str, int] = {
    "ahmia": 168,
    "onionscan": 24,
    "threatfox": 6,
    "urlhaus": 6,
    "feodo": 6,
    "abuse_ssl": 6,
    "circl": 12,
    "blockchair": 1,
    "crtsh": 168,
    "graphsense": 720,
    "darkforumcti": 720,
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _cache_paths(source: str, url: str):
    cache_dir = CACHE_ROOT / source
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()
    return cache_dir / f"{key}.body", cache_dir / f"{key}.meta.json", key


async def fetch_with_cache(
    url: str,
    source: str,
    ttl_hours: int,
    parser,
    *,
    method: str = "GET",
    json_body: dict | None = None,
    headers: dict | None = None,
) -> object | None:
    """
    Fetch URL with cache-first strategy:
      1. Cache hit within TTL → return parser(cached body).
      2. Cache miss or expired → fetch live → update cache → return parser(body).
      3. Live failure → if stale cache exists, use it with warning.
      4. No cache and live fails → return None; caller must handle gracefully.
    """
    body_file, meta_file, cache_key = _cache_paths(source, url)

    # --- Cache hit ---
    if body_file.exists() and meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text())
            expires = datetime.fromisoformat(meta["expires_at"])
            if expires > utc_now():
                age = int((utc_now() - datetime.fromisoformat(meta["fetched_at"])).total_seconds())
                log.info("cache.hit", source=source, url=url, age_seconds=age,
                         cache_hit=True, record_count=meta.get("record_count", 0))
                return parser(body_file.read_bytes())
        except Exception as e:
            log.warning("cache.meta.corrupt", source=source, url=url, error=str(e))

    # --- Live fetch ---
    log.info("cache.miss", source=source, url=url, cache_hit=False)
    t0 = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            if method == "POST" and json_body is not None:
                resp = await client.post(url, json=json_body, headers=headers or {})
            else:
                resp = await client.get(url, headers=headers or {})
            resp.raise_for_status()
            body = resp.content
            http_status = resp.status_code
            content_type = resp.headers.get("content-type", "")
        duration_ms = int((time.monotonic() - t0) * 1000)
        log.info(
            "source.fetched",
            source=source,
            url=url,
            http_status=http_status,
            duration_ms=duration_ms,
            cache_hit=False,
        )
    except Exception as e:
        duration_ms = int((time.monotonic() - t0) * 1000)
        log.warning(
            "source.unreachable",
            source=source,
            url=url,
            error=str(e),
            duration_ms=duration_ms,
        )
        if body_file.exists():
            log.info("cache.stale_fallback", source=source, url=url)
            try:
                return parser(body_file.read_bytes())
            except Exception as pe:
                log.warning("cache.stale.parse_error", source=source, error=str(pe))
        return None

    # --- Update cache ---
    try:
        result = parser(body)
        record_count = len(result) if hasattr(result, "__len__") else 0
        body_file.write_bytes(body)
        meta = {
            "url": url,
            "sha256": hashlib.sha256(body).hexdigest(),
            "fetched_at": utc_now().isoformat(),
            "expires_at": (utc_now() + timedelta(hours=ttl_hours)).isoformat(),
            "record_count": record_count,
            "http_status": http_status,
            "content_type": content_type,
            "duration_ms": duration_ms,
        }
        meta_file.write_text(json.dumps(meta, indent=2))
        return result
    except Exception as e:
        log.warning("cache.write_error", source=source, url=url, error=str(e))
        try:
            return parser(body)
        except Exception:
            return None


def get_cached_body(source: str, url: str) -> bytes | None:
    """Return raw cached bytes for a URL, regardless of TTL. Returns None if absent."""
    body_file, _, _ = _cache_paths(source, url)
    if body_file.exists():
        return body_file.read_bytes()
    return None
