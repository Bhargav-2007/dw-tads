import sys
import os
import importlib
import urllib.request
import json

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

expected_breakdown = {
    1: 12,
    2: 14,
    3: 11,
    4: 14,
    5: 10,
    6: 9,
    7: 8,
}

plane_folders = {
    1: "plane1-infrastructure",
    2: "plane2-collection",
    3: "plane3-analytics",
    4: "plane4-fusion",
    5: "plane5-legal",
    6: "plane6-case",
    7: "plane7-presentation",
}

counts = {}
used_live_http = True

for plane_id in range(1, 8):
    port = 8000 + plane_id
    url = f"http://localhost:{port}/services"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DW-TADS-Verifier/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            count = len(data.get("services", []))
            counts[plane_id] = count
            print(f"Plane {plane_id} (HTTP {url}): {count} services")
    except Exception:
        used_live_http = False
        break

if not used_live_http:
    print("Live HTTP endpoints not reachable or still booting. Verifying via plane package registries...")
    counts = {}
    for plane_id in range(1, 8):
        folder = plane_folders[plane_id]
        mod = importlib.import_module(f"{folder}.services")
        count = len(mod.SERVICES)
        counts[plane_id] = count
        print(f"Plane {plane_id} ({folder}): {count} services")

total_services = sum(counts.values())
print(f"\nTotal Services Count: {total_services}")

# Validate per-plane counts
for plane_id, exp in expected_breakdown.items():
    actual = counts.get(plane_id, 0)
    if actual != exp:
        print(f"FAILED: Plane {plane_id} expected {exp} services, got {actual}")
        sys.exit(1)

# Validate grand total
if total_services == 78:
    print("SUCCESS: Confirmed exactly 78 services across 7 planes. (Exit 0)")
    sys.exit(0)
else:
    print(f"FAILED: Total services {total_services} != 78 (Exit 1)")
    sys.exit(1)
