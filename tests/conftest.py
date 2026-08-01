"""Pytest configuration."""
import sys
from pathlib import Path

# Add src to sys.path so tests can import platform_core
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
