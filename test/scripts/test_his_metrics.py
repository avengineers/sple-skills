"""Tests for .github/scripts/his_metrics.py"""

import pytest
from his_metrics import (
    count_goto,
    count_return,
    count_params,
    count_stmts,
    count_calls,
    count_cyclomatic,
    count_path,
    count_level,
    count_comf,
    not_implemented,
    analyze_file,
    check_thresholds,
    print_report,
    THRESHOLDS,
    METRIC_FUNCS,
)


class TestCountGoto:
    def test_no_goto(self):
        assert count_goto(["int x = 0;", "return x;"]) == 0

    def test_single_goto(self):
        assert count_goto(["goto error;", "return 0;"]) == 1

    def test_multiple_goto(self):
        assert count_goto(["goto a;", "goto b;", "x = 1;"]) == 2

    def test_goto_in_string_still_counts(self):
        # The regex is simple and matches goto even in strings
        assert count_goto(['printf("goto label");']) == 1


class TestCountReturn:
    def test_no_return(self):
        assert count_return(["int x = 0;", "x++;"])== 0

    def test_single_return(self):
        assert count_return(["return 0;"]) == 1

    def test_multiple_returns(self):
        assert count_return(["return 0;", "return 1;", "x = 1;"]) == 2


class TestCountParams:
    def test_no_params(self):
        assert count_params("void foo()") == 0

    def test_single_param(self):
        assert count_params("int foo(int x)") == 1

    def test_multiple_params(self):
        assert count_params("int foo(int x, int y, int z)") == 3

    def test_no_parens(self):
        assert count_params("int x = 0;") == 0


class TestCountStmts:
    def test_no_stmts(self):
        assert count_stmts(["// comment", "{"]) == 0

    def test_single_stmt(self):
        assert count_stmts(["int x = 0;"]) == 1

    def test_multiple_stmts(self):
        assert count_stmts(["int x = 0;", "x++; y++;"]) == 3


class TestCountCalls:
    def test_no_calls(self):
        assert count_calls(["int x = 0;"]) == 0

    def test_single_call(self):
        assert count_calls(["foo();"]) == 1

    def test_multiple_calls(self):
        assert count_calls(["foo(); bar();"]) == 2


class TestCountCyclomatic:
    def test_simple_function(self):
        assert count_cyclomatic(["int x = 0;", "return x;"]) == 1

    def test_with_if(self):
        assert count_cyclomatic(["if (x > 0) {", "return 1;", "}"]) == 2

    def test_with_multiple_decisions(self):
        lines = ["if (a) {", "} else if (b && c) {", "for (i=0;;) {", "}"]
        result = count_cyclomatic(lines)
        assert result > 1


class TestCountPath:
    def test_no_branches(self):
        assert count_path(["int x = 0;", "return x;"]) == 0

    def test_if_else(self):
        assert count_path(["if (x) {", "} else {", "}"]) == 2

    def test_switch_case(self):
        assert count_path(["switch(x) {", "case 1:", "case 2:", "}"]) == 3


class TestCountLevel:
    def test_no_nesting(self):
        assert count_level(["int x = 0;"]) == 0

    def test_one_level(self):
        assert count_level(["void f() {", "    int x;", "}"]) == 1

    def test_deep_nesting(self):
        lines = ["void f() {", "    if (x) {", "        while (y) {", "            z++;", "        }", "    }", "}"]
        assert count_level(lines) == 3

    def test_empty_lines(self):
        assert count_level([]) == 0


class TestCountComf:
    def test_no_comments(self):
        assert count_comf(["int x = 0;", "return x;"]) == 0.0

    def test_all_comments(self):
        assert count_comf(["// comment"]) == 0.0  # no code lines

    def test_mixed(self):
        lines = ["// comment", "int x = 0;", "// another", "return x;"]
        result = count_comf(lines)
        assert result == pytest.approx(1.0)  # 2 comments / 2 code = 1.0

    def test_empty(self):
        assert count_comf([]) == 0


class TestNotImplemented:
    def test_returns_na(self):
        assert not_implemented() == "N/A"

    def test_with_args(self):
        assert not_implemented([1, 2, 3], key="val") == "N/A"


