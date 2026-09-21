"""Integration test: Fusion & Knowledge Graph Pipeline.
Asserts:
- persona.links → Actor + Handle nodes in Neo4j
- wallet.attribution → Wallet node in Neo4j
- idempotency verified (same input processed twice produces no duplicate nodes)
"""
import sys
import os
import importlib
import pytest

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

UnifiedGraph = importlib.import_module("plane4-fusion.services.unified_graph").UnifiedGraph


class MockNeo4jSession:
    def __init__(self, graph_store):
        self.graph = graph_store

    def run(self, query, **params):
        q = query.strip()
        if "MERGE (a:Actor" in q:
            actor_id = params.get("actor_id")
            if actor_id:
                self.graph["actors"].add(actor_id)

        if "MERGE (h:Handle" in q or "MERGE (h1:Handle" in q:
            h_id = params.get("h_id") or params.get("ha")
            if h_id:
                self.graph["handles"].add(h_id)
            h2 = params.get("hb")
            if h2:
                self.graph["handles"].add(h2)

        if "MERGE (w:Wallet" in q:
            addr = params.get("addr")
            if addr:
                self.graph["wallets"].add(addr)

        if "MERGE (o:OnionService" in q:
            onion = params.get("onion")
            if onion:
                self.graph["onion_services"].add(onion)

        if "MERGE (c:ClearnetIP" in q:
            ip = params.get("ip")
            if ip:
                self.graph["clearnet_ips"].add(ip)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockNeo4jDriver:
    def __init__(self, graph_store):
        self.graph = graph_store

    def session(self):
        return MockNeo4jSession(self.graph)

    def close(self):
        pass


@pytest.mark.asyncio
async def test_fusion_persona_links_graph_nodes(monkeypatch):
    graph_store = {
        "actors": set(),
        "handles": set(),
        "wallets": set(),
        "onion_services": set(),
        "clearnet_ips": set(),
    }
    monkeypatch.setattr(
        "plane4-fusion.services.unified_graph.get_neo4j_driver",
        lambda: MockNeo4jDriver(graph_store),
    )

    service = UnifiedGraph()
    msg = {
        "handle_a": "actor_alpha",
        "handle_b": "actor_beta",
        "similarity_score": 0.94,
    }

    # First pass
    outputs = await service.handle(msg)
    assert len(outputs) == 1
    assert "actor:actor_alpha" in graph_store["actors"]
    assert "actor_alpha" in graph_store["handles"]
    assert "actor_beta" in graph_store["handles"]

    # Idempotency check: process same input again
    outputs2 = await service.handle(msg)
    assert len(graph_store["actors"]) == 1
    assert len(graph_store["handles"]) == 2


@pytest.mark.asyncio
async def test_fusion_wallet_attribution_graph_node(monkeypatch):
    graph_store = {
        "actors": set(),
        "handles": set(),
        "wallets": set(),
        "onion_services": set(),
        "clearnet_ips": set(),
    }
    monkeypatch.setattr(
        "plane4-fusion.services.unified_graph.get_neo4j_driver",
        lambda: MockNeo4jDriver(graph_store),
    )

    service = UnifiedGraph()
    msg = {
        "wallet_address": "1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q",
        "currency": "BTC",
        "vasp_name": "Binance",
    }

    # First pass
    outputs = await service.handle(msg)
    assert len(outputs) == 1
    assert "1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q" in graph_store["wallets"]

    # Idempotency check: process identical input again
    await service.handle(msg)
    assert len(graph_store["wallets"]) == 1
