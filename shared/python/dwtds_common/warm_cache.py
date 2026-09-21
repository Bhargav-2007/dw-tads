"""Cache warming CLI — populates /var/lib/dwtds/cache/ from all live sources.

Usage:
    python3 -m dwtds_common.warm_cache \
        --sources ahmia,threatfox,urlhaus,feodo,abuse_ssl,circl \
        --cache-dir /var/lib/dwtds/cache

Run on a connected host before air-gap transfer. In air-gap mode the
services automatically read from cache; nothing else changes.
"""

import argparse
import asyncio
import csv
import io
import json
import sys
from urllib.parse import quote

from .cache import fetch_with_cache, TTL_HOURS
from .logging import configure_logging, get_logger

log = get_logger("warm_cache")

AHMIA_KEYWORDS = [
    "market", "forum", "hacking", "ransomware", "leaks",
    "carding", "drugs", "arms", "exploit", "darknet",
]

FEODO_URL = "https://feodotracker.abuse.ch/downloads/ipblocklist.csv"
URLHAUS_URL = "https://urlhaus.abuse.ch/downloads/csv_recent/"
ABUSE_SSL_URL = "https://sslbl.abuse.ch/blacklist/sslipblacklist.txt"
THREATFOX_URL = "https://threatfox-api.abuse.ch/api/v1/"
CIRCL_URL = "https://www.circl.lu/doc/misp/feed-osint/hashes.csv"


def _parse_json(body: bytes):
    return json.loads(body)


def _parse_csv_rows(body: bytes) -> list[dict]:
    text = body.decode("utf-8", errors="replace")
    lines = [l for l in text.splitlines() if l and not l.startswith("#")]
    if not lines:
        return []
    reader = csv.DictReader(lines)
    return list(reader)


def _parse_text_lines(body: bytes) -> list[str]:
    return [l.strip() for l in body.decode("utf-8", errors="replace").splitlines()
            if l.strip() and not l.startswith("#")]


async def warm_ahmia():
    log.info("warm.ahmia.start", keywords=len(AHMIA_KEYWORDS))
    for kw in AHMIA_KEYWORDS:
        url = f"https://ahmia.fi/search/?q={quote(kw)}"
        await fetch_with_cache(url, "ahmia", TTL_HOURS["ahmia"], lambda b: b)
        await asyncio.sleep(1)


async def warm_threatfox():
    url = THREATFOX_URL
    body = {"query": "get_iocs", "days": 7}
    await fetch_with_cache(url, "threatfox", TTL_HOURS["threatfox"],
                           _parse_json, method="POST", json_body=body,
                           headers={"API-KEY": "00000000000000000000000000000000"})


async def warm_urlhaus():
    await fetch_with_cache(URLHAUS_URL, "urlhaus", TTL_HOURS["urlhaus"],
                           _parse_csv_rows)


async def warm_feodo():
    await fetch_with_cache(FEODO_URL, "feodo", TTL_HOURS["feodo"],
                           _parse_csv_rows)


async def warm_abuse_ssl():
    await fetch_with_cache(ABUSE_SSL_URL, "abuse_ssl", TTL_HOURS["abuse_ssl"],
                           _parse_text_lines)


async def warm_circl():
    await fetch_with_cache(CIRCL_URL, "circl", TTL_HOURS["circl"],
                           _parse_text_lines)


WARMERS = {
    "ahmia": warm_ahmia,
    "threatfox": warm_threatfox,
    "urlhaus": warm_urlhaus,
    "feodo": warm_feodo,
    "abuse_ssl": warm_abuse_ssl,
    "circl": warm_circl,
}


async def main(sources: list[str]) -> int:
    errors = 0
    for source in sources:
        fn = WARMERS.get(source)
        if fn is None:
            log.warning("warm.unknown_source", source=source)
            continue
        log.info("warm.source.start", source=source)
        try:
            await fn()
            log.info("warm.source.done", source=source)
        except Exception as e:
            log.error("warm.source.error", source=source, error=str(e))
            errors += 1
    return errors


if __name__ == "__main__":
    configure_logging("INFO", "warm_cache")
    parser = argparse.ArgumentParser(description="Warm DW-TADS cache from live sources")
    parser.add_argument("--sources", default=",".join(WARMERS.keys()),
                        help="Comma-separated list of sources to warm")
    parser.add_argument("--cache-dir", default="/var/lib/dwtds/cache",
                        help="Cache root directory")
    args = parser.parse_args()

    import os
    os.environ["CACHE_DIR"] = args.cache_dir

    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    errors = asyncio.run(main(sources))
    sys.exit(1 if errors else 0)
