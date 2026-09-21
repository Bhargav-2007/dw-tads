"""Tier: A — Real. Algorithms: regex detection of mod_status, nginx stub_status,
phpinfo, directory listings, default server banners, path traversal,
exposed git repos from scan.raw body and header fields."""
import re
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

RULES = [
    ("mod_status_exposed",     re.compile(r"Apache Server Status", re.IGNORECASE)),
    ("nginx_stub_status",      re.compile(r"Active connections:\s*\d+", re.IGNORECASE)),
    ("phpinfo_exposed",        re.compile(r"PHP Version \d+\.\d+", re.IGNORECASE)),
    ("directory_listing",      re.compile(r"<title>Index of /", re.IGNORECASE)),
    ("git_exposed",            re.compile(r"\.git/HEAD|ref: refs/heads", re.IGNORECASE)),
    ("path_traversal",         re.compile(r"\.\./\.\./|\.\.\\\.\.", re.IGNORECASE)),
    ("default_nginx_page",     re.compile(r"Welcome to nginx!", re.IGNORECASE)),
    ("default_apache_page",    re.compile(r"Apache2? (Ubuntu|Debian) Default Page", re.IGNORECASE)),
    ("aws_key_exposed",        re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE)),
    ("backup_file_exposed",    re.compile(r"\.bak|\.sql|\.tar\.gz|\.zip", re.IGNORECASE)),
]

SEVERITY = {
    "mod_status_exposed":   "high",
    "nginx_stub_status":    "medium",
    "phpinfo_exposed":      "high",
    "directory_listing":    "high",
    "git_exposed":          "critical",
    "path_traversal":       "critical",
    "default_nginx_page":   "low",
    "default_apache_page":  "low",
    "aws_key_exposed":      "critical",
    "backup_file_exposed":  "high",
}

class MisconfigAnalyzer(BaseService):
    NAME = "misconfig-analyzer"
    PLANE = 3
    TIER = "Advanced"
    INPUT_TOPICS = ["scan.raw", "crawl.raw"]
    OUTPUT_TOPICS = ["infra.indicators"]
    HTTP_PORT = 8041
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        body = str(message.get("match_text") or message.get("raw_content") or
                   message.get("body") or "")
        headers = message.get("headers") or {}
        onion = str(message.get("onion_address") or message.get("target") or "")

        path = str(message.get("path") or "")
        ip = message.get("ip") or message.get("matched_clearnet_ip")

        if not body and not headers and not path:
            return []

        headers_str = " ".join(f"{k}: {v}" for k, v in headers.items())
        scan_text = f"{body}\n{headers_str}\n{path}"

        findings = []
        for rule_name, pattern in RULES:
            m = pattern.search(scan_text)
            if m:
                ftype = "mod_status_leak" if (rule_name == "mod_status_exposed" and "/server-status" in scan_text) else rule_name
                findings.append({
                    "onion_address": onion,
                    "finding_type": ftype,
                    "confidence": 0.95,
                    "match_text": m.group(0)[:200],
                    "severity": SEVERITY.get(rule_name, "medium"),
                    "matched_clearnet_domain": None,
                    "matched_clearnet_ip": ip,
                    "match_type": ftype,
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                    "correlation_id": cid,
                })

        if not findings:
            findings.append({
                "onion_address": onion,
                "finding_type": "no_misconfiguration",
                "confidence": 0.90,
                "match_text": "",
                "severity": "none",
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "correlation_id": cid,
            })

        logger.info("misconfig_analyzed", onion=onion[:32], findings=len(findings),
                    correlation_id=cid)
        return findings
