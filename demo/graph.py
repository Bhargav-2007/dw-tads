"""Fixture-only graph loader. Reference: DEMO-DATA-CONTRACT.md section 4."""
from .common import *

# Identifiers in these queries are static; fixture strings are parameters only.
NODE_QUERIES = {
 'actors': ('actor_id', 'MERGE (n:Actor {actor_id:$id}) SET n += $props, n.demo_id=$id, n.synthetic=true'),
 'handles': ('handle_id', 'MERGE (n:Handle {handle_id:$id}) SET n += $props, n.demo_id=$id, n.synthetic=true'),
 'wallets': ('address', 'MERGE (n:Wallet {address:$id,currency:$currency}) SET n += $props, n.demo_id=$id, n.synthetic=true'),
 'onion_services': ('onion_address', 'MERGE (n:OnionService {onion_address:$id}) SET n += $props, n.demo_id=$id, n.synthetic=true'),
 'clearnet_ips': ('ip_address', 'MERGE (n:ClearnetIP {ip_address:$id}) SET n += $props, n.demo_id=$id, n.synthetic=true'),
 'pgp_keys': ('fingerprint', 'MERGE (n:PGPKey {fingerprint:$id}) SET n += $props, n.demo_id=$id, n.synthetic=true')
}
EDGE_QUERIES = {
 'HasHandle': 'MATCH (a {demo_id:$a}), (b {demo_id:$b}) MERGE (a)-[r:HasHandle]->(b) SET r += $props',
 'StylometricMatch': 'MATCH (a {demo_id:$a}), (b {demo_id:$b}) MERGE (a)-[r:StylometricMatch]->(b) SET r += $props',
 'Trusts': 'MATCH (a {demo_id:$a}), (b {demo_id:$b}) MERGE (a)-[r:Trusts]->(b) SET r += $props',
 'ControlsWallet': 'MATCH (a {demo_id:$a}), (b {demo_id:$b}) MERGE (a)-[r:ControlsWallet]->(b) SET r += $props',
 'UsesPGP': 'MATCH (a {demo_id:$a}), (b {demo_id:$b}) MERGE (a)-[r:UsesPGP]->(b) SET r += $props',
 'ResolvesTo': 'MATCH (a {demo_id:$a}), (b {demo_id:$b}) MERGE (a)-[r:ResolvesTo]->(b) SET r += $props'
}
CONSTRAINTS = [
 'CREATE CONSTRAINT actor_id IF NOT EXISTS FOR (n:Actor) REQUIRE n.actor_id IS UNIQUE',
 'CREATE CONSTRAINT handle_id IF NOT EXISTS FOR (n:Handle) REQUIRE n.handle_id IS UNIQUE',
 'CREATE CONSTRAINT wallet_addr IF NOT EXISTS FOR (n:Wallet) REQUIRE (n.address,n.currency) IS UNIQUE',
 'CREATE CONSTRAINT onion_addr IF NOT EXISTS FOR (n:OnionService) REQUIRE n.onion_address IS UNIQUE',
 'CREATE CONSTRAINT clearnet_ip IF NOT EXISTS FOR (n:ClearnetIP) REQUIRE n.ip_address IS UNIQUE',
 'CREATE CONSTRAINT pgp_fp IF NOT EXISTS FOR (n:PGPKey) REQUIRE n.fingerprint IS UNIQUE'
]

def seed_graph():
    fixture = json.loads((DATA/'seed_graph.json').read_text())
    event_id = digest(canonical(fixture))
    with db() as conn:
        conn.execute('SELECT pg_advisory_xact_lock(424244)')
        if conn.execute("SELECT 1 FROM processed WHERE consumer='graph-seed' AND event_id=%s", (event_id,)).fetchone():
            return {'seeded': False, 'reason': 'already loaded'}
        audit(conn, 'graph_seed_intent', event_id, event_id)
    with graph() as driver, driver.session() as session:
        for query in CONSTRAINTS:
            session.run(query).consume()
        def write(tx):
            for group, (key, query) in NODE_QUERIES.items():
                for node in fixture.get(group, []):
                    props = dict(node, provenance='synthetic fixture; not inferred', recorded_at='2025-04-20T00:00:00Z')
                    tx.run(query, id=node[key], currency=node.get('currency'), props=props).consume()
            for edge in fixture['edges']:
                query = EDGE_QUERIES[edge['type']]
                tx.run(query, a=edge['from'], b=edge['to'], props={'confidence':edge['confidence'], 'synthetic':True, 'provenance':'fixture assertion; not calibrated'}).consume()
        session.execute_write(write)
    with db() as conn:
        conn.execute("INSERT INTO processed VALUES ('graph-seed',%s) ON CONFLICT DO NOTHING", (event_id,))
        audit(conn, 'graph_seed_complete', event_id, event_id)
    return {'seeded': True}

def snapshot():
    with graph() as driver, driver.session() as s:
        nodes = [dict(r) for r in s.run('MATCH (n) RETURN n.demo_id AS id, labels(n)[0] AS type, properties(n) AS properties ORDER BY id')]
        edges = [dict(r) for r in s.run('MATCH (a)-[r]->(b) RETURN a.demo_id AS source,b.demo_id AS target,type(r) AS type,properties(r) AS properties')]
    return {'synthetic':True,'nodes':nodes,'edges':edges}
