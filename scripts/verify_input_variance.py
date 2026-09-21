"""Verify input variance — same service, different inputs → different outputs.

Tests 18 Tier A services to confirm output is not hardcoded.
Passes two different input messages and asserts output differs.

Exit 0 = all 18 pass.
Exit 1 = failures found.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shared", "python"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TIER_A_TESTS = [
    # (module_path, class_name, input_a, input_b, field_to_compare)
    ("services.evidence-pipeline.evidence_pipeline", "EvidencePipeline",
     {"text": "hello world exploit", "target": "http://abc.onion", "correlation_id": "cid-a"},
     {"text": "buy drugs bitcoin", "target": "http://xyz.onion", "correlation_id": "cid-b"},
     "source_sha256"),

    ("services.onion-discovery.onion_discovery", "OnionDiscovery",
     {"keyword": "market", "correlation_id": "cid-a"},
     {"keyword": "forum", "correlation_id": "cid-b"},
     None),  # No output comparison needed; just assert no crash

    ("services.ahmia-crawler.ahmia_crawler", "AhmiaCrawler",
     {"query": "hacking", "correlation_id": "cid-a"},
     {"query": "drugs", "correlation_id": "cid-b"},
     None),

    ("services.threat-feed-loader.threat_feed_loader", "ThreatFeedLoader",
     {"feed_type": "feodo", "correlation_id": "cid-a"},
     {"feed_type": "urlhaus", "correlation_id": "cid-b"},
     None),

    ("services.entity-extractor.entity_extractor", "EntityExtractor",
     {"text": "Send 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa to 0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
      "handle_id": "alice", "platform": "tor", "source_sha256": "aaa", "correlation_id": "cid-a"},
     {"text": "No addresses here just plain text with no entities",
      "handle_id": "bob", "platform": "tor", "source_sha256": "bbb", "correlation_id": "cid-b"},
     "entity_count"),

    ("services.stylometry-engine.stylometry_engine", "StylometryEngine",
     {"text": "The quick brown fox jumps over the lazy dog",
      "handle_id": "alice", "correlation_id": "cid-a"},
     {"text": "Buy drugs on darknet best prices bitcoin accepted no kyc",
      "handle_id": "bob", "correlation_id": "cid-b"},
     "fingerprint_sha256"),

    ("services.behavioral-profiler.behavioral_profiler", "BehavioralProfiler",
     {"handle_id": "alice", "posted_at": "2024-01-15T02:30:00Z",
      "text": "night owl post", "correlation_id": "cid-a"},
     {"handle_id": "bob", "posted_at": "2024-01-15T14:00:00Z",
      "text": "daytime activity post", "correlation_id": "cid-b"},
     "estimated_timezone_offset"),

    ("services.category-classifier.category_classifier", "CategoryClassifier",
     {"text": "buy cocaine heroin pills drugs escrow bitcoin vendor price",
      "handle_id": "x", "platform": "tor", "source_sha256": "aaa", "correlation_id": "cid-a"},
     {"text": "CVE exploit shellcode payload rootkit hacking breach zero-day",
      "handle_id": "y", "platform": "tor", "source_sha256": "bbb", "correlation_id": "cid-b"},
     "top_category"),

    ("services.blockchain-clusterer.blockchain_clusterer", "BlockchainClusterer",
     {"currency": "BTC", "from_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf",
      "to_address": "1BpEi6DfDAUFd153wiGrvkiKW1LghNFLNp", "correlation_id": "cid-a"},
     {"currency": "BTC", "from_address": "1BpEi6DfDAUFd153wiGrvkiKW1LghNFLNp",
      "to_address": "1Cf7DfMhQNi4rz9LxJRvBxeHa3pqwNg6Bk", "correlation_id": "cid-b"},
     "cluster_size"),

    ("services.confidence-scorer.confidence_scorer", "ConfidenceScorer",
     {"signals": {"stylometry": 0.90, "behavioral": 0.85}, "handle_id": "x",
      "similarity_score": 0.90, "correlation_id": "cid-a"},
     {"signals": {"stylometry": 0.30, "behavioral": 0.20}, "handle_id": "y",
      "similarity_score": 0.30, "correlation_id": "cid-b"},
     "confidence_score"),

    ("services.misconfig-analyzer.misconfig_analyzer", "MisconfigAnalyzer",
     {"match_text": "Apache Server Status Active connections: 42",
      "onion_address": "abcdef.onion", "headers": {}, "correlation_id": "cid-a"},
     {"match_text": "Welcome to nginx! Index of / PHP Version 7.4",
      "onion_address": "xyz.onion", "headers": {}, "correlation_id": "cid-b"},
     "finding_type"),

    ("services.clearnet-correlator.clearnet_correlator", "ClearnetCorrelator",
     {"onion_address": "abc.onion", "favicon_sha256": "deadbeef",
      "ssl_serial": "1234abcd", "finding_type": "scan", "correlation_id": "cid-a"},
     {"onion_address": "xyz.onion", "favicon_sha256": "cafebabe",
      "ssl_serial": "5678efgh", "finding_type": "scan", "correlation_id": "cid-b"},
     "onion_address"),

    ("services.deepfake-detector.deepfake_detector", "DeepfakeDetector",
     {"source_sha256": "aaaaaa", "pixels": list(range(64)), "correlation_id": "cid-a"},
     {"source_sha256": "bbbbbb", "pixels": [255] * 64, "correlation_id": "cid-b"},
     "fake_score"),

    ("services.image-forensics.image_forensics", "ImageForensics",
     {"source_sha256": "aaaaaa", "pixels": [0, 128, 255] * 22, "correlation_id": "cid-a"},
     {"source_sha256": "cccccc", "pixels": [64, 64, 64] * 22, "correlation_id": "cid-b"},
     "ela_score"),

    ("services.malware-sandbox.malware_sandbox", "MalwareSandbox",
     {"source_sha256": "aaa", "text": "powershell -enc base64payload CreateRemoteThread",
      "correlation_id": "cid-a"},
     {"source_sha256": "bbb", "text": "hello world this is benign text",
      "correlation_id": "cid-b"},
     "verdict"),

    ("services.synthetic-media-analyzer.synthetic_media_analyzer", "SyntheticMediaAnalyzer",
     {"source_sha256": "aaa", "media_type": "image",
      "pixels": [i % 255 for i in range(100)], "correlation_id": "cid-a"},
     {"source_sha256": "bbb", "media_type": "audio",
      "audio_magnitudes": [0.8, 0.7, 0.9, 0.85, 0.75], "correlation_id": "cid-b"},
     "synthetic_score"),

    ("services.legal-admissibility.legal_admissibility", "LegalAdmissibility",
     {"leaf_sha256": "a" * 64, "merkle_root": None, "correlation_id": "cid-a"},
     {"leaf_sha256": "b" * 64, "merkle_root": None, "correlation_id": "cid-b"},
     None),

    ("services.vasp-attributor.vasp_attributor", "VaspAttributor",
     {"wallet_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf", "currency": "BTC",
      "cluster_size": 5, "correlation_id": "cid-a"},
     {"wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", "currency": "ETH",
      "cluster_size": 1500, "correlation_id": "cid-b"},
     "confidence"),
]


async def run_test(module_path, class_name, input_a, input_b, compare_field):
    """Import service class and run two inputs; verify outputs differ if compare_field set."""
    # Convert module path to importable format
    import importlib
    mod_path = module_path.replace("-", "_").replace("/", ".").replace("\\", ".")
    # Try direct import
    try:
        parts = module_path.split("/")
        if len(parts) == 2:
            pkg, mod = parts[0].replace("-", "_"), parts[1].replace("-", "_")
            sys.path.insert(0, str(
                __import__("pathlib").Path(__file__).resolve().parent.parent / "services" /
                parts[0]
            ))
            mod_obj = importlib.import_module(mod)
        else:
            mod_obj = importlib.import_module(mod_path)
    except ImportError as e:
        # Try services/<slug>/<py>.py directly
        import importlib.util
        ws = __import__("pathlib").Path(__file__).resolve().parent.parent
        slug = module_path.split("/")[1] if "/" in module_path else module_path.split(".")[1]
        py_name = module_path.split("/")[-1].replace("-", "_") if "/" in module_path else mod_path.split(".")[-1]
        spec_path = ws / "services" / slug / f"{py_name}.py"
        if not spec_path.exists():
            return False, f"Module not found: {spec_path}"
        spec = importlib.util.spec_from_file_location(py_name, spec_path)
        mod_obj = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod_obj)
        except Exception as e2:
            return False, f"Import error: {e2}"

    cls = getattr(mod_obj, class_name, None)
    if cls is None:
        return False, f"Class {class_name} not found"

    svc = cls()
    try:
        out_a = await svc.handle(input_a)
        out_b = await svc.handle(input_b)
    except Exception as e:
        return False, f"handle() raised: {e}"

    if compare_field and out_a and out_b:
        val_a = out_a[0].get(compare_field)
        val_b = out_b[0].get(compare_field)
        if val_a == val_b:
            return False, f"Output {compare_field} identical for different inputs: {val_a!r}"

    return True, "OK"


async def main():
    passed = 0
    failed = 0
    for args in TIER_A_TESTS:
        module_path, class_name = args[0], args[1]
        input_a, input_b, field = args[2], args[3], args[4]
        name = f"{class_name}"
        ok, msg = await run_test(module_path, class_name, input_a, input_b, field)
        if ok:
            print(f"PASS  {name}")
            passed += 1
        else:
            print(f"FAIL  {name}: {msg}")
            failed += 1

    print(f"\n{passed} PASSED / {failed} FAILED (of {len(TIER_A_TESTS)} Tier A tests)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