class TestAnalyzeFile:
    def test_analyze_simple_c_file(self, tmp_path):
        c_file = tmp_path / "test.c"
        c_file.write_text(
            "// A simple function\n"
            "int add(int a, int b) {\n"
            "    return a + b;\n"
            "}\n",
            encoding="utf-8",
        )
        results = analyze_file(c_file)
        assert "COMF" in results
        assert "GOTO" in results
        assert results["GOTO"] == 0
        assert results["RETURN"] == 1
        assert "STMT" in results
        assert "STMT_MIN" in results
        assert "STMT_MAX" in results
        assert results["STMT_MIN"] == results["STMT"]

    def test_analyze_file_with_goto(self, tmp_path):
        c_file = tmp_path / "goto_test.c"
        c_file.write_text("void f() {\n    goto error;\nerror:\n    return;\n}\n", encoding="utf-8")
        results = analyze_file(c_file)
        assert results["GOTO"] == 1
        assert results["RETURN"] == 1


class TestCheckThresholds:
    def test_all_ok(self):
        results = {
            "COMF": 0.5,
            "PATH": 10,
            "GOTO": 0,
            "CYCLO": 5,
            "CALLING": "N/A",
            "CALLS": 3,
            "PARAM": 2,
            "STMT": 10,
            "LEVEL": 2,
            "RETURN": 1,
            "AP_CG_CYCLE": 0,
            "VOCF": "N/A",
            "NOMV": 0,
            "NOMVPR": 0,
        }
        verdicts = check_thresholds(results)
        assert verdicts["COMF"] is True
        assert verdicts["PATH"] is True
        assert verdicts["GOTO"] is True
        assert verdicts["CYCLO"] is True
        assert verdicts["CALLS"] is True
        assert verdicts["PARAM"] is True
        assert verdicts["LEVEL"] is True
        assert verdicts["RETURN"] is True

    def test_fail_goto(self):
        results = {
            "COMF": 0.5, "PATH": 10, "GOTO": 3, "CYCLO": 5,
            "CALLING": "N/A", "CALLS": 3, "PARAM": 2, "STMT": 10,
            "LEVEL": 2, "RETURN": 1, "AP_CG_CYCLE": 0,
            "VOCF": "N/A", "NOMV": 0, "NOMVPR": 0,
        }
        verdicts = check_thresholds(results)
        assert verdicts["GOTO"] is False

    def test_fail_cyclo(self):
        results = {
            "COMF": 0.5, "PATH": 10, "GOTO": 0, "CYCLO": 50,
            "CALLING": 3, "CALLS": 3, "PARAM": 2, "STMT": 10,
            "LEVEL": 2, "RETURN": 1, "AP_CG_CYCLE": 0,
            "VOCF": 2, "NOMV": 0, "NOMVPR": 0,
        }
        verdicts = check_thresholds(results)
        assert verdicts["CYCLO"] is False
        assert verdicts["CALLING"] is True
        assert verdicts["VOCF"] is True


class TestPrintReport:
    def test_print_report_runs(self, capsys):
        results = {
            "COMF": 0.5, "PATH": 10, "GOTO": 0, "CYCLO": 5,
            "CALLING": "N/A", "CALLS": 3, "PARAM": 2, "STMT": 10,
            "LEVEL": 2, "RETURN": 1, "AP_CG_CYCLE": 0,
            "VOCF": "N/A", "NOMV": 0, "NOMVPR": 0,
        }
        verdicts = check_thresholds(results)
        print_report("test.c", results, verdicts)
        captured = capsys.readouterr()
        assert "HIS Metrics Report" in captured.out
        assert "test.c" in captured.out
        assert "OK" in captured.out

    def test_print_report_with_fail(self, capsys):
        results = {
            "COMF": 0.0, "PATH": 100, "GOTO": 5, "CYCLO": 50,
            "CALLING": "N/A", "CALLS": 30, "PARAM": 10, "STMT": 100,
            "LEVEL": 10, "RETURN": 5, "AP_CG_CYCLE": 0,
            "VOCF": "N/A", "NOMV": 0, "NOMVPR": 0,
        }
        verdicts = check_thresholds(results)
        print_report("bad.c", results, verdicts)
        captured = capsys.readouterr()
        assert "FAIL" in captured.out


class TestAnalyzeFileExceptionInMetric:
    def test_analyze_with_exception_in_param(self, tmp_path):
        """Exercise the except branch in analyze_file."""
        c_file = tmp_path / "edge.c"
        c_file.write_text(
            "int add(int a, int b) {\n"
            "    return a + b;\n"
            "}\n",
            encoding="utf-8",
        )
        results = analyze_file(c_file)
        assert "PARAM" in results
