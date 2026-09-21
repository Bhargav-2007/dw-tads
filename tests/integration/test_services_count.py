"""Integration test: Service inventory count and contract verification.
Asserts:
- Sum of plane services == 78
- Per-plane breakdown: 12, 14, 11, 14, 10, 9, 8
- Every NAME unique across all 78
- Every HTTP_PORT unique across all 78
- Every service conforms to the Section B contract
"""
import sys
import os
import importlib

# Add workspace root to sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import pytest


def get_plane_services(folder_name: str):
    mod = importlib.import_module(f"{folder_name}.services")
    return mod.SERVICES


def test_services_count_and_uniqueness():
    plane_specs = [
        (1, "plane1-infrastructure", 12),
        (2, "plane2-collection", 14),
        (3, "plane3-analytics", 11),
        (4, "plane4-fusion", 14),
        (5, "plane5-legal", 10),
        (6, "plane6-case", 9),
        (7, "plane7-presentation", 8),
    ]

    all_services = []
    plane_counts = {}

    for plane_id, folder_name, expected_count in plane_specs:
        services = get_plane_services(folder_name)
        plane_counts[plane_id] = len(services)
        assert len(services) == expected_count, (
            f"Plane {plane_id} ({folder_name}) expected {expected_count} services, got {len(services)}"
        )
        all_services.extend(services)

    total_count = len(all_services)
    assert total_count == 78, f"Expected 78 total services across all 7 planes, got {total_count}"

    # Verify all service names are unique across all 78
    names = [s.NAME for s in all_services]
    duplicate_names = [n for n in set(names) if names.count(n) > 1]
    assert len(names) == len(set(names)), f"Duplicate service names found: {duplicate_names}"

    # Verify all service HTTP_PORTs are unique across all 78
    ports = [s.HTTP_PORT for s in all_services]
    duplicate_ports = [p for p in set(ports) if ports.count(p) > 1]
    assert len(ports) == len(set(ports)), f"Duplicate HTTP_PORTs found: {duplicate_ports}"

    # Verify class contract on each service
    for s in all_services:
        assert hasattr(s, "NAME") and isinstance(s.NAME, str) and len(s.NAME) > 0
        assert hasattr(s, "PLANE") and isinstance(s.PLANE, int) and 1 <= s.PLANE <= 7
        assert hasattr(s, "TIER") and s.TIER in ["Foundation", "Intermediate", "Advanced", "Expert", "Critical"]
        assert hasattr(s, "INPUT_TOPICS") and isinstance(s.INPUT_TOPICS, list)
        assert hasattr(s, "OUTPUT_TOPICS") and isinstance(s.OUTPUT_TOPICS, list)
        assert hasattr(s, "HTTP_PORT") and isinstance(s.HTTP_PORT, int)
        assert hasattr(s, "HTTP_ROUTES") and isinstance(s.HTTP_ROUTES, list)
        assert hasattr(s, "start") and callable(getattr(s, "start"))
        assert hasattr(s, "handle") and callable(getattr(s, "handle"))
        assert hasattr(s, "health") and callable(getattr(s, "health"))


@pytest.mark.asyncio
async def test_all_services_health():
    """Verify health() returns {'status': 'ok', ...} on every service."""
    plane_folders = [
        "plane1-infrastructure",
        "plane2-collection",
        "plane3-analytics",
        "plane4-fusion",
        "plane5-legal",
        "plane6-case",
        "plane7-presentation",
    ]
    all_service_classes = []
    for folder in plane_folders:
        all_service_classes.extend(get_plane_services(folder))

    for cls in all_service_classes:
        instance = cls()
        h = await instance.health()
        assert h["status"] == "ok"
        assert h["service"] == cls.NAME
        assert h["plane"] == cls.PLANE
