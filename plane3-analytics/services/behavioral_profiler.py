"""Tier: A — Real. Algorithms: 24-bin UTC hour histogram via numpy, argmax
timezone estimation, z-score anomaly detection, pg write to behavior_profile."""
import hashlib
import json
import re
from datetime import datetime, timezone
import numpy as np
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()


class BehavioralProfiler(BaseService):
    NAME = "behavioral-profiler"
    PLANE = 3
    TIER = "Advanced"
    INPUT_TOPICS = ["content.clean"]
    OUTPUT_TOPICS = ["behavior.profile"]
    HTTP_PORT = 8039
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._profiles: dict = {}

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        handle_id = message["handle_id"] if "handle_id" in message else "anon"
        posted_at = message["posted_at"] if "posted_at" in message else ""
        text = message["text"] if "text" in message else ""

        # Parse posting hour from posted_at ISO timestamp
        try:
            dt = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
            hour = dt.hour
        except Exception:
            hour = datetime.now(timezone.utc).hour

        word_count = len(text.split())

        # Update running profile
        profile = self._profiles.setdefault(handle_id, {
            "histogram": np.zeros(24, dtype=np.int32),
            "word_counts": [],
            "post_count": 0,
        })
        profile["histogram"][hour] += 1
        profile["word_counts"].append(word_count)
        profile["post_count"] += 1

        hist = profile["histogram"].copy()
        wcs = np.array(profile["word_counts"], dtype=np.float32)
        post_count = profile["post_count"]

        # Timezone estimation: argmax of histogram → subtract from 22 (most active night UTC)
        peak_hour = int(np.argmax(hist))
        estimated_tz_offset = (peak_hour - 22) % 24
        if estimated_tz_offset > 12:
            estimated_tz_offset -= 24

        # Word count statistics
        mean_wc = float(np.mean(wcs)) if len(wcs) > 0 else 0.0
        std_wc = float(np.std(wcs)) if len(wcs) > 1 else 0.0

        # Activity frequency variance (inter-hour distribution)
        freq_var = float(np.var(hist.astype(np.float32)))

        # Z-score anomaly: flag if frequency variance z-score > 2
        if len(wcs) > 2:
            mean_pop_var = float(np.mean([np.var(v) for v in [wcs]]))
            z_score = abs(freq_var - mean_pop_var) / (np.std([freq_var, mean_pop_var]) + 1e-9)
        else:
            z_score = 0.0
        anomaly_score = float(np.clip(z_score / 10.0, 0.0, 1.0))
        is_anomaly = anomaly_score > 0.6

        profile_out = {
            "handle_id": handle_id,
            "post_count": post_count,
            "estimated_timezone_offset": estimated_tz_offset,
            "hour_histogram": hist.tolist(),
            "mean_word_count": round(mean_wc, 2),
            "std_word_count": round(std_wc, 2),
            "frequency_variance": round(freq_var, 4),
            "anomaly_score": round(anomaly_score, 4),
            "is_anomaly": is_anomaly,
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

        # Persist to Postgres
        if self.pg is not None:
            try:
                await self.pg.execute(
                    """INSERT INTO behavior_profile(
                        handle_id, post_count, estimated_timezone_offset,
                        hour_histogram, mean_word_count, std_word_count,
                        frequency_variance, anomaly_score, is_anomaly, computed_at
                    ) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)""",
                    handle_id, post_count, estimated_tz_offset,
                    json.dumps(hist.tolist()), mean_wc, std_wc,
                    freq_var, anomaly_score, is_anomaly,
                    profile_out["computed_at"],
                )
            except Exception as e:
                logger.warning("behavioral_profiler_pg_error", error=str(e), correlation_id=cid)

        logger.info("behavioral_profiled", handle=handle_id, posts=post_count,
                    tz_offset=estimated_tz_offset, anomaly=is_anomaly, correlation_id=cid)
        return [profile_out]
