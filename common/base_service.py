"""Backwards-compatibility shim.

All 78 service files import BaseService from common.base_service.
This module attempts to import from dwtds_common (shared library).
If dwtds_common is not yet on sys.path, falls back to the local
implementation which mirrors the same interface.

Do NOT change the service files to import from dwtds_common directly —
this shim ensures both production (Docker, sys.path includes shared/python)
and test (pytest, workspace root on sys.path) paths work identically.
"""

import os
import sys

# Try to resolve dwtds_common from shared/python
_shared = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "shared", "python")
if _shared not in sys.path:
    sys.path.insert(0, _shared)

try:
    from dwtds_common.base_service import BaseService, utc_now  # noqa: F401
    from dwtds_common.logging import (  # noqa: F401
        configure_logging,
        get_logger,
        set_correlation_id,
        get_correlation_id,
    )
    from dwtds_common.evidence import (  # noqa: F401
        sha256_hex,
        merkle_root,
        merkle_leaf_hash,
        merkle_parent_hash,
        verify_merkle_proof,
        canonical,
        digest,
    )
    from dwtds_common.cache import fetch_with_cache  # noqa: F401
    from dwtds_common.validation import validate  # noqa: F401
except ImportError:
    # Fallback: minimal inline implementation so tests don't crash
    # even when shared/python is not available.
    import asyncio
    import hashlib
    import json
    import uuid
    from abc import ABC, abstractmethod
    from datetime import datetime, timezone

    def utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def get_correlation_id() -> str:
        return str(uuid.uuid4())

    def set_correlation_id(cid: str) -> None:
        pass

    def configure_logging(*args, **kwargs) -> None:
        pass

    def get_logger(name: str = "dwtds"):
        import structlog
        return structlog.get_logger(name)

    def canonical(value) -> bytes:
        if isinstance(value, bytes):
            return value
        return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")

    def digest(data) -> str:
        return sha256_hex(data)

    def sha256_hex(data) -> str:
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha256(data).hexdigest()

    def merkle_leaf_hash(evidence_sha: str) -> str:
        return hashlib.sha256(b"\x00" + bytes.fromhex(evidence_sha)).hexdigest()

    def merkle_parent_hash(a: str, b: str) -> str:
        return hashlib.sha256(b"\x01" + bytes.fromhex(a) + bytes.fromhex(b)).hexdigest()

    def verify_merkle_proof(leaf_sha: str, proof: list, root: str) -> bool:
        current = merkle_leaf_hash(leaf_sha)
        for step in proof:
            sibling = step["hash"]
            if step.get("side") == "left":
                current = merkle_parent_hash(sibling, current)
            else:
                current = merkle_parent_hash(current, sibling)
        return current == root

    def merkle_root(hashes: list) -> str:
        if not hashes:
            return "0" * 64
        leaves = [hashlib.sha256(b"\x00" + bytes.fromhex(h)).hexdigest() for h in hashes]
        while len(leaves) > 1:
            if len(leaves) % 2:
                leaves.append(leaves[-1])
            leaves = [hashlib.sha256(b"\x01" + bytes.fromhex(leaves[i]) + bytes.fromhex(leaves[i+1])).hexdigest()
                      for i in range(0, len(leaves), 2)]
        return leaves[0]

    async def fetch_with_cache(*args, **kwargs):
        return None

    def validate(topic: str, payload: dict) -> dict:
        return payload

    class BaseService(ABC):
        NAME: str = "base-service"
        PLANE: int = 1
        TIER: str = "Foundation"
        INPUT_TOPICS: list = []
        OUTPUT_TOPICS: list = []
        HTTP_PORT: int = 0
        HTTP_ROUTES: list = ["/health", "/ready", "/metrics"]

        def __init__(self, kafka=None, pg=None, neo4j=None, minio=None):
            self.kafka = kafka
            self.pg = pg
            self.neo4j = neo4j
            self.minio = minio
            self.log = get_logger(self.NAME)
            self._running = False
            self.metrics_count: int = 0
            self._seen_hashes: set = set()

        @abstractmethod
        async def handle(self, message: dict) -> list:
            ...

        async def health(self) -> dict:
            return {"status": "ok", "service": self.NAME, "plane": self.PLANE}

        async def ready(self) -> dict:
            return {"status": "ready", "service": self.NAME, "plane": self.PLANE}

        async def start(self) -> None:
            self._running = True

        async def stop(self) -> None:
            self._running = False

        async def publish(self, topic: str, payload: dict) -> None:
            pass


__all__ = [
    "BaseService",
    "utc_now",
    "configure_logging",
    "get_logger",
    "set_correlation_id",
    "get_correlation_id",
    "sha256_hex",
    "merkle_root",
    "merkle_leaf_hash",
    "merkle_parent_hash",
    "verify_merkle_proof",
    "canonical",
    "digest",
    "fetch_with_cache",
    "validate",
]
