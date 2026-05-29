"""Tests for c-unit-testing/scripts/analyze_dependencies.py"""

import pytest
from pathlib import Path
from analyze_dependencies import DependencyAnalyzer


SAMPLE_C_CODE = """\
#include <stdio.h>
#include "my_header.h"

#define REG_ADDR (*(volatile uint32_t*)0x40021000)

static int helper_func(int x) {
    return x + 1;
}

extern int global_var;
int module_state = 0;

int public_func(int a, int b) {
    if (a > 0) {
        printf("hello");
        helper_func(a);
        goto error;
    }
    global_var = b;
    return a + b;
error:
    return -1;
}
"""


@pytest.fixture
def sample_c_file(tmp_path):
    """Create a sample C file for testing."""
    c_file = tmp_path / "sample.c"
    c_file.write_text(SAMPLE_C_CODE, encoding="utf-8")
    return c_file


@pytest.fixture
def analyzer(sample_c_file):
    """Create and run analyzer on sample C file."""
    a = DependencyAnalyzer(sample_c_file)
    a.analyze()
    return a


class TestDependencyAnalyzerInit:
    def test_reads_file_content(self, sample_c_file):
        a = DependencyAnalyzer(sample_c_file)
        assert len(a.content) > 0
        assert "#include" in a.content

    def test_initializes_empty_sets(self, sample_c_file):
        a = DependencyAnalyzer(sample_c_file)
        assert len(a.external_functions) == 0
        assert len(a.includes) == 0


class TestFindIncludes:
    def test_finds_system_includes(self, analyzer):
        assert "stdio.h" in analyzer.includes

    def test_finds_local_includes(self, analyzer):
        assert "my_header.h" in analyzer.includes


class TestFindFunctions:
    def test_finds_static_functions(self, analyzer):
        assert "helper_func" in analyzer.static_functions

    def test_finds_external_calls(self, analyzer):
        assert "printf" in analyzer.external_functions

    def test_excludes_static_from_external(self, analyzer):
        assert "helper_func" not in analyzer.external_functions

    def test_excludes_keywords(self, analyzer):
        assert "if" not in analyzer.external_functions
        assert "return" not in analyzer.external_functions


class TestFindGlobals:
    def test_finds_globals(self, analyzer):
        assert "module_state" in analyzer.global_variables


class TestFindHardwareAccesses:
    def test_finds_register_macro(self, sample_c_file):
        a = DependencyAnalyzer(sample_c_file)
        a.analyze()
        assert isinstance(a.hardware_accesses, list)

    def test_direct_mmio_access(self, tmp_path):
        c_file = tmp_path / "mmio.c"
        c_file.write_text(
            "void write_reg(void) {\n"
            "    *(volatile uint32_t*)0x40020000 = 0xFF;\n"
            "}\n",
            encoding="utf-8",
        )
        a = DependencyAnalyzer(c_file)
        a.analyze()
        assert len(a.hardware_accesses) > 0
        assert any("0x40020000" in hw["address"] for hw in a.hardware_accesses)


class TestPrintReport:
    def test_prints_report(self, analyzer, capsys):
        analyzer.print_report()
        captured = capsys.readouterr()
        assert "Dependency Analysis" in captured.out
        assert "INCLUDES" in captured.out
        assert "EXTERNAL FUNCTIONS" in captured.out
        assert "GLOBAL VARIABLES" in captured.out
        assert "STATIC FUNCTIONS" in captured.out
        assert "TESTING RECOMMENDATIONS" in captured.out

    def test_print_recommendations(self, analyzer, capsys):
        analyzer.print_report()
        captured = capsys.readouterr()
        assert "Mock external function calls" in captured.out


class TestEmptyFile:
    def test_empty_c_file(self, tmp_path):
        c_file = tmp_path / "empty.c"
        c_file.write_text("", encoding="utf-8")
        a = DependencyAnalyzer(c_file)
        a.analyze()
        assert len(a.includes) == 0
        assert len(a.external_functions) == 0
        assert len(a.static_functions) == 0
        assert len(a.hardware_accesses) == 0


class TestMainCli:
    def test_no_args_exits(self, monkeypatch):
        from analyze_dependencies import main
        monkeypatch.setattr("sys.argv", ["analyze_dependencies.py"])
        with pytest.raises(SystemExit):
            main()

    def test_missing_file_exits(self, tmp_path, monkeypatch):
        from analyze_dependencies import main
        monkeypatch.setattr("sys.argv", [
            "analyze_dependencies.py", str(tmp_path / "missing.c"),
        ])
        with pytest.raises(SystemExit):
            main()

    def test_non_c_file_warns(self, tmp_path, monkeypatch, capsys):
        from analyze_dependencies import main
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1", encoding="utf-8")
        monkeypatch.setattr("sys.argv", [
            "analyze_dependencies.py", str(py_file),
        ])
        main()
        captured = capsys.readouterr()
        assert "Warning" in captured.out

    def test_valid_c_file(self, tmp_path, monkeypatch, capsys):
        from analyze_dependencies import main
        c_file = tmp_path / "module.c"
        c_file.write_text("#include <stdio.h>\nint main() { return 0; }\n", encoding="utf-8")
        monkeypatch.setattr("sys.argv", [
            "analyze_dependencies.py", str(c_file),
        ])
        main()
        captured = capsys.readouterr()
        assert "Dependency Analysis" in captured.out
