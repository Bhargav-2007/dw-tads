"""Tier: A — Real. Algorithms: parameterized Neo4j MERGE for all entity types.
F-string Cypher forbidden. All parameters passed via named $params."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

ENTITY_CYPHER = {
    "btc_address": """
        MERGE (a:WalletAddress {value: $value, currency: "BTC"})
        ON CREATE SET a.first_seen = $now, a.source = $source
        ON MATCH SET a.last_seen = $now
        MERGE (h:ThreatActor {id: $handle_id})
        ON CREATE SET h.first_seen = $now
        MERGE (h)-[:CONTROLS]->(a)
        RETURN a.value AS entity, "btc_address" AS type
    """,
    "eth_address": """
        MERGE (a:WalletAddress {value: $value, currency: "ETH"})
        ON CREATE SET a.first_seen = $now, a.source = $source
        ON MATCH SET a.last_seen = $now
        MERGE (h:ThreatActor {id: $handle_id})
        MERGE (h)-[:CONTROLS]->(a)
        RETURN a.value AS entity, "eth_address" AS type
    """,
    "xmr_address": """
        MERGE (a:WalletAddress {value: $value, currency: "XMR"})
        ON CREATE SET a.first_seen = $now, a.source = $source
        ON MATCH SET a.last_seen = $now
        MERGE (h:ThreatActor {id: $handle_id})
        MERGE (h)-[:CONTROLS]->(a)
        RETURN a.value AS entity, "xmr_address" AS type
    """,
    "domain": """
        MERGE (d:Domain {value: $value})
        ON CREATE SET d.first_seen = $now, d.source = $source
        ON MATCH SET d.last_seen = $now
        MERGE (h:ThreatActor {id: $handle_id})
        MERGE (h)-[:ASSOCIATED_WITH]->(d)
        RETURN d.value AS entity, "domain" AS type
    """,
    "ipv4": """
        MERGE (i:IPAddress {value: $value})
        ON CREATE SET i.first_seen = $now, i.source = $source
        ON MATCH SET i.last_seen = $now
        RETURN i.value AS entity, "ipv4" AS type
    """,
    "onion_v3": """
        MERGE (o:OnionService {address: $value})
        ON CREATE SET o.first_seen = $now, o.source = $source
        ON MATCH SET o.last_seen = $now
        RETURN o.address AS entity, "onion_v3" AS type
    """,
}


class EntityResolver(BaseService):
    NAME = "entity-resolver"
    PLANE = 4
    TIER = "Advanced"
    INPUT_TOPICS = ["actor.entities"]
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8048
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        handle_id = message["handle_id"] if "handle_id" in message else "anon"
        entities = message["entities"] if "entities" in message else []
        source = message["platform"] if "platform" in message else "unknown"

        now = datetime.now(timezone.utc).isoformat()
        resolved = []

        for ent in entities:
            ent_type = ent.get("type", "")
            ent_value = ent.get("value", "")
            if not ent_value or ent_type not in ENTITY_CYPHER:
                continue

            cypher = ENTITY_CYPHER[ent_type]

            if self.neo4j is not None:
                try:
                    rows = await self.neo4j.run(
                        cypher,
                        value=ent_value,
                        handle_id=handle_id,
                        now=now,
                        source=source,
                    )
                    if rows:
                        resolved.append({
                            "entity": rows[0].get("entity", ent_value),
                            "type": ent_type,
                            "resolved": True,
                        })
                except Exception as e:
                    logger.warning("entity_resolver_neo4j_error", error=str(e),
                                   entity=ent_value[:32], correlation_id=cid)
                    resolved.append({"entity": ent_value, "type": ent_type, "resolved": False})
            else:
                resolved.append({"entity": ent_value, "type": ent_type, "resolved": False})

        out = [{
            "event_type": "entities_resolved",
            "handle_id": handle_id,
            "resolved_count": len(resolved),
            "entities": resolved,
            "resolved_at": now,
            "correlation_id": cid,
        }]
        logger.info("entity_resolved", handle=handle_id, count=len(resolved),
                    correlation_id=cid)
        return out
