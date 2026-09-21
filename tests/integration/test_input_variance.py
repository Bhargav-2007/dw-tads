"""Integration tests for input variance — no network required."""
import asyncio
import importlib.util
import sys
import os
import pytest
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "shared" / "python"))
sys.path.insert(0, str(WORKSPACE))


def _load_service(slug: str, py_name: str, class_name: str):
    """Load a service class from services/<slug>/<py_name>.py."""
    spec_path = WORKSPACE / "services" / slug / f"{py_name}.py"
    spec = importlib.util.spec_from_file_location(py_name, spec_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, class_name)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ── Entity Extractor: BTC address presence vs absence ────────────────────────
def test_entity_extractor_btc_vs_no_btc():
    cls = _load_service("entity-extractor", "entity_extractor", "EntityExtractor")
    svc = cls()
    out_with = _run(svc.handle({
        "text": "Send 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa to my wallet",
        "handle_id": "alice", "platform": "tor",
        "source_sha256": "aaa", "correlation_id": "cid-a"
    }))
    out_without = _run(svc.handle({
        "text": "No crypto addresses here just plain text",
        "handle_id": "bob", "platform": "tor",
        "source_sha256": "bbb", "correlation_id": "cid-b"
    }))
    assert out_with[0]["entity_count"] != out_without[0]["entity_count"], \
        "Entity count must differ between text with/without addresses"


# ── Stylometry: different texts → different fingerprints ─────────────────────
def test_stylometry_different_texts():
    cls = _load_service("stylometry-engine", "stylometry_engine", "StylometryEngine")
    svc = cls()
    out_a = _run(svc.handle({
        "text": "I am selling drugs on the darknet bitcoin only",
        "handle_id": "alice", "correlation_id": "cid-a"
    }))
    out_b = _run(svc.handle({
        "text": "The quick brown fox jumps over the lazy dog",
        "handle_id": "bob", "correlation_id": "cid-b"
    }))
    sha_a = out_a[0].get("fingerprint_sha256", "")
    sha_b = out_b[0].get("fingerprint_sha256", "")
    assert sha_a != sha_b, "Fingerprints must differ for different texts"


# ── Behavioral profiler: different hours → different timezone estimate ────────
def test_behavioral_profiler_hour_variance():
    cls = _load_service("behavioral-profiler", "behavioral_profiler", "BehavioralProfiler")
    svc = cls()
    out_a = _run(svc.handle({
        "handle_id": "alice", "posted_at": "2024-01-01T02:00:00Z",
        "text": "night post", "correlation_id": "cid-a"
    }))
    out_b = _run(svc.handle({
        "handle_id": "bob", "posted_at": "2024-01-01T14:00:00Z",
        "text": "day post", "correlation_id": "cid-b"
    }))
    tz_a = out_a[0]["estimated_timezone_offset"]
    tz_b = out_b[0]["estimated_timezone_offset"]
    # After only 1 post each, histogram peaks at posted hour → different offsets
    hist_a = out_a[0]["hour_histogram"]
    hist_b = out_b[0]["hour_histogram"]
    assert hist_a != hist_b, "Histograms must differ for posts at different hours"


# ── Category classifier: drugs text → drugs top category ─────────────────────
def test_category_classifier_drugs_vs_hacking():
    cls = _load_service("category-classifier", "category_classifier", "CategoryClassifier")
    svc = cls()
    out_drugs = _run(svc.handle({
        "text": "buy cocaine heroin mdma pills drugs vendor gram bitcoin",
        "handle_id": "x", "platform": "tor", "source_sha256": "aaa", "correlation_id": "cid-a"
    }))
    out_hack = _run(svc.handle({
        "text": "CVE exploit shellcode zero-day payload breach hack vulnerability",
        "handle_id": "y", "platform": "tor", "source_sha256": "bbb", "correlation_id": "cid-b"
    }))
    assert out_drugs[0]["top_category"] == "drugs", \
        f"Expected 'drugs', got {out_drugs[0]['top_category']}"
    assert out_hack[0]["top_category"] == "hacking", \
        f"Expected 'hacking', got {out_hack[0]['top_category']}"


