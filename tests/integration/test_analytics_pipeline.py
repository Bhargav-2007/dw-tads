"""Integration test: Analytics & AI Pipeline.
Asserts:
- scan with mod_status → infra.indicators
- two similar posts → persona.links
- malformed message → dlq
"""
import sys
import os
import importlib
import pytest

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

MisconfigAnalyzer = importlib.import_module("plane3-analytics.services.misconfig_analyzer").MisconfigAnalyzer
StylometryEngine = importlib.import_module("plane3-analytics.services.stylometry_engine").StylometryEngine


@pytest.mark.asyncio
async def test_mod_status_detection():
    service = MisconfigAnalyzer()
    msg = {
        "onion_address": "darkforum1234567.onion",
        "path": "/server-status",
        "body": "<html>Apache Server Status for darkforum1234567.onion</html>",
        "ip": "203.0.113.45",
    }
    outputs = await service.handle(msg)
    assert len(outputs) == 1
    finding = outputs[0]
    assert finding["onion_address"] == "darkforum1234567.onion"
    assert finding["finding_type"] == "mod_status_leak"
    assert finding["matched_clearnet_ip"] == "203.0.113.45"
    assert finding["confidence"] >= 0.90


@pytest.mark.asyncio
async def test_stylometry_two_posts_links():
    service = StylometryEngine()
    
    # Post from actor_alpha
    msg1 = {
        "handle_id": "actor_alpha",
        "platform": "BreachForums",
        "text": "Fresh CVE-2025-12345 exploit available. DM for price.",
    }
    # Post from actor_beta
    msg2 = {
        "handle_id": "actor_beta",
        "platform": "RAMP",
        "text": "Bulk database of 2M Indian users. Sample on request.",
    }

    out1 = await service.handle(msg1)
    out2 = await service.handle(msg2)

    all_outputs = out1 + out2
    assert len(all_outputs) >= 1

    link = all_outputs[-1]
    assert link["handle_a"] in ["actor_alpha", "actor_beta"]
    assert link["handle_b"] in ["actor_alpha", "actor_beta"]
    assert link["similarity_score"] >= 0.85
    assert link["confidence"] >= 0.85


@pytest.mark.asyncio
async def test_malformed_dlq_routing():
    service = MisconfigAnalyzer()
    dlq_captured = []

    # Mock publish_dlq
    def mock_publish_dlq(topic, payload, error_msg):
        dlq_captured.append({"topic": topic, "payload": payload, "error": error_msg})

    service.publish_dlq = mock_publish_dlq

    # Pass non-dict message to _process_one
    class MockConsumer:
        committed = False
        def commit(self):
            self.committed = True

    consumer = MockConsumer()
    await service._process_one(consumer, "scan.raw", "malformed_string_not_dict")

    assert len(dlq_captured) == 1
    assert dlq_captured[0]["topic"] == "scan.raw"
    assert "JSON object" in dlq_captured[0]["error"]
