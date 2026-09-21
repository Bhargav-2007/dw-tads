"""Separate persistent run database; no connection to online intelligence storage."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime,timezone
from .contracts import encode,sha

@contextmanager
def database():
    conn=sqlite3.connect(os.environ['MOCK_DATABASE'],timeout=10)
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    try:
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize():
    Path(os.environ['MOCK_DATABASE']).parent.mkdir(parents=True,exist_ok=True)
    with database() as conn:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,scenario TEXT NOT NULL,created_by TEXT NOT NULL,
            status TEXT NOT NULL,fail_service TEXT,fault_used INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,reviewed_by TEXT,decision TEXT,error TEXT);
        CREATE TABLE IF NOT EXISTS steps(run_id TEXT REFERENCES runs(id),service TEXT,response TEXT NOT NULL,
            PRIMARY KEY(run_id,service));
        CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT REFERENCES runs(id),
            event TEXT NOT NULL,actor TEXT NOT NULL,ts TEXT NOT NULL,details TEXT NOT NULL,prev_hash TEXT NOT NULL,this_hash TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS immutable_events_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS immutable_events_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
        ''')

def now():
    return datetime.now(timezone.utc).isoformat()

def audit(conn,run_id,event,actor,details):
    previous=conn.execute('SELECT this_hash FROM events ORDER BY seq DESC LIMIT 1').fetchone()
    previous=previous[0] if previous else '0'*64
    payload={'run_id':run_id,'event':event,'actor':actor,'ts':now(),'details':details,'synthetic':True}
    value=sha({'previous':previous,'payload':payload})
    conn.execute('INSERT INTO events(run_id,event,actor,ts,details,prev_hash,this_hash) VALUES (?,?,?,?,?,?,?)',
        (run_id,event,actor,payload['ts'],encode(details).decode(),previous,value))

def verify():
    import json
    previous='0'*64
    with database() as conn:
        rows=conn.execute('SELECT * FROM events ORDER BY seq').fetchall()
    for row in rows:
        payload={k:row[k] for k in ['run_id','event','actor','ts']}
        payload.update(details=json.loads(row['details']),synthetic=True)
        if previous!=row['prev_hash'] or sha({'previous':previous,'payload':payload})!=row['this_hash']:
            return False
        previous=row['this_hash']
    return True
