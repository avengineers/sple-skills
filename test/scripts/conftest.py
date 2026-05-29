"""Conftest for test/scripts - adds skill script directories to sys.path."""

import sys
from pathlib import Path

_his_metrics_dir = str(Path(__file__).parent.parent.parent / "plugins" / "embedded-sple" / "skills" / "his-metrics" / "scripts")
if _his_metrics_dir not in sys.path:
    sys.path.insert(0, _his_metrics_dir)
