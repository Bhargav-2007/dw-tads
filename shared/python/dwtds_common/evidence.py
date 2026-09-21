"""SHA-256 and Merkle tree utilities (RFC-6962 style)."""

import hashlib
import json


def canonical(value) -> bytes:
    """Return deterministic JSON bytes for hashing."""
    if isinstance(value, bytes):
        return value
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def digest(data) -> str:
    """Return SHA-256 hex digest of str or bytes data."""
    return sha256_hex(data)


def sha256_hex(data) -> str:
    """Return SHA-256 hex digest of data (str or bytes)."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def merkle_leaf_hash(evidence_sha: str) -> str:
    """RFC-6962 leaf node: H(0x00 || evidence_sha_bytes)."""
    return hashlib.sha256(b"\x00" + bytes.fromhex(evidence_sha)).hexdigest()


def merkle_parent_hash(a: str, b: str) -> str:
    """RFC-6962 interior node: H(0x01 || a_bytes || b_bytes)."""
    return hashlib.sha256(b"\x01" + bytes.fromhex(a) + bytes.fromhex(b)).hexdigest()


def merkle_root(hashes: list[str]) -> str:
    """
    Compute Merkle root from a list of SHA-256 hex strings.
    Returns '0' * 64 for an empty list.
    Duplicates the last leaf when count is odd (RFC-6962).
    """
    if not hashes:
        return "0" * 64
    leaves = [merkle_leaf_hash(h) for h in hashes]
    while len(leaves) > 1:
        if len(leaves) % 2:
            leaves.append(leaves[-1])
        leaves = [
            merkle_parent_hash(leaves[i], leaves[i + 1])
            for i in range(0, len(leaves), 2)
        ]
    return leaves[0]


def verify_merkle_proof(leaf_sha: str, proof: list[dict], root: str) -> bool:
    """
    Verify a Merkle inclusion proof.
    Each element of proof is {"hash": str, "side": "left"|"right"}.
    """
    current = merkle_leaf_hash(leaf_sha)
    for step in proof:
        sibling = step["hash"]
        if step["side"] == "left":
            current = merkle_parent_hash(sibling, current)
        else:
            current = merkle_parent_hash(current, sibling)
    return current == root
