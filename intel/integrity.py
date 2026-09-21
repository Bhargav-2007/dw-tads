"""Technical record history and domain-separated SHA-256 Merkle proofs."""
from .common import db,objects,BUCKET,canonical,digest,Jsonb,audit,json
from .normalize import parse


def leaf(record):
    return digest(b'\x00'+canonical(record))

def parent(a,b):
    return digest(b'\x01'+bytes.fromhex(a)+bytes.fromhex(b))

def root(leaves):
    if not leaves:
        raise ValueError('An empty tree has no root')
    level=list(leaves)
    while len(level)>1:
        if len(level)%2:
            level.append(level[-1])
        level=[parent(level[i],level[i+1]) for i in range(0,len(level),2)]
    return level[0]

def proof(leaves,index):
    if not 0<=index<len(leaves):
        raise ValueError('Leaf index out of bounds')
    steps=[]
    level=list(leaves)
    while len(level)>1:
        if len(level)%2:
            level.append(level[-1])
        steps.append({'side':'left' if index%2 else 'right','hash':level[index^1]})
        level=[parent(level[i],level[i+1]) for i in range(0,len(level),2)]
        index//=2
    return steps

def verify_proof(record,steps,expected_root):
    result=leaf(record)
    for step in steps:
        if step['side'] not in ('left','right'):
            raise ValueError('Invalid proof direction')
        result=parent(step['hash'],result) if step['side']=='left' else parent(result,step['hash'])
    return result==expected_root

def archive(conn,sha,records,edges,cid):
    if conn.execute('SELECT 1 FROM intel_merkle_anchors WHERE snapshot_sha=%s',(sha,)).fetchone():
        return
    ordered=sorted(records,key=lambda r:r['id'])
    hashes=[leaf(r) for r in ordered]
    with conn.cursor() as cur:
        cur.executemany('INSERT INTO intel_record_versions(id,snapshot_sha,source,payload,leaf_hash) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',
            [(r['id'],sha,r['source'],Jsonb(r),h) for r,h in zip(ordered,hashes)])
        cur.executemany('INSERT INTO intel_relationship_versions VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING',
            [(e['source_id'],e['target_id'],e['type'],sha) for e in edges])
    conn.execute('INSERT INTO intel_merkle_anchors(snapshot_sha,root,leaf_count) VALUES (%s,%s,%s)',(sha,root(hashes),len(hashes)))
    audit(conn,'snapshot_merkle_anchored',sha,cid)

def backfill():
    with db() as conn:
        conn.execute('SELECT pg_advisory_xact_lock(424248)')
        rows=conn.execute('SELECT s.sha256,s.source,s.object_key,s.object_version FROM intel_snapshots s LEFT JOIN intel_merkle_anchors a ON a.snapshot_sha=s.sha256 WHERE s.processed_at IS NOT NULL AND a.snapshot_sha IS NULL ORDER BY s.captured_at').fetchall()
        client=objects()
        for sha,source,key,version in rows:
            response=client.get_object(BUCKET,key,version_id=version)
            try:
                body=response.read()
            finally:
                response.close(); response.release_conn()
            if digest(body)!=sha:
                raise ValueError('Stored snapshot failed history backfill integrity check: '+sha)
            records,edges=parse(source,json.loads(body))
            archive(conn,sha,records,edges,'history-backfill')
    return len(rows)
