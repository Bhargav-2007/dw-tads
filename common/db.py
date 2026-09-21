"""Database and infrastructure helpers for DW-TADS.
Handles Postgres, Neo4j, MinIO, Redis connections and audit ledger hash-chaining.
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional




def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def get_pg_conn():
    """Connect to Postgres using environment variables."""
    import psycopg
    return psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "dwtds"),
        user=os.getenv("PGUSER", "dwtds"),
        password=os.getenv("PGPASSWORD", "dwtds_password"),
        connect_timeout=5,
    )


def get_neo4j_driver():
    """Connect to Neo4j graph database."""
    from neo4j import GraphDatabase
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD", "dwtds_password")
    return GraphDatabase.driver(uri, auth=(user, pwd), connection_timeout=5)


def get_minio_client():
    """Connect to MinIO object store."""
    from minio import Minio
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)


def append_audit_log(
    conn,
    event_type: str,
    action: str,
    actor_user: str = "system",
    resource: Optional[str] = None,
    query_hash: Optional[str] = None,
    result_hash: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Append-only audit ledger entry with advisory locking and hash chaining.
    prev_hash -> this_hash.
    """
    from psycopg.types.json import Jsonb
    if metadata is None:
        metadata = {}
    if "ts" not in metadata:
        metadata["ts"] = utc_now()

    # Advisory lock to guarantee sequential hash continuity
    conn.execute("SELECT pg_advisory_xact_lock(424242)")

    prev_row = conn.execute(
        "SELECT this_hash FROM audit_log ORDER BY audit_id DESC LIMIT 1"
    ).fetchone()
    prev_hash = prev_row[0] if prev_row else "0" * 64

    payload = {
        "event_type": event_type,
        "actor_user": actor_user,
        "action": action,
        "resource": resource or "",
        "query_hash": query_hash or "",
        "result_hash": result_hash or "",
        "prev_hash": prev_hash,
        "metadata": metadata,
    }
    this_hash = digest(prev_hash.encode("utf-8") + canonical(payload))

    conn.execute(
        """
        INSERT INTO audit_log(event_type, actor_user, action, resource, query_hash, result_hash, prev_hash, this_hash, ts, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """,
        (
            event_type,
            actor_user,
            action,
            resource,
            query_hash,
            result_hash,
            prev_hash,
            this_hash,
            Jsonb(metadata),
        ),
    )
    return this_hash


def verify_audit_chain(conn) -> bool:
    """Verify continuity of the cryptographic audit hash chain."""
    rows = conn.execute(
        """
        SELECT audit_id, event_type, actor_user, action, resource, query_hash, result_hash, prev_hash, this_hash, metadata
        FROM audit_log
        ORDER BY audit_id ASC
        """
    ).fetchall()

    if not rows:
        return True

    expected_prev = "0" * 64
    for row in rows:
        (
            audit_id,
            event_type,
            actor_user,
            action,
            resource,
            query_hash,
            result_hash,
            prev_hash,
            this_hash,
            metadata,
        ) = row

        if prev_hash != expected_prev:
            return False

        payload = {
            "event_type": event_type,
            "actor_user": actor_user,
            "action": action,
            "resource": resource or "",
            "query_hash": query_hash or "",
            "result_hash": result_hash or "",
            "prev_hash": prev_hash,
            "metadata": metadata or {},
        }
        calculated = digest(prev_hash.encode("utf-8") + canonical(payload))
        if calculated != this_hash:
            return False

        expected_prev = this_hash

    return True


def insert_evidence(
    conn,
    sha256: str,
    source_url: str,
    source_type: str,
    captured_at: str,
    minio_bucket: str,
    minio_key: str,
    ingested_by: str,
    merkle_root: Optional[str] = None,
) -> bool:
    """Insert evidence record; returns False on duplicate sha256."""
    try:
        conn.execute(
            """
            INSERT INTO evidence (sha256, source_url, source_type, captured_at, minio_bucket, minio_key, merkle_root, ingested_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                sha256,
                source_url,
                source_type,
                captured_at,
                minio_bucket,
                minio_key,
                merkle_root,
                ingested_by,
            ),
        )
        return True
    except Exception as e:
        conn.rollback()
        return False

