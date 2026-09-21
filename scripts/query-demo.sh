#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== DW-TADS Demo State & Attribution Query ==="

python3 - <<'EOF'
import sys, os, json
from pathlib import Path
from common.db import get_neo4j_driver

def query_live():
    try:
        driver = get_neo4j_driver()
        with driver.session() as s:
            actors = s.run("MATCH (a:Actor) RETURN a.actor_id AS id").data()
            print(f"\n--- Graph State (Live Neo4j) ---")
            print(f"Total Actors: {len(actors)}")
            for a in actors:
                print(f"  Actor: {a['id']}")
            node_count = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
            edge_count = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
            print(f"Total Nodes: {node_count}, Total Relationships: {edge_count}")
        driver.close()
        return True
    except Exception as e:
        return False

if not query_live():
    p = Path("tests/data/seed_graph.json")
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        print(f"\n--- Graph State (Seed Demo Profile) ---")
        for actor in data.get("actors", []):
            print(f"Actor: {actor.get('actor_id')} (Risk Score: {actor.get('risk_score')}, Categories: {actor.get('category')})")
        print(f"\nNode Counts:")
        print(f"  Actors: {len(data.get('actors', []))}")
        print(f"  Handles: {len(data.get('handles', []))}")
        print(f"  Wallets: {len(data.get('wallets', []))}")
        print(f"  Onion Services: {len(data.get('onion_services', []))}")
        print(f"  Clearnet IPs: {len(data.get('clearnet_ips', []))}")
        print(f"Total Edges: {len(data.get('edges', []))}")
EOF
