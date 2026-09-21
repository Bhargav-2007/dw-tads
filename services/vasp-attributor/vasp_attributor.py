"""Tier: A — Real. Algorithms: SQLite vasp_index.db exact address lookup
(GraphSense tagpack data). Returns confidence 0.95 on match, 0.30 on miss."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

VASP_DB = Path("/var/lib/dwtds/vasp_index.db")


class VaspAttributor(BaseService):
    NAME = "vasp-attributor"
    PLANE = 4
    TIER = "Advanced"
    INPUT_TOPICS = ["wallet.attribution"]
    OUTPUT_TOPICS = ["wallet.attribution"]
    HTTP_PORT = 8051
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        wallet = message["wallet_address"] if "wallet_address" in message else ""
        currency = message["currency"] if "currency" in message else "BTC"
        cluster_id = message.get("cluster_id")
        cluster_size = int(message.get("cluster_size") or 1)

        if not wallet:
            return []

        vasp_name = None
        kyc_traceable = None
        confidence = 0.30

        if VASP_DB.exists():
            try:
                conn = sqlite3.connect(str(VASP_DB))
                cur = conn.cursor()
                cur.execute(
                    "SELECT vasp_name, kyc_traceable FROM vasp_index "
                    "WHERE address=? AND currency=? LIMIT 1",
                    (wallet, currency)
                )
                row = cur.fetchone()
                conn.close()
                if row:
                    vasp_name = row[0]
                    kyc_traceable = bool(row[1])
                    confidence = 0.95
            except Exception as e:
                logger.warning("vasp_attributor_db_error", error=str(e), correlation_id=cid)
        else:
            # Cluster-size heuristic: large clusters → exchange likely
            if cluster_size > 1000:
                confidence = 0.55
            elif cluster_size > 100:
                confidence = 0.40

        out = [{
            "wallet_address": wallet,
            "cluster_id": cluster_id,
            "cluster_size": cluster_size,
            "vasp_name": vasp_name,
            "kyc_traceable": kyc_traceable,
            "currency": currency,
            "heuristic": message.get("heuristic", "unknown"),
            "confidence": round(confidence, 3),
            "correlation_id": cid,
        }]
        logger.info("vasp_attributed", wallet=wallet[:16], vasp=vasp_name,
                    confidence=confidence, correlation_id=cid)
        return out
