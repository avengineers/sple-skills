"""Sync version from pyproject.toml to plugin manifest JSON files."""

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent


def get_version_from_pyproject() -> str:
    pyproject = ROOT / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def update_json_version(filepath: Path, version: str) -> None:
    content = json.loads(filepath.read_text(encoding="utf-8"))

    # Update top-level metadata version
    if "metadata" in content:
        content["metadata"]["version"] = version

    # Update plugin entries version
    if "plugins" in content:
        for plugin in content["plugins"]:
            plugin["version"] = version

    filepath.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")


def update_plugin_json(filepath: Path, version: str) -> None:
    content = json.loads(filepath.read_text(encoding="utf-8"))
    content["version"] = version
    filepath.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")


def git_add(filepath: Path) -> None:
    subprocess.run(["git", "add", str(filepath)], cwd=ROOT, check=True)


def main():
    version = get_version_from_pyproject()
    print(f"Syncing version {version} to manifest files...")

    manifests = [
        ROOT / ".github" / "plugin" / "marketplace.json",
        ROOT / ".claude-plugin" / "marketplace.json",
    ]
    for manifest in manifests:
        if manifest.exists():
            update_json_version(manifest, version)
            git_add(manifest)
            print(f"  Updated {manifest.relative_to(ROOT)}")

    # Both the root plugin.json (Copilot CLI / Agent Skills spec) and the
    # .claude-plugin/plugin.json (Claude Code) must stay version-synced.
    plugin_jsons = [
        ROOT / "plugins" / "embedded-sple" / "plugin.json",
        ROOT / "plugins" / "embedded-sple" / ".claude-plugin" / "plugin.json",
    ]
    for plugin_json in plugin_jsons:
        if plugin_json.exists():
            update_plugin_json(plugin_json, version)
            git_add(plugin_json)
            print(f"  Updated {plugin_json.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
