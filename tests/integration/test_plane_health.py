"""Integration test: Plane health and /services endpoints.
Asserts:
- GET /services on each plane returns correct per-plane count (12, 14, 18, 10, 9, 8, 7)
- GET /health on each plane returns 200 and 'ok'
"""
import sys
import os
import importlib
import pytest
from aiohttp.test_utils import TestClient, TestServer

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from common.plane_base import PlaneRunner


def get_plane_services(folder_name: str):
    mod = importlib.import_module(f"{folder_name}.services")
    return mod.SERVICES


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "plane_id,folder_name,plane_name,port,expected_count",
    [
        (1, "plane1-infrastructure", "plane1-infrastructure", 8001, 12),
        (2, "plane2-collection", "plane2-collection", 8002, 14),
        (3, "plane3-analytics", "plane3-analytics", 8003, 11),
        (4, "plane4-fusion", "plane4-fusion", 8004, 14),
        (5, "plane5-legal", "plane5-legal", 8005, 10),
        (6, "plane6-case", "plane6-case", 8006, 9),
        (7, "plane7-presentation", "plane7-presentation", 8007, 8),
    ],
)
async def test_plane_endpoints(plane_id, folder_name, plane_name, port, expected_count):
    services = get_plane_services(folder_name)
    runner = PlaneRunner(
        plane_id=plane_id,
        plane_name=plane_name,
        plane_port=port,
        service_classes=services,
    )
    runner._setup_routes()
    runner.services = [cls() for cls in runner.service_classes]

    server = TestServer(runner._app)
    client = TestClient(server)
    await client.start_server()

    try:
        # 1. Test /health
        resp = await client.get("/health")
        assert resp.status == 200
        health_data = await resp.json()
        assert health_data["status"] == "ok"
        assert health_data["plane"] == plane_id
        assert health_data["services_count"] == expected_count

        # 2. Test /services
        resp = await client.get("/services")
        assert resp.status == 200
        services_data = await resp.json()
        assert services_data["plane"] == plane_id
        assert services_data["count"] == expected_count
        assert len(services_data["services"]) == expected_count

        for item in services_data["services"]:
            assert "name" in item
            assert "plane" in item
            assert "tier" in item
            assert "input_topics" in item
            assert "output_topics" in item
            assert "http_port" in item
            assert "health" in item
            assert item["health"]["status"] == "ok"

    finally:
        await client.close()
