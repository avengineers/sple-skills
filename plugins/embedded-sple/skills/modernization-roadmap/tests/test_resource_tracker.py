"""Tests for modernization-roadmap/scripts/resource_tracker.py"""

import json
import pytest
from pathlib import Path
from resource_tracker import (
    ResourceMetrics,
    parse_map_file,
    save_baseline,
    load_metrics,
    compare_metrics,
    print_comparison_report,
)


class TestParseMapFile:
    def test_arm_gcc_format(self, tmp_path):
        map_file = tmp_path / "output.map"
        map_file.write_text(
            ".text   0x08000000   0x1000\n"
            ".bss    0x20000000   0x0200\n",
            encoding="utf-8",
        )
        result = parse_map_file(map_file)
        assert result is not None
        assert result.rom_bytes == 0x1000
        assert result.ram_bytes == 0x0200

    def test_summary_format(self, tmp_path):
        map_file = tmp_path / "output.map"
        map_file.write_text(
            "Total RO  Size (Code + RO Data)    8192 bytes\n"
            "Total RW  Size (RW Data + ZI Data)  4096 bytes\n",
            encoding="utf-8",
        )
        result = parse_map_file(map_file)
        assert result is not None
        assert result.rom_bytes == 8192
        assert result.ram_bytes == 4096

    def test_nonexistent_file(self, tmp_path):
        result = parse_map_file(tmp_path / "missing.map")
        assert result is None

    def test_empty_file(self, tmp_path, capsys):
        map_file = tmp_path / "empty.map"
        map_file.write_text("", encoding="utf-8")
        result = parse_map_file(map_file)
        assert result is not None
        assert result.ram_bytes == 0
        assert result.rom_bytes == 0
        captured = capsys.readouterr()
        assert "Warning" in captured.err
        assert "No RAM/ROM data extracted" in captured.err

    def test_sets_source_and_timestamp(self, tmp_path):
        map_file = tmp_path / "test.map"
        map_file.write_text("some content", encoding="utf-8")
        result = parse_map_file(map_file)
        assert result.source_file == str(map_file)
        assert result.timestamp  # non-empty

    def test_invalid_hex_values(self, tmp_path):
        """Exercise ValueError except branch in parse_map_file."""
        map_file = tmp_path / "bad.map"
        map_file.write_text(
            ".text   0x08000000   NOT_HEX\n"
            ".bss    0x20000000   ALSO_BAD\n",
            encoding="utf-8",
        )
        result = parse_map_file(map_file)
        assert result is not None


class TestSaveBaseline:
    def test_saves_json(self, tmp_path):
        metrics = ResourceMetrics(
            ram_bytes=1024, rom_bytes=2048,
            source_file="test.map", timestamp="2026-01-01T00:00:00",
        )
        output = tmp_path / "baseline.json"
        save_baseline(metrics, output)

        assert output.exists()
        data = json.loads(output.read_text())
        assert data["ram_bytes"] == 1024
        assert data["rom_bytes"] == 2048

    def test_creates_parent_dirs(self, tmp_path):
        metrics = ResourceMetrics(
            ram_bytes=100, rom_bytes=200,
            source_file="test.map", timestamp="2026-01-01",
        )
        output = tmp_path / "nested" / "dir" / "baseline.json"
        save_baseline(metrics, output)
        assert output.exists()


class TestLoadMetrics:
    def test_loads_json(self, tmp_path):
        json_file = tmp_path / "metrics.json"
        json_file.write_text(json.dumps({
            "ram_bytes": 512, "rom_bytes": 1024,
            "source_file": "test.map", "timestamp": "2026-01-01",
        }))
        result = load_metrics(json_file)
        assert result.ram_bytes == 512
        assert result.rom_bytes == 1024

    def test_nonexistent_file(self, tmp_path):
        result = load_metrics(tmp_path / "missing.json")
        assert result is None


class TestCompareMetrics:
    def test_within_limits(self):
        baseline = ResourceMetrics(ram_bytes=1000, rom_bytes=2000, source_file="b", timestamp="t1")
        current = ResourceMetrics(ram_bytes=1050, rom_bytes=2100, source_file="c", timestamp="t2")
        result = compare_metrics(baseline, current, limit_percent=10.0)
        assert result["overall_pass"] is True
        assert result["delta"]["ram_bytes"] == 50
        assert result["delta"]["rom_bytes"] == 100

    def test_exceeds_limits(self):
        baseline = ResourceMetrics(ram_bytes=1000, rom_bytes=2000, source_file="b", timestamp="t1")
        current = ResourceMetrics(ram_bytes=1200, rom_bytes=2000, source_file="c", timestamp="t2")
        result = compare_metrics(baseline, current, limit_percent=10.0)
        assert result["overall_pass"] is False
        assert result["limits"]["ram_within_limit"] is False

    def test_zero_baseline(self):
        baseline = ResourceMetrics(ram_bytes=0, rom_bytes=0, source_file="b", timestamp="t1")
        current = ResourceMetrics(ram_bytes=100, rom_bytes=100, source_file="c", timestamp="t2")
        result = compare_metrics(baseline, current)
        assert result["delta"]["ram_percent"] == 0
        assert result["delta"]["rom_percent"] == 0
        assert result["overall_pass"] is False
        assert result["limits"]["ram_within_limit"] is False
        assert result["limits"]["rom_within_limit"] is False
        assert len(result["warnings"]) == 2

    def test_zero_baseline_both_zero_passes(self):
        baseline = ResourceMetrics(ram_bytes=0, rom_bytes=0, source_file="b", timestamp="t1")
        current = ResourceMetrics(ram_bytes=0, rom_bytes=0, source_file="c", timestamp="t2")
        result = compare_metrics(baseline, current)
        assert result["overall_pass"] is True
        assert "warnings" not in result

    def test_decrease_within_limit(self):
        baseline = ResourceMetrics(ram_bytes=1000, rom_bytes=2000, source_file="b", timestamp="t1")
        current = ResourceMetrics(ram_bytes=950, rom_bytes=1900, source_file="c", timestamp="t2")
        result = compare_metrics(baseline, current, limit_percent=10.0)
        assert result["overall_pass"] is True
        assert result["delta"]["ram_bytes"] == -50


