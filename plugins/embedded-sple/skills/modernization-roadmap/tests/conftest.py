"""Conftest for modernization-roadmap skill tests."""

import sys
from pathlib import Path

_scripts_dir = str(Path(__file__).parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)
