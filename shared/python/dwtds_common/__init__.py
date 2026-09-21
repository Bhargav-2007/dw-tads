"""
dwtds_common — Shared library for all 78 DW-TADS microservices.

Exports: BaseService, KafkaProducer, KafkaConsumer, PgClient,
Neo4jClient, MinioClient, EvidenceHasher, set_correlation_id,
get_correlation_id, configure_logging, get_logger, validate,
fetch_with_cache, merkle_root, sha256_hex.
"""

from .logging import configure_logging, get_logger, set_correlation_id, get_correlation_id
from .base_service import BaseService
from .cache import fetch_with_cache
from .evidence import sha256_hex, merkle_root, merkle_leaf_hash, merkle_parent_hash, canonical, digest
from .validation import validate, SCHEMAS

__all__ = [
    "BaseService",
    "configure_logging",
    "get_logger",
    "set_correlation_id",
    "get_correlation_id",
    "fetch_with_cache",
    "sha256_hex",
    "merkle_root",
    "merkle_leaf_hash",
    "merkle_parent_hash",
    "canonical",
    "digest",
    "validate",
    "SCHEMAS",
]
