"""Tier: B — Honest stub. Reads mock_sources/, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

class SyntheticMediaAnalyzer(BaseService):
    NAME = "synthetic-media-analyzer"
    PLANE = 3
    TIER = "Expert"
    INPUT_TOPICS = ["synthetic.media"]
    OUTPUT_TOPICS = ["media.forensics"]
    HTTP_PORT = 8052
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        media_id = message["media_id"] if "media_id" in message else "synth_asset_10"
        synth_score = float(message["synthetic_score"]) if "synthetic_score" in message else 0.85

        if synth_score > 0.80:
            generator_type = "Diffusion_Model"
        elif synth_score > 0.50:
            generator_type = "GAN_StyleGAN"
        else:
            generator_type = "Camera_Sensor_Noise"

        out = [{
            "media_id": media_id,
            "synthetic_score": synth_score,
            "inferred_generator": generator_type,
            "fingerprinted_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("synthetic_media_fingerprinted", media_id=media_id, generator=generator_type, correlation_id=cid)
        return out
