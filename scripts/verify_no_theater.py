"""Verify no theater code in service files.

Checks:
  1. No service references tests/data/mock_sources/
  2. No service uses mock_mode
  3. No hardcoded placeholder onion addresses (http://ahmia-.onion patterns)
  4. Every handle() reads from message[...] or message.get(...)
  5. No hardcoded confidence values used as sole return (emb_cos = 0.92 etc.)
  6. Count of services matches 78

Exit 0 = all checks pass.
Exit 1 = violations found.
"""

import ast
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
SERVICES_DIR = WORKSPACE / "services"

FORBIDDEN_PATTERNS = [
    (re.compile(r'tests[/\\]data[/\\]mock_sources'), "mock_sources path reference"),
    (re.compile(r'\bmock_mode\b'), "mock_mode usage"),
    (re.compile(r'http://ahmia-\w+\.onion'), "hardcoded placeholder .onion"),
    (re.compile(r'http://discovery-\w+\.onion'), "hardcoded discovery .onion"),
    (re.compile(r'"192\.0\.2\.1"'), "hardcoded TEST-NET IP"),
    (re.compile(r'emb_cos\s*=\s*0\.\d+\s*$', re.MULTILINE), "hardcoded cosine score"),
    (re.compile(r'return\s*\[\s*\{[^}]*"hardcoded'), "hardcoded return value"),
]

MESSAGE_READ_RE = re.compile(r'message\s*[\[".]')


def check_service_file(path: Path) -> list[str]:
    violations = []
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"  read_error: {e}"]

    # Check forbidden patterns
    for pat, label in FORBIDDEN_PATTERNS:
        if pat.search(code):
            violations.append(f"  FORBIDDEN: {label}")

    # Check that handle() reads from message
    if "async def handle" in code:
        # Find handle body
        handle_start = code.find("async def handle")
        handle_body = code[handle_start:handle_start + 2000]
        if not MESSAGE_READ_RE.search(handle_body):
            violations.append("  MISSING: handle() does not read from message[...] or message.get(...)")

    return violations


def main() -> int:
    service_dirs = [d for d in SERVICES_DIR.iterdir() if d.is_dir()]
    errors = 0
    total_services = 0

    for svc_dir in sorted(service_dirs):
        py_files = list(svc_dir.glob("*.py"))
        if not py_files:
            continue
        total_services += 1
        for py_file in py_files:
            if py_file.name.startswith("__"):
                continue
            violations = check_service_file(py_file)
            if violations:
                print(f"FAIL {py_file.relative_to(WORKSPACE)}")
                for v in violations:
                    print(v)
                errors += 1
            else:
                pass  # quiet on success

    print(f"\nTotal services: {total_services} (expected 78)")
    if total_services != 78:
        print(f"COUNT MISMATCH: expected 78, found {total_services}")
        errors += 1

    if errors == 0:
        print("ALL CHECKS PASSED — no theater code detected.")
        return 0
    else:
        print(f"FAILED: {errors} service(s) with violations.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
