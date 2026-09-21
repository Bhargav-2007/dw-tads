"""Tier: A — Real. Algorithms: union-find with path compression and union by
rank (Tarjan-Cormen). Writes cluster results to wallet_clusters Postgres table."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()


class UnionFind:
    """Weighted union-find with path compression and union by rank."""

    def __init__(self):
        self.parent: dict[str, str] = {}
        self.rank: dict[str, int] = {}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: str, y: str):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1

    def clusters(self) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for node in self.parent:
            root = self.find(node)
            result.setdefault(root, []).append(node)
        return result


class BlockchainClusterer(BaseService):
    NAME = "blockchain-clusterer"
    PLANE = 4
    TIER = "Advanced"
    INPUT_TOPICS = ["chain.tx"]
    OUTPUT_TOPICS = ["wallet.attribution"]
    HTTP_PORT = 8050
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._uf: dict[str, UnionFind] = {}  # per-currency union-find

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        currency = message["currency"] if "currency" in message else "BTC"
        from_addr = message["from_address"] if "from_address" in message else ""
        to_addr = message["to_address"] if "to_address" in message else ""
        heuristic = message.get("heuristic", "common_input_ownership")

        if not from_addr or not to_addr:
            return []

        uf = self._uf.setdefault(currency, UnionFind())
        uf.union(from_addr, to_addr)

        cluster_root = uf.find(from_addr)
        cluster_members = uf.clusters().get(cluster_root, [from_addr])
        cluster_id = hashlib.sha256(f"{currency}:{cluster_root}".encode()).hexdigest()[:16]
        cluster_size = len(cluster_members)

        # Write to Postgres wallet_clusters table
        if self.pg is not None:
            try:
                await self.pg.execute(
                    """INSERT INTO wallet_clusters(cluster_id, currency, addresses, heuristic)
                       VALUES($1,$2,$3,$4)
                       ON CONFLICT (cluster_id) DO UPDATE
                       SET addresses=$3, heuristic=$4, updated_at=NOW()""",
                    cluster_id, currency, cluster_members, heuristic,
                )
            except Exception as e:
                logger.warning("blockchain_clusterer_pg_error", error=str(e),
                               correlation_id=cid)

        out = [{
            "wallet_address": from_addr,
            "cluster_id": cluster_id,
            "cluster_size": cluster_size,
            "vasp_name": None,
            "kyc_traceable": None,
            "currency": currency,
            "heuristic": heuristic,
            "confidence": min(1.0, 0.60 + min(cluster_size, 50) / 100.0),
            "correlation_id": cid,
        }]
        logger.info("blockchain_clustered", currency=currency, cluster_id=cluster_id,
                    size=cluster_size, correlation_id=cid)
        return out
