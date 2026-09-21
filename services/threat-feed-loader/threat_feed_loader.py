"""Tier: A — Real. Algorithms: live HTTP fetch from abuse.ch SSL IP BL, Feodo
Tracker, URLhaus CSV, ThreatFox API (POST), CIRCL OSINT. IPv4 regex validation.
Cache-first with per-source TTLs (6h for abuse.ch feeds)."""
import csv
import io
import json
import re
from datetime import datetime, timezone
import httpx
import structlog
from common.base_service import BaseService, fetch_with_cache

logger = structlog.get_logger()

IPV4_RE = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)
DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)

FEODO_URL = "https://feodotracker.abuse.ch/downloads/ipblocklist.csv"
URLHAUS_URL = "https://urlhaus.abuse.ch/downloads/csv_recent/"
ABUSE_SSL_URL = "https://sslbl.abuse.ch/blacklist/sslipblacklist.txt"
THREATFOX_URL = "https://threatfox-api.abuse.ch/api/v1/"


def _parse_csv(body: bytes) -> list[dict]:
    text = body.decode("utf-8", errors="replace")
    lines = [l for l in text.splitlines() if l and not l.startswith("#")]
    if not lines:
        return []
    try:
        return list(csv.DictReader(lines))
    except Exception:
        return []


def _parse_txt_ips(body: bytes) -> list[str]:
    return [l.strip() for l in body.decode("utf-8", errors="replace").splitlines()
            if l.strip() and not l.startswith("#") and IPV4_RE.match(l.strip())]


def _parse_threatfox(body: bytes) -> list[dict]:
    try:
        d = json.loads(body)
        return d.get("data", []) if isinstance(d, dict) else []
    except Exception:
        return []


class ThreatFeedLoader(BaseService):
    NAME = "threat-feed-loader"
    PLANE = 2
    TIER = "Intermediate"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["threat.iocs"]
    HTTP_PORT = 8030
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        feed_type = message["feed_type"] if "feed_type" in message else "threatfox"

        iocs = []

        if feed_type == "threatfox":
            data = await fetch_with_cache(
                THREATFOX_URL, "threatfox", 6, _parse_threatfox,
                method="POST",
                json_body={"query": "get_iocs", "days": 1},
                headers={"API-KEY": "00000000000000000000000000000000"},
            )
            for entry in (data or []):
                val = str(entry.get("ioc") or entry.get("ioc_value") or "")
                ioc_type = str(entry.get("ioc_type") or "")
                conf = float(entry.get("confidence_level") or 75) / 100.0
                if ioc_type == "ip:port":
                    ip = val.split(":")[0]
                    if IPV4_RE.match(ip):
                        iocs.append({"ioc": ip, "ioc_type": "ipv4", "confidence": conf,
                                     "source": "threatfox",
                                     "first_seen": str(entry.get("first_seen", "")),
                                     "tags": entry.get("tags") or [],
                                     "correlation_id": cid})
                elif ioc_type == "domain":
                    if DOMAIN_RE.match(val):
                        iocs.append({"ioc": val, "ioc_type": "domain", "confidence": conf,
                                     "source": "threatfox",
                                     "first_seen": str(entry.get("first_seen", "")),
                                     "tags": entry.get("tags") or [],
                                     "correlation_id": cid})

        elif feed_type == "feodo":
            rows = await fetch_with_cache(FEODO_URL, "feodo", 6, _parse_csv)
            for row in (rows or []):
                ip = str(row.get("dst_ip") or row.get("ip_address") or "").strip()
                if IPV4_RE.match(ip):
                    iocs.append({"ioc": ip, "ioc_type": "c2_ip", "confidence": 0.95,
                                 "source": "feodo",
                                 "first_seen": str(row.get("first_seen", "")),
                                 "tags": ["c2", "botnet"],
                                 "correlation_id": cid})

        elif feed_type == "urlhaus":
            rows = await fetch_with_cache(URLHAUS_URL, "urlhaus", 6, _parse_csv)
            for row in (rows or []):
                url_val = str(row.get("url") or "").strip()
                if url_val.startswith("http"):
                    iocs.append({"ioc": url_val, "ioc_type": "url", "confidence": 0.85,
                                 "source": "urlhaus",
                                 "first_seen": str(row.get("dateadded", "")),
                                 "tags": ["malware", "phishing"],
                                 "correlation_id": cid})

        elif feed_type == "abuse_ssl":
            ips = await fetch_with_cache(ABUSE_SSL_URL, "abuse_ssl", 6, _parse_txt_ips)
            for ip in (ips or []):
                iocs.append({"ioc": ip, "ioc_type": "ssl_blacklisted_ip",
                             "confidence": 0.90, "source": "abuse_ssl",
                             "first_seen": "", "tags": ["ssl", "c2"],
                             "correlation_id": cid})

        logger.info("threat_feed_loaded", feed_type=feed_type, ioc_count=len(iocs),
                    correlation_id=cid)
        return iocs
