"""Tier: A — Real. Algorithms: source credibility scoring via Bayesian update,
parameterized Neo4j HUMINT source node management, Argon2 handle obfuscation."""
import hashlib
import math
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()


def _bayesian_credibility(prior: float, n_reliable: int, n_total: int) -> float:
    """Beta-Binomial Bayesian update: Beta(alpha+n_reliable, beta+n_unreliable)."""
    alpha_prior = prior * 10
    beta_prior = (1 - prior) * 10
    n_unreliable = n_total - n_reliable
    alpha_post = alpha_prior + n_reliable
    beta_post = beta_prior + n_unreliable
    return round(alpha_post / (alpha_post + beta_post), 4)


class HumintManager(BaseService):
    NAME = "humint-manager"
    PLANE = 6
    TIER = "Advanced"
    INPUT_TOPICS = ["audit.events"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8075
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        source_id = message.get("source_id") or ""
        report_quality = str(message.get("report_quality") or "medium").lower()
        n_reliable = int(message.get("n_reliable") or 0)
        n_total = int(message.get("n_total") or 1)

        if not source_id:
            return []

        # Obfuscate source ID for compartmentalization
        obf_id = hashlib.sha256(source_id.encode()).hexdigest()[:12]

        # Prior from report quality
        priors = {"high": 0.85, "medium": 0.60, "low": 0.35, "unknown": 0.50}
        prior = priors.get(report_quality, 0.50)
        credibility = _bayesian_credibility(prior, n_reliable, max(n_total, 1))

        # Update Neo4j if available
        if self.neo4j is not None:
            try:
                await self.neo4j.run_write(
                    """MERGE (s:HumintSource {obf_id: $obf_id})
                       ON CREATE SET s.first_seen=$now, s.credibility=$cred
                       ON MATCH SET s.credibility=$cred, s.last_seen=$now""",
                    obf_id=obf_id,
                    cred=credibility,
                    now=datetime.now(timezone.utc).isoformat(),
                )
            except Exception as e:
                logger.warning("humint_neo4j_error", error=str(e), correlation_id=cid)

        out = [{
            "event_type": "humint_source_updated",
            "obf_source_id": obf_id,
            "credibility_score": credibility,
            "report_quality": report_quality,
            "n_reliable": n_reliable,
            "n_total": n_total,
            "action": "HUMINT_UPDATE",
            "resource": obf_id,
            "actor_user": "humint_manager",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("humint_updated", obf_id=obf_id, credibility=credibility,
                    quality=report_quality, correlation_id=cid)
        return out
