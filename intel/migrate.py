"""Checksummed, transactional PostgreSQL migrations."""
from pathlib import Path
from demo.common import digest

def migrate(conn):
    conn.execute('SELECT pg_advisory_xact_lock(424249)')
    conn.execute('CREATE TABLE IF NOT EXISTS intel_schema_migrations(version TEXT PRIMARY KEY,sha256 CHAR(64) NOT NULL,applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())')
    for path in sorted(Path('/app/intel/migrations').glob('*.sql')):
        body=path.read_text(encoding='utf-8-sig')
        sha=digest(body.encode())
        row=conn.execute('SELECT sha256 FROM intel_schema_migrations WHERE version=%s',(path.name,)).fetchone()
        if row:
            if row[0]!=sha:
                raise RuntimeError('Applied migration was modified: '+path.name)
            continue
        conn.execute(body)
        conn.execute('INSERT INTO intel_schema_migrations(version,sha256) VALUES (%s,%s)',(path.name,sha))
