"""Pytest configuration for DW-TADS test suite."""
import os
import sys
from pathlib import Path

# Add workspace root and shared/python to sys.path
workspace = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(workspace / "shared" / "python"))
sys.path.insert(0, str(workspace))
