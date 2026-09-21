"""Tier: A — Real. Algorithms: union-find + heuristic clustering."""
import hashlib
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

class UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}
    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1

class BlockchainClusterer(BaseService):
    NAME = "blockchain-clusterer"
    PLANE = 3
    TIER = "Intermediate"
    INPUT_TOPICS = ["chain.tx"]
    OUTPUT_TOPICS = ["wallet.attribution"]
    HTTP_PORT = 8039
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.uf = UnionFind()

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        currency = message["currency"] if "currency" in message else "BTC"
        raw_inputs = message["from_addresses"] if "from_addresses" in message else [message["from_address"] if "from_address" in message else "1InputAddrDefault"]
        raw_outputs = message["to_addresses"] if "to_addresses" in message else [message["to_address"] if "to_address" in message else "1OutputAddrDefault"]
        amounts = message["output_amounts"] if "output_amounts" in message else []

        inputs = [a for a in raw_inputs if a]
        outputs = [a for a in raw_outputs if a]

        # Heuristic 1: common input ownership
        for i in range(1, len(inputs)):
            self.uf.union(inputs[0], inputs[i])

        # Heuristic 2: change address
        if len(outputs) == 2:
            matching = [o for o in outputs if o in inputs]
            non_matching = [o for o in outputs if o not in inputs]
            if len(matching) == 1 and len(non_matching) == 1:
                self.uf.union(inputs[0], non_matching[0])

        # Heuristic 3: CoinJoin detection
        is_coinjoin = (len(inputs) >= 3 and len(outputs) >= 3 and len(amounts) >= 3 and len(set(amounts)) < len(amounts))

        root = self.uf.find(inputs[0])
        cluster_members = sorted([k for k in self.uf.parent if self.uf.find(k) == root])
        cluster_id = "cluster:" + hashlib.sha256(",".join(cluster_members).encode()).hexdigest()[:12]

        heuristic = "coinjoin" if is_coinjoin else ("change_address" if len(outputs) == 2 else "common_input_ownership")
        conf = 0.50 if is_coinjoin else 0.90

        out = [{
            "wallet_address": inputs[0],
            "cluster_id": cluster_id,
            "cluster_size": len(cluster_members),
            "currency": currency,
            "heuristic": heuristic,
            "confidence": conf,
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("wallet_clustered", cluster_id=cluster_id, size=len(cluster_members), correlation_id=cid)
        return out
