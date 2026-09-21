"""Tier: B — Honest stub. Reads message, applies real logic.
Tier A upgrade: loads NLLB-200 model from /models/nllb/ if present;
degrades gracefully (language detection only) if model absent."""
import hashlib
import re
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

# Simplified language detection heuristics
LANG_PATTERNS = {
    "ru": re.compile(r"[\u0400-\u04FF]{3,}", re.UNICODE),
    "zh": re.compile(r"[\u4E00-\u9FFF]{2,}", re.UNICODE),
    "ar": re.compile(r"[\u0600-\u06FF]{3,}", re.UNICODE),
    "de": re.compile(r"\b(und|das|die|der|ein|ist|nicht|mit|für)\b", re.IGNORECASE),
    "fr": re.compile(r"\b(le|la|les|un|une|des|et|est|pas|pour)\b", re.IGNORECASE),
    "es": re.compile(r"\b(el|la|los|las|un|una|y|es|no|para)\b", re.IGNORECASE),
}


class MultilingualNlp(BaseService):
    NAME = "multilingual-nlp"
    PLANE = 3
    TIER = "Advanced"
    INPUT_TOPICS = ["content.clean"]
    OUTPUT_TOPICS = ["content.clean"]
    HTTP_PORT = 8044
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._nllb = None
        self._nllb_loaded = False

    def _try_load_nllb(self):
        from pathlib import Path
        model_path = Path("/models/nllb")
        if not model_path.exists():
            return
        try:
            from transformers import pipeline as hf_pipeline
            self._nllb = hf_pipeline("translation", model=str(model_path),
                                     device=-1, max_length=512)
            self._nllb_loaded = True
            logger.info("nllb_model_loaded", path=str(model_path))
        except Exception as e:
            logger.warning("nllb_load_failed", error=str(e))

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        text = message["text"] if "text" in message else ""
        handle_id = message["handle_id"] if "handle_id" in message else "anon"
        platform = message["platform"] if "platform" in message else "unknown"
        source_sha = message["source_sha256"] if "source_sha256" in message else ""

        if not text:
            return []

        # Language detection
        detected_lang = "en"
        lang_confidence = 0.50
        for lang_code, pattern in LANG_PATTERNS.items():
            if pattern.search(text):
                detected_lang = lang_code
                match_count = len(pattern.findall(text))
                lang_confidence = min(1.0, 0.60 + match_count * 0.05)
                break

        # Translation (Tier A: use NLLB; Tier B: pass through)
        if not self._nllb_loaded:
            self._try_load_nllb()

        translated_text = text
        if detected_lang != "en" and self._nllb is not None:
            try:
                result = self._nllb(text[:512],
                                    src_lang=detected_lang,
                                    tgt_lang="eng_Latn")
                translated_text = result[0]["translation_text"]
            except Exception as e:
                logger.warning("nllb_translate_error", error=str(e), correlation_id=cid)

        out = [{
            "handle_id": handle_id,
            "platform": platform,
            "text": translated_text,
            "posted_at": message.get("posted_at", datetime.now(timezone.utc).isoformat()),
            "source_sha256": source_sha,
            "detected_language": detected_lang,
            "lang_confidence": round(lang_confidence, 3),
            "was_translated": translated_text != text,
            "correlation_id": cid,
        }]
        logger.info("multilingual_nlp_processed", lang=detected_lang,
                    translated=translated_text != text, correlation_id=cid)
        return out
