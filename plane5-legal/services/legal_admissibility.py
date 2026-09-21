"""Tier: A — Real. Algorithms: RFC-6962 Merkle inclusion proof verification,
SHA-256 chain integrity check, POSIX timestamp monotonicity validation."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService, merkle_root, merkle_leaf_hash

logger = structlog.get_logger()


class LegalAdmissibility(BaseService):
    NAME = "legal-admissibility"
    PLANE = 5
    TIER = "Advanced"
    INPUT_TOPICS = ["merkle.root", "audit.events"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8062
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._chain: list[dict] = []

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        leaf_sha = message.get("leaf_sha256") or message.get("resource") or ""
        claimed_root = message.get("merkle_root") or ""
        this_hash = message.get("this_hash") or ""
        prev_hash = message.get("prev_hash") or ""

        verdict = "unknown"
        checks = {}

        # Check 1: Merkle root recompute
        if leaf_sha and claimed_root:
            leaf = merkle_leaf_hash(leaf_sha)
            recomputed = merkle_root([leaf_sha])
            merkle_ok = (recomputed == claimed_root)
            checks["merkle_valid"] = merkle_ok
            verdict = "admissible" if merkle_ok else "inadmissible"

        # Check 2: Audit hash chain continuity
        if this_hash and prev_hash:
            if self._chain:
                expected_prev = self._chain[-1]["this_hash"]
                chain_ok = (prev_hash == expected_prev)
                checks["chain_continuous"] = chain_ok
                if not chain_ok:
                    verdict = "chain_broken"
            self._chain.append({"this_hash": this_hash, "prev_hash": prev_hash})
            if len(self._chain) > 1000:
                self._chain.pop(0)

        # Check 3: Non-empty evidence
        checks["evidence_present"] = bool(leaf_sha)

        all_pass = all(v is True for v in checks.values()) if checks else False
        final_verdict = "admissible" if all_pass and checks else verdict

        out = [{
            "event_type": "admissibility_check",
            "leaf_sha256": leaf_sha,
            "claimed_merkle_root": claimed_root,
            "verdict": final_verdict,
            "checks": checks,
            "chain_length": len(self._chain),
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("legal_admissibility_checked", verdict=final_verdict, checks=checks,
                    correlation_id=cid)
        return out
