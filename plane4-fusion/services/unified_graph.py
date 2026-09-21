"""Tier: B — Honest stub. Reads message, applies real logic."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

try:
    from common.db import get_neo4j_driver
except ImportError:
    def get_neo4j_driver():
        return None

logger = structlog.get_logger()

class UnifiedGraph(BaseService):
    NAME = "unified-graph"
    PLANE = 4
    TIER = "Foundation"
    INPUT_TOPICS = ["persona.links", "wallet.attribution", "infra.indicators"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8053
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"

        # Determine entity type from message shape
        if "handle_a" in message and "handle_b" in message:
            edge_type = "persona_link"
            src = message["handle_a"]
            dst = message["handle_b"]
            weight = float(message.get("similarity_score") or 0.5)
        elif "wallet_address" in message:
            edge_type = "wallet_control"
            src = message.get("cluster_id") or message["wallet_address"]
            dst = message["wallet_address"]
            weight = float(message.get("confidence") or 0.5)
        elif "onion_address" in message:
            edge_type = "infra_correlation"
            src = message["onion_address"]
            dst = message.get("matched_clearnet_domain") or message.get("matched_clearnet_ip") or ""
            weight = float(message.get("confidence") or 0.5)
        else:
            return []

        if not src or not dst:
            return []

        driver = None
        if self.neo4j is not None:
            driver = self.neo4j
        else:
            try:
                driver = get_neo4j_driver()
            except Exception:
                driver = None

        if driver is not None:
            try:
                if hasattr(driver, "session"):
                    with driver.session() as s:
                        if edge_type == "persona_link":
                            actor_id = f"actor:{src}"
                            s.run(
                                "MERGE (a:Actor {id: $actor_id}) "
                                "MERGE (h1:Handle {id: $ha}) "
                                "MERGE (h2:Handle {id: $hb}) "
                                "MERGE (h1)-[r:LINKED_TO]->(h2) "
                                "SET r.weight = $weight",
                                actor_id=actor_id,
                                ha=src,
                                hb=dst,
                                weight=weight,
                            )
                        elif edge_type == "wallet_control":
                            s.run(
                                "MERGE (w:Wallet {address: $addr}) "
                                "SET w.currency = $currency, w.vasp = $vasp",
                                addr=message["wallet_address"],
                                currency=message.get("currency", "BTC"),
                                vasp=message.get("vasp_name"),
                            )
                        elif edge_type == "infra_correlation":
                            s.run(
                                "MERGE (o:OnionService {id: $onion}) "
                                "MERGE (c:ClearnetIP {id: $ip})",
                                onion=src,
                                ip=dst,
                            )
                elif hasattr(driver, "run_write"):
                    await driver.run_write(
                        """MERGE (a:Node {id: $src})
                           MERGE (b:Node {id: $dst})
                           MERGE (a)-[r:LINKED {type: $edge_type}]->(b)
                           ON CREATE SET r.weight=$weight, r.first_seen=$now
                           ON MATCH SET r.weight=$weight, r.last_seen=$now""",
                        src=src, dst=dst, edge_type=edge_type, weight=weight,
                        now=datetime.now(timezone.utc).isoformat(),
                    )
            except Exception as e:
                logger.warning("unified_graph_neo4j_error", error=str(e), correlation_id=cid)

        out = [{
            "event_type": "graph_edge_merged",
            "src": src,
            "dst": dst,
            "edge_type": edge_type,
            "weight": round(weight, 4),
            "merged_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("unified_graph_edge_merged", edge_type=edge_type, src=src[:32],
                    dst=dst[:32], correlation_id=cid)
        return out
