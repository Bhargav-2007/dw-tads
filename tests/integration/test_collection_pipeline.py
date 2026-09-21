"""Integration test: Collection & Evidence Pipeline.
Asserts:
- load_demo_data → evidence row + audit_log
- duplicate sha256 → UNIQUE rejects
- hash chain continuous and cryptographically verifiable
"""
import sys
import os
import pytest

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import importlib
from common.base_service import utc_now, digest
from common.db import append_audit_log, verify_audit_chain, insert_evidence
EvidencePipeline = importlib.import_module("plane1-infrastructure.services.evidence_pipeline").EvidencePipeline




class MockCursor:
    def __init__(self, rows=None):
        self._rows = rows or []

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return self._rows


class MockDBConnection:
    """In-memory SQLite/Dictionary mock for Postgres testing."""
    def __init__(self):
        self.evidence = {}
        self.audit_log = []
        self.advisory_locks = []

    def execute(self, query, params=None):
        query_strip = query.strip()
        if "pg_advisory_xact_lock" in query_strip:
            self.advisory_locks.append(params)
            return MockCursor()

        if "SELECT this_hash FROM audit_log" in query_strip:
            if self.audit_log:
                last_hash = self.audit_log[-1]["this_hash"]
                return MockCursor([(last_hash,)])
            return MockCursor([])

        if "INSERT INTO audit_log" in query_strip:
            (event_type, actor_user, action, resource, query_hash, result_hash, prev_hash, this_hash, metadata) = params
            audit_id = len(self.audit_log) + 1
            meta_dict = getattr(metadata, "obj", metadata)
            if not isinstance(meta_dict, dict):
                meta_dict = {}
            row = {
                "audit_id": audit_id,
                "event_type": event_type,
                "actor_user": actor_user,
                "action": action,
                "resource": resource,
                "query_hash": query_hash,
                "result_hash": result_hash,
                "prev_hash": prev_hash,
                "this_hash": this_hash,
                "metadata": meta_dict,
            }
            self.audit_log.append(row)
            return MockCursor()

        if "SELECT audit_id, event_type" in query_strip:
            rows = [
                (
                    r["audit_id"],
                    r["event_type"],
                    r["actor_user"],
                    r["action"],
                    r["resource"],
                    r["query_hash"],
                    r["result_hash"],
                    r["prev_hash"],
                    r["this_hash"],
                    r["metadata"],
                )
                for r in self.audit_log
            ]
            return MockCursor(rows)

        if "INSERT INTO evidence" in query_strip:
            (sha256, source_url, source_type, captured_at, minio_bucket, minio_key, merkle_root, ingested_by) = params
            if sha256 in self.evidence:
                raise Exception("duplicate key value violates unique constraint")
            self.evidence[sha256] = {
                "sha256": sha256,
                "source_url": source_url,
                "source_type": source_type,
            }
            return MockCursor()

        return MockCursor()

    def commit(self):
        pass

    def rollback(self):
        pass


@pytest.mark.asyncio
async def test_evidence_pipeline_output():
    service = EvidencePipeline()
    msg = {
        "target": "darkforum1234567.onion",
        "path": "/threads",
        "text": "Fresh CVE-2025-12345 exploit available.",
        "handle_id": "actor_alpha",
        "platform": "BreachForums",
    }
    outputs = await service.handle(msg)
    assert len(outputs) == 3

    # Check content.clean schema
    clean = outputs[0]
    assert clean["handle_id"] == "actor_alpha"
    assert clean["platform"] == "BreachForums"
    assert "source_sha256" in clean
    assert len(clean["source_sha256"]) == 64

    # Check merkle.root schema
    merkle = outputs[1]
    assert "merkle_root" in merkle
    assert merkle["leaf_sha256"] == clean["source_sha256"]

    # Check audit.events schema
    audit = outputs[2]
    assert audit["event_type"] == "evidence_anchored"
    assert audit["resource"] == clean["source_sha256"]


def test_unique_evidence_rejection():
    conn = MockDBConnection()
    sha = digest(b"test-evidence-payload")

    # First insert succeeds
    ok1 = insert_evidence(
        conn,
        sha256=sha,
        source_url="http://test.onion",
        source_type="crawl",
        captured_at=utc_now(),
        minio_bucket="evidence",
        minio_key=f"raw/{sha}",
        ingested_by="test",
    )
    assert ok1 is True

    # Duplicate insert fails
    ok2 = insert_evidence(
        conn,
        sha256=sha,
        source_url="http://test.onion",
        source_type="crawl",
        captured_at=utc_now(),
        minio_bucket="evidence",
        minio_key=f"raw/{sha}",
        ingested_by="test",
    )
    assert ok2 is False


def test_audit_hash_chain_continuity():
    conn = MockDBConnection()

    # Append 5 audit events
    for i in range(5):
        append_audit_log(
            conn,
            event_type="evidence_ingested",
            action=f"action_{i}",
            actor_user="analyst1",
            resource=f"resource_{i}",
            metadata={"index": i},
        )

    # Verify chain
    assert len(conn.audit_log) == 5
    assert verify_audit_chain(conn) is True

    # Tamper with middle row to ensure verify_audit_chain detects tampering
    conn.audit_log[2]["resource"] = "tampered_resource"
    assert verify_audit_chain(conn) is False
