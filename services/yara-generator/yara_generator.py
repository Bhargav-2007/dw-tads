"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService
logger = structlog.get_logger()
def _extract_strings(text: str, min_len: int = 8) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9_/\\.-]{%d,}" % min_len, text)
    return list(set(words))[:10]
class YaraGenerator(BaseService):
    NAME = "yara-generator"
    PLANE = 4
    TIER = "Advanced"
    INPUT_TOPICS = ["category.signals"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8061
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]
    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        handle_id = message.get("handle_id") or "unknown"
        top_category = message.get("top_category") or "unknown"
        source_sha = message.get("source_sha256") or ""
        category_scores = message.get("category_scores") or {}
        rule_name = f"dwtads_{top_category}_{source_sha[:8] if source_sha else handle_id[:8]}"
        strings = [f'$s{i} = "{s}"' for i, s in enumerate(_extract_strings(" ".join(category_scores.keys()))) if s]
        if not strings:
            strings = [f'$s0 = "{top_category}"']
        condition = "any of ($s*)" if len(strings) > 1 else "$s0"
        yara_rule = (f"rule {rule_name} {{\n"
                     f"  meta:\n"
                     f"    description = \"Auto-generated for {top_category}\"\n"
                     f"    score = \"{message.get('top_score', 0)}\"\n"
                     f"  strings:\n"
                     + "\n".join(f"    {s}" for s in strings) +
                     f"\n  condition:\n    {condition}\n}}")
        rule_hash = hashlib.sha256(yara_rule.encode()).hexdigest()
        out = [{"event_type": "yara_rule_generated", "handle_id": handle_id,
                "rule_name": rule_name, "top_category": top_category,
                "rule_hash": rule_hash, "yara_rule": yara_rule,
                "string_count": len(strings),
                "generated_at": datetime.now(timezone.utc).isoformat(), "correlation_id": cid}]
        logger.info("yara_generated", rule_name=rule_name, category=top_category, correlation_id=cid)
        return out
