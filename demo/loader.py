"""Fixture loader only. Reference: DEMO-DATA-CONTRACT.md section 1."""
import io
from argon2 import PasswordHasher
from .common import *
from .graph import seed_graph

def load():
    client = objects()
    with db() as conn:
        conn.execute('SELECT pg_advisory_xact_lock(424245)')
        for user in json.loads((DATA/'demo_users.json').read_text())['users']:
            conn.execute('INSERT INTO users(username,role,password_hash,mfa_secret) VALUES (%s,%s,%s,%s) ON CONFLICT(username) DO NOTHING',
                         (user['username'],user['role'],PasswordHasher().hash(user['password']),user['mfa_secret']))
        posts = json.loads((DATA/'forum_posts.json').read_text())
        for post in posts:
            body = canonical(post)
            sha = digest(body)
            key = 'fixtures/posts/' + sha + '.json'
            client.put_object('raw-crawl',key,io.BytesIO(body),len(body),content_type='application/json')
            response = client.get_object('raw-crawl',key)
            try:
                if digest(response.read()) != sha:
                    raise ValueError('Object hash mismatch')
            finally:
                response.close()
                response.release_conn()
            event = envelope('crawl.raw',dict(sha256=sha,minio_bucket='raw-crawl',minio_key=key,captured_at=post['posted_at'],source_url='fixture://forum_posts/'+sha))
            queue(conn,'crawl.raw',event)
        for name,topic in [('onion_scans.json','scan.raw'),('blockchain_txs.json','chain.tx')]:
            for record in json.loads((DATA/name).read_text()):
                queue(conn,topic,envelope(topic,record))
        ident = digest(canonical(posts))
        if conn.execute("INSERT INTO processed VALUES ('fixture-loader',%s) ON CONFLICT DO NOTHING RETURNING event_id",(ident,)).fetchone():
            audit(conn,'fixtures_loaded',ident,ident)
    p = producer()
    try:
        flush_outbox(p)
    finally:
        p.close(timeout=5)
    return {'posts':len(posts),'graph':seed_graph()}
