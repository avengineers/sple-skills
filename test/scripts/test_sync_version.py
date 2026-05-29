"""Tests for scripts/sync_version.py."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from sync_version import (
    get_version_from_pyproject,
    main,
    update_json_version,
    update_plugin_json,
)


class TestGetVersionFromPyproject:
    def test_extracts_version(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.2.3"\n', encoding="utf-8")
        monkeypatch.setattr("sync_version.ROOT", tmp_path)
        assert get_version_from_pyproject() == "1.2.3"

    def test_raises_if_no_version(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'\n", encoding="utf-8")
        monkeypatch.setattr("sync_version.ROOT", tmp_path)
        with pytest.raises(ValueError, match="Could not find version"):
            get_version_from_pyproject()

    def test_extracts_prerelease_version(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "2.0.0-rc.1"\n', encoding="utf-8")
        monkeypatch.setattr("sync_version.ROOT", tmp_path)
        assert get_version_from_pyproject() == "2.0.0-rc.1"


class TestUpdateJsonVersion:
    def test_updates_metadata_and_plugins(self, tmp_path):
        manifest = tmp_path / "marketplace.json"
        data = {
            "metadata": {"version": "0.0.0"},
            "plugins": [
                {"name": "plugin-a", "version": "0.0.0"},
                {"name": "plugin-b", "version": "0.0.0"},
            ],
        }
        manifest.write_text(json.dumps(data), encoding="utf-8")

        update_json_version(manifest, "3.1.0")

        result = json.loads(manifest.read_text(encoding="utf-8"))
        assert result["metadata"]["version"] == "3.1.0"
        assert result["plugins"][0]["version"] == "3.1.0"
        assert result["plugins"][1]["version"] == "3.1.0"

    def test_handles_missing_metadata_key(self, tmp_path):
        manifest = tmp_path / "marketplace.json"
        data = {"plugins": [{"name": "p", "version": "0.0.0"}]}
        manifest.write_text(json.dumps(data), encoding="utf-8")

        update_json_version(manifest, "1.0.0")

        result = json.loads(manifest.read_text(encoding="utf-8"))
        assert "metadata" not in result
        assert result["plugins"][0]["version"] == "1.0.0"

    def test_handles_missing_plugins_key(self, tmp_path):
        manifest = tmp_path / "marketplace.json"
        data = {"metadata": {"version": "0.0.0"}}
        manifest.write_text(json.dumps(data), encoding="utf-8")

        update_json_version(manifest, "2.0.0")

        result = json.loads(manifest.read_text(encoding="utf-8"))
        assert result["metadata"]["version"] == "2.0.0"


class TestUpdatePluginJson:
    def test_updates_version_field(self, tmp_path):
        plugin = tmp_path / "plugin.json"
        data = {"name": "embedded-sple", "version": "0.0.0", "skills": []}
        plugin.write_text(json.dumps(data), encoding="utf-8")

        update_plugin_json(plugin, "4.5.6")

        result = json.loads(plugin.read_text(encoding="utf-8"))
        assert result["version"] == "4.5.6"
        assert result["name"] == "embedded-sple"


class TestMain:
    def test_syncs_all_manifests(self, tmp_path, monkeypatch):
        monkeypatch.setattr("sync_version.ROOT", tmp_path)

        # Create pyproject.toml
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.0.0"\n', encoding="utf-8")

        # Create marketplace manifests
        github_dir = tmp_path / ".github" / "plugin"
        github_dir.mkdir(parents=True)
        marketplace = github_dir / "marketplace.json"
        marketplace.write_text(
            json.dumps({"metadata": {"version": "0.0.0"}, "plugins": [{"version": "0.0.0"}]}),
            encoding="utf-8",
        )

        claude_dir = tmp_path / ".claude-plugin"
        claude_dir.mkdir()
        claude_marketplace = claude_dir / "marketplace.json"
        claude_marketplace.write_text(
            json.dumps({"metadata": {"version": "0.0.0"}, "plugins": [{"version": "0.0.0"}]}),
            encoding="utf-8",
        )

        # Create plugin.json
        plugin_dir = tmp_path / "plugins" / "embedded-sple"
        plugin_dir.mkdir(parents=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(
            json.dumps({"version": "0.0.0"}), encoding="utf-8"
        )

        main()

        assert json.loads(marketplace.read_text())["metadata"]["version"] == "1.0.0"
        assert json.loads(claude_marketplace.read_text())["metadata"]["version"] == "1.0.0"
        assert json.loads(plugin_json.read_text())["version"] == "1.0.0"

    def test_skips_missing_manifests(self, tmp_path, monkeypatch):
        monkeypatch.setattr("sync_version.ROOT", tmp_path)

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.0.0"\n', encoding="utf-8")

        # No manifest files — should not raise
        main()