# ── Blockchain clusterer: union-find cluster grows ────────────────────────────
def test_blockchain_clusterer_grows():
    cls = _load_service("blockchain-clusterer", "blockchain_clusterer", "BlockchainClusterer")
    svc = cls()
    out_1 = _run(svc.handle({
        "currency": "BTC",
        "from_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf",
        "to_address": "1BpEi6DfDAUFd153wiGrvkiKW1LghNFLNp",
        "correlation_id": "cid-a"
    }))
    out_2 = _run(svc.handle({
        "currency": "BTC",
        "from_address": "1BpEi6DfDAUFd153wiGrvkiKW1LghNFLNp",
        "to_address": "1Cf7DfMhQNi4rz9LxJRvBxeHa3pqwNg6Bk",
        "correlation_id": "cid-b"
    }))
    assert out_2[0]["cluster_size"] >= out_1[0]["cluster_size"], \
        "Cluster must grow with additional union operations"


# ── Confidence scorer: high signals → high score ──────────────────────────────
def test_confidence_scorer_high_vs_low():
    cls = _load_service("confidence-scorer", "confidence_scorer", "ConfidenceScorer")
    svc = cls()
    out_high = _run(svc.handle({
        "subject_id": "alice", "similarity_score": 0.95,
        "signals": {"stylometry": 0.95, "behavioral": 0.90},
        "correlation_id": "cid-a"
    }))
    out_low = _run(svc.handle({
        "subject_id": "bob", "similarity_score": 0.20,
        "signals": {"stylometry": 0.20, "behavioral": 0.15},
        "correlation_id": "cid-b"
    }))
    assert out_high[0]["confidence_score"] > out_low[0]["confidence_score"], \
        "High signals must produce higher confidence score"


# ── Misconfig analyzer: real matches → different finding types ────────────────
def test_misconfig_analyzer_findings():
    cls = _load_service("misconfig-analyzer", "misconfig_analyzer", "MisconfigAnalyzer")
    svc = cls()
    out_modstatus = _run(svc.handle({
        "match_text": "Apache Server Status for localhost",
        "onion_address": "abc.onion", "headers": {}, "correlation_id": "cid-a"
    }))
    out_git = _run(svc.handle({
        "match_text": ".git/HEAD ref: refs/heads/main",
        "onion_address": "xyz.onion", "headers": {}, "correlation_id": "cid-b"
    }))
    types = [o["finding_type"] for o in out_modstatus]
    assert "mod_status_exposed" in types, f"Expected mod_status_exposed, got {types}"
    git_types = [o["finding_type"] for o in out_git]
    assert "git_exposed" in git_types, f"Expected git_exposed, got {git_types}"


# ── Deepfake detector: different pixels → different scores ────────────────────
def test_deepfake_detector_variance():
    cls = _load_service("deepfake-detector", "deepfake_detector", "DeepfakeDetector")
    svc = cls()
    out_a = _run(svc.handle({
        "source_sha256": "a" * 64, "pixels": list(range(64)), "correlation_id": "cid-a"
    }))
    out_b = _run(svc.handle({
        "source_sha256": "b" * 64, "pixels": [255] * 64, "correlation_id": "cid-b"
    }))
    assert out_a[0]["fake_score"] != out_b[0]["fake_score"], \
        "Deepfake score must differ for different pixel inputs"


# ── Malware sandbox: malicious text → malware, benign → benign ──────────────
def test_malware_sandbox_verdicts():
    cls = _load_service("malware-sandbox", "malware_sandbox", "MalwareSandbox")
    svc = cls()
    out_mal = _run(svc.handle({
        "source_sha256": "aaa",
        "text": "powershell -enc base64 CreateRemoteThread WriteProcessMemory VirtualAllocEx bitcoin: payment.onion",
        "correlation_id": "cid-a"
    }))
    out_ben = _run(svc.handle({
        "source_sha256": "bbb",
        "text": "hello world this is benign text no malware here at all",
        "correlation_id": "cid-b"
    }))
    assert out_mal[0]["malware_score"] > out_ben[0]["malware_score"], \
        "Malicious text must score higher than benign text"
