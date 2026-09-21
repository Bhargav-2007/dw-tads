"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
import re
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()


def _compute_lexical_richness(text: str) -> float:
    """Type-Token Ratio (TTR): unique_words / total_words."""
    words = re.findall(r"\b\w+\b", text.lower())
    if not words:
        return 0.0
    return round(len(set(words)) / len(words), 4)


def _avg_sentence_len(text: str) -> float:
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sentences:
        return 0.0
    return round(sum(len(s.split()) for s in sentences) / len(sentences), 2)


class CognitiveFingerprint(BaseService):
    NAME = "cognitive-fingerprint"
    PLANE = 3
    TIER = "Advanced"
    INPUT_TOPICS = ["content.clean"]
    OUTPUT_TOPICS = ["persona.links"]
    HTTP_PORT = 8043
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        text = message["text"] if "text" in message else ""
        handle_id = message["handle_id"] if "handle_id" in message else "anon"

        if not text:
            return []

        ttr = _compute_lexical_richness(text)
        avg_sl = _avg_sentence_len(text)
        word_count = len(text.split())
        upper_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        exclamation_rate = text.count("!") / max(word_count, 1)

        # Fingerprint hash for deduplication
        fp_input = f"{ttr:.4f}:{avg_sl:.2f}:{upper_ratio:.4f}:{exclamation_rate:.4f}"
        fp_hash = hashlib.sha256(fp_input.encode()).hexdigest()

        out = [{
            "handle_id": handle_id,
            "lexical_richness": ttr,
            "avg_sentence_length": avg_sl,
            "word_count": word_count,
            "upper_ratio": round(upper_ratio, 4),
            "exclamation_rate": round(exclamation_rate, 4),
            "cognitive_fingerprint": fp_hash,
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("cognitive_fingerprinted", handle=handle_id, ttr=ttr,
                    avg_sl=avg_sl, correlation_id=cid)
        return out