class TestPrintComparisonReport:
    def test_prints_pass_report(self, capsys):
        baseline = ResourceMetrics(ram_bytes=1000, rom_bytes=2000, source_file="b", timestamp="t1")
        current = ResourceMetrics(ram_bytes=1050, rom_bytes=2050, source_file="c", timestamp="t2")
        result = compare_metrics(baseline, current)
        print_comparison_report(result)
        captured = capsys.readouterr()
        assert "PASS" in captured.out
        assert "RAM" in captured.out

    def test_prints_fail_report(self, capsys):
        baseline = ResourceMetrics(ram_bytes=1000, rom_bytes=2000, source_file="b", timestamp="t1")
        current = ResourceMetrics(ram_bytes=2000, rom_bytes=4000, source_file="c", timestamp="t2")
        result = compare_metrics(baseline, current, limit_percent=5.0)
        print_comparison_report(result)
        captured = capsys.readouterr()
        assert "FAIL" in captured.out


class TestMainCli:
    def test_no_command_exits(self, monkeypatch):
        from resource_tracker import main
        monkeypatch.setattr("sys.argv", ["resource_tracker.py"])
        with pytest.raises(SystemExit):
            main()

    def test_baseline_command(self, tmp_path, monkeypatch):
        from resource_tracker import main
        map_file = tmp_path / "test.map"
        map_file.write_text("Total RO  Size (Code + RO Data)    1024 bytes\nTotal RW  Size (RW Data + ZI Data)  512 bytes\n")
        output = tmp_path / "baseline.json"
        monkeypatch.setattr("sys.argv", [
            "resource_tracker.py", "baseline", str(map_file), str(output),
        ])
        main()
        assert output.exists()

    def test_baseline_missing_map_exits(self, tmp_path, monkeypatch):
        from resource_tracker import main
        monkeypatch.setattr("sys.argv", [
            "resource_tracker.py", "baseline", str(tmp_path / "nope.map"), str(tmp_path / "out.json"),
        ])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_compare_command_pass(self, tmp_path, monkeypatch):
        import json as json_mod
        from resource_tracker import main

        baseline = tmp_path / "baseline.json"
        baseline.write_text(json_mod.dumps({
            "ram_bytes": 1000, "rom_bytes": 2000,
            "source_file": "b.map", "timestamp": "t1",
        }))
        map_file = tmp_path / "current.map"
        map_file.write_text("Total RO  Size (Code + RO Data)    2050 bytes\nTotal RW  Size (RW Data + ZI Data)  1050 bytes\n")
        output = tmp_path / "compare.json"

        monkeypatch.setattr("sys.argv", [
            "resource_tracker.py", "compare", str(baseline), str(map_file), "--output", str(output),
        ])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        assert output.exists()

    def test_compare_command_fail(self, tmp_path, monkeypatch):
        import json as json_mod
        from resource_tracker import main

        baseline = tmp_path / "baseline.json"
        baseline.write_text(json_mod.dumps({
            "ram_bytes": 1000, "rom_bytes": 2000,
            "source_file": "b.map", "timestamp": "t1",
        }))
        map_file = tmp_path / "current.map"
        map_file.write_text("Total RO  Size (Code + RO Data)    9000 bytes\nTotal RW  Size (RW Data + ZI Data)  5000 bytes\n")

        monkeypatch.setattr("sys.argv", [
            "resource_tracker.py", "compare", str(baseline), str(map_file),
        ])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_report_command(self, tmp_path, monkeypatch):
        import json as json_mod
        from resource_tracker import main

        baseline = tmp_path / "baseline.json"
        baseline.write_text(json_mod.dumps({
            "ram_bytes": 1000, "rom_bytes": 2000,
            "source_file": "b.map", "timestamp": "t1",
        }))
        current = tmp_path / "current.json"
        current.write_text(json_mod.dumps({
            "ram_bytes": 1050, "rom_bytes": 2050,
            "source_file": "c.map", "timestamp": "t2",
        }))

        monkeypatch.setattr("sys.argv", [
            "resource_tracker.py", "report", str(baseline), str(current),
        ])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    def test_compare_missing_baseline_exits(self, tmp_path, monkeypatch):
        from resource_tracker import main
        map_file = tmp_path / "current.map"
        map_file.write_text("some content")
        monkeypatch.setattr("sys.argv", [
            "resource_tracker.py", "compare", str(tmp_path / "nope.json"), str(map_file),
        ])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_report_missing_file_exits(self, tmp_path, monkeypatch):
        import json as json_mod
        from resource_tracker import main
        baseline = tmp_path / "baseline.json"
        baseline.write_text(json_mod.dumps({
            "ram_bytes": 100, "rom_bytes": 200,
            "source_file": "b.map", "timestamp": "t1",
        }))
        monkeypatch.setattr("sys.argv", [
            "resource_tracker.py", "report", str(baseline), str(tmp_path / "nope.json"),
        ])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
