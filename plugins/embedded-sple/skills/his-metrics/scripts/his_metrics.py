"""
HIS Metrics Analyzer for Embedded C
Calculates key HIS metrics and checks against configurable thresholds.

Usage: Place this script in your repo and run with a C file or directory as argument.

Thresholds can be adjusted at the top of the script.
"""

import sys
import re
from pathlib import Path

# === HIS Metric Thresholds (adjust as needed) ===
THRESHOLDS = {
    "COMF": 0.2,  # > 0.2
    "PATH": 80,  # <= 80
    "GOTO": 0,  # = 0
    "CYCLO": 10,  # <= 10 (v(G))
    "CALLING": 5,  # <= 5
    "CALLS": 7,  # <= 7
    "PARAM": 5,  # <= 5
    "STMT_MIN": 1,  # > 0
    "STMT_MAX": 50,  # <= 50
    "LEVEL": 4,  # <= 4
    "RETURN": [0, 1],  # Either 0 or 1
    "AP_CG_CYCLE": 0,  # = 0
    "VOCF": 4,  # <= 4
    "NOMV": 0,  # = 0
    "NOMVPR": 0,  # = 0
}


# === Metric Calculation Functions ===
def count_goto(lines):
    return sum(1 for l in lines if re.search(r"\bgoto\b", l))


def count_return(lines):
    return sum(1 for l in lines if re.search(r"\breturn\b", l))


def count_params(line):
    # crude: count commas in parameter list
    params = re.findall(r"\(([^)]*)\)", line)
    if params:
        return len([p for p in params[0].split(",") if p.strip()])
    return 0


def count_stmts(lines):
    # crude: count semicolons
    return sum(l.count(";") for l in lines)


def count_calls(lines):
    # crude: count function calls (foo(...))
    return sum(len(re.findall(r"\w+\s*\(", l)) for l in lines)


def count_cyclomatic(lines):
    # v(G) = 1 + number of decision points
    count = 1
    for l in lines:
        count += len(re.findall(r"\b(if|for|while|case|catch|\?\:|&&|\|\|)\b", l))
    return count


def count_path(lines):
    # crude: count number of unique paths (if/else/switch)
    return sum(len(re.findall(r"\b(if|else if|else|switch|case)\b", l)) for l in lines)


def count_level(lines):
    # crude: max indentation level
    return max((len(l) - len(l.lstrip(" "))) // 4 for l in lines if l.strip()) if lines else 0


def count_comf(lines):
    # crude: comment lines / total lines
    comment_lines = sum(1 for l in lines if l.strip().startswith("//") or l.strip().startswith("/*"))
    code_lines = sum(1 for l in lines if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("/*"))
    return comment_lines / code_lines if code_lines else 0


# Placeholders for advanced metrics (VOCF, NOMV, NOMVPR, AP_CG_CYCLE)
def not_implemented(*args, **kwargs):
    return "N/A"


METRIC_FUNCS = {
    "COMF": count_comf,
    "PATH": count_path,
    "GOTO": count_goto,
    "CYCLO": count_cyclomatic,
    "CALLING": not_implemented,
    "CALLS": count_calls,
    "PARAM": count_params,
    "STMT": count_stmts,
    "LEVEL": count_level,
    "RETURN": count_return,
    "AP_CG_CYCLE": not_implemented,
    "VOCF": not_implemented,
    "NOMV": not_implemented,
    "NOMVPR": not_implemented,
}


def analyze_file(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    results = {}
    for metric, func in METRIC_FUNCS.items():
        try:
            if metric == "PARAM":
                # Only count params for function definitions
                param_counts = [count_params(l) for l in lines if re.match(r"\w+\s+\w+\s*\(", l)]
                results[metric] = max(param_counts) if param_counts else 0
            else:
                results[metric] = func(lines)
        except Exception as e:
            results[metric] = f"ERR: {e}"
    # STMT min/max
    results["STMT_MIN"] = results["STMT"]
    results["STMT_MAX"] = results["STMT"]
    return results


def check_thresholds(results):
    verdicts = {}
    t = THRESHOLDS
    verdicts["COMF"] = results["COMF"] > t["COMF"]
    verdicts["PATH"] = results["PATH"] <= t["PATH"]
    verdicts["GOTO"] = results["GOTO"] == t["GOTO"]
    verdicts["CYCLO"] = results["CYCLO"] <= t["CYCLO"]
    verdicts["CALLING"] = "N/A" if results["CALLING"] == "N/A" else results["CALLING"] <= t["CALLING"]
    verdicts["CALLS"] = results["CALLS"] <= t["CALLS"]
    verdicts["PARAM"] = results["PARAM"] <= t["PARAM"]
    verdicts["STMT"] = t["STMT_MIN"] < results["STMT"] <= t["STMT_MAX"]
    verdicts["LEVEL"] = results["LEVEL"] <= t["LEVEL"]
    verdicts["RETURN"] = results["RETURN"] in t["RETURN"]
    verdicts["AP_CG_CYCLE"] = results["AP_CG_CYCLE"] == t["AP_CG_CYCLE"]
    verdicts["VOCF"] = "N/A" if results["VOCF"] == "N/A" else results["VOCF"] <= t["VOCF"]
    verdicts["NOMV"] = results["NOMV"] == t["NOMV"]
    verdicts["NOMVPR"] = results["NOMVPR"] == t["NOMVPR"]
    return verdicts


def print_report(path, results, verdicts):
    print(f"\nHIS Metrics Report for: {path}")
    for metric in THRESHOLDS:
        val = results.get(metric, "N/A")
        verdict = verdicts.get(metric, "N/A")
        print(f"{metric:12}: {val:8} | {'OK' if verdict else 'FAIL'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python his_metrics.py <file.c | dir>")
        sys.exit(1)
    target = Path(sys.argv[1])
    files = [target] if target.is_file() else list(target.rglob("*.c"))
    for f in files:
        results = analyze_file(f)
        verdicts = check_thresholds(results)
        print_report(f, results, verdicts)
