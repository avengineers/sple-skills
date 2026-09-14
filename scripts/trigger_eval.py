"""Measure which skill an agent picks for a prompt.

The description in a skill's frontmatter decides whether the agent reaches for
that skill at all. It is therefore the one part of a skill that cannot be
improved by reading it: a rewrite that reads better may trigger worse, and this
skill set overlaps on purpose — `c-code-review-checklist` against
`c-code-review-comprehensive`, `test-coverage-roadmap` against `c-unit-testing`.
This harness turns that into a measurement.

    python scripts/trigger_eval.py test/evals/test-coverage-roadmap.json
    python scripts/trigger_eval.py test/evals/*.json --runs 5 --model sonnet

**This costs model calls** — one per case per run — so it is driven by hand and
is not part of the pull-request pipeline.

What it measures, and what it does not:

* Every run denies the tools that let the agent explore or act, leaving `Skill`.
  The agent therefore either invokes a skill or answers in prose, which is the
  routing decision and nothing else. A run with full tools wanders through the
  file system, costs many times as much, and buries the signal.
* The result is specific to one model. Trigger behaviour differs between them,
  so `--model` is recorded in the report and a number from one model says
  nothing about another.
* A pass is a rate over N runs, not a proof. The decision is sampled, so a
  single run is noise.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Everything that lets the agent explore or change the workspace. What is left
# is the Skill tool, so a run answers the routing question and stops.
DENIED_TOOLS = [
    "Agent",
    "Bash",
    "BashOutput",
    "Edit",
    "Glob",
    "Grep",
    "KillShell",
    "LSP",
    "NotebookEdit",
    "PowerShell",
    "Read",
    "SlashCommand",
    "TaskCreate",
    "TaskOutput",
    "TaskStop",
    "TodoWrite",
    "ToolSearch",
    "WebFetch",
    "WebSearch",
    "Write",
]

DEFAULT_RUNS = 3
DEFAULT_THRESHOLD = 0.5
DEFAULT_TIMEOUT = 180


@dataclass(frozen=True)
class Case:
    query: str
    should_trigger: bool
    expect: str | None = None
    """Which skill should win, when the set covers a cluster of them.

    The review skills overlap deliberately, and there the question is not
    whether one fires but which of three does. Naming the winner per case lets
    a single run cover the cluster rather than one run per skill.
    """

    def target(self, default: str) -> str:
        return self.expect or default


@dataclass(frozen=True)
class EvalSet:
    skill: str
    cases: list[Case]


@dataclass(frozen=True)
class Result:
    case: Case
    hits: int
    runs: int
    rate: float
    passed: bool
    others: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class Outcome:
    results: list[Result]

    @property
    def passed(self) -> bool:
        """An empty run is not a green run — it proved nothing."""
        return bool(self.results) and all(r.passed for r in self.results)


def load_eval_set(path: Path) -> EvalSet:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    skill = payload.get("skill")
    if not skill:
        raise ValueError(f"{path}: no 'skill' field — the set must name the skill under test")
    cases = payload.get("cases") or []
    if not cases:
        raise ValueError(f"{path}: no 'cases' — an empty set reports green and proves nothing")
    for entry in cases:
        if "should_trigger" not in entry and "expect" not in entry:
            raise ValueError(
                f"{path}: case {entry.get('query')!r} has neither 'should_trigger' nor 'expect'"
            )
    return EvalSet(
        skill=skill,
        cases=[
            Case(
                query=c["query"],
                # Naming the skill that should win says it should trigger.
                should_trigger=bool(c.get("should_trigger", "expect" in c)),
                expect=c.get("expect"),
            )
            for c in cases
        ],
    )


def invoked_skills(stream: str) -> set[str]:
    """Skill names used in a recorded `--output-format stream-json` run.

    The CLI writes warnings into the same stream, so a line that is not JSON is
    skipped rather than raised — one stray line must not discard a paid run.
    """
    found: set[str] = set()
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(event, dict):
            continue
        for block in (event.get("message") or {}).get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if block.get("name") != "Skill":
                continue
            name = ((block.get("input") or {}).get("skill") or "").strip()
            if name:
                found.add(name.split(":")[-1])  # `plugin:skill` is addressed, `skill` is meant
    return found


def loaded_plugins(stream: str) -> dict[str, str]:
    """Plugin name to directory, from the run's init event."""
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(event, dict) or event.get("subtype") != "init":
            continue
        if event.get("type") != "system":
            continue
        return {p.get("name", ""): p.get("path", "") for p in event.get("plugins") or []}
    return {}


def check_plugin_under_test(stream: str, expected: Path | None) -> None:
    """Stop unless the run loaded the plugin we meant to measure.

    Without this the harness silently measures the plugin installed for the
    account. That already happened once: a whole run compared the released
    description against itself, and the result looked plausible.
    """
    if expected is None:
        return
    wanted = Path(expected).resolve()
    paths = [Path(p).resolve() for p in loaded_plugins(stream).values() if p]
    if wanted not in paths:
        raise RuntimeError(
            f"the plugin under test is not loaded from {wanted}. Loaded instead: "
            f"{[str(p) for p in paths] or 'nothing'}. The measurement would describe "
            f"a different version than the one on disk here."
        )


def verdict(case: Case, hits: int, runs: int, threshold: float, others: set[str] | None = None) -> Result:
    rate = hits / runs if runs else 0.0
    passed = rate >= threshold if case.should_trigger else rate < threshold
    if not runs:
        passed = False  # nothing ran, so nothing was shown
    return Result(case=case, hits=hits, runs=runs, rate=rate, passed=passed, others=others or set())


def run_query(query: str, model: str, cwd: Path, timeout: int, plugin_dir: Path | None) -> str:
    command = [
        "claude",
        "-p",
        query,
        "--output-format",
        "stream-json",
        "--verbose",
        "--model",
        model,
        "--disallowedTools",
        *DENIED_TOOLS,
    ]
    if plugin_dir:
        # Without this the run measures the plugin **installed** for the
        # account, not the working tree. The two differ by exactly the edit
        # under test, so a before/after comparison would silently compare the
        # released description with itself.
        command += ["--plugin-dir", str(plugin_dir)]
    try:
        finished = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            # Windows hands a child process a cp1252 pipe, and the CLI writes
            # UTF-8. Without this the whole run dies on the first umlaut or dash
            # in a model's prose, after the call has already been paid for.
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return ""
    return finished.stdout or ""


def evaluate(
    eval_set: EvalSet,
    *,
    runs: int,
    threshold: float,
    model: str,
    cwd: Path,
    timeout: int,
    plugin_dir: Path | None = None,
    report: bool = True,
) -> Outcome:
    results = []
    verified = False
    for case in eval_set.cases:
        target = case.target(eval_set.skill)
        hits, others, executed = 0, set(), 0
        for _ in range(runs):
            stream = run_query(case.query, model, cwd, timeout, plugin_dir)
            if not verified:
                check_plugin_under_test(stream, plugin_dir)
                verified = True
            used = invoked_skills(stream)
            executed += 1
            if target in used:
                hits += 1
            others |= used - {target}
        result = verdict(case, hits, executed, threshold, others)
        results.append(result)
        if report:
            print(_line(result), flush=True)
    return Outcome(results=results)


def _line(result: Result) -> str:
    mark = "PASS" if result.passed else "FAIL"
    if result.case.expect:
        want = f"-> {result.case.expect}"
    else:
        want = "should trigger" if result.case.should_trigger else "must not trigger"
    tail = f"  (also: {', '.join(sorted(result.others))})" if result.others else ""
    return (
        f"{mark}  {result.hits}/{result.runs} = {result.rate:.0%}  {want:16} "
        f"{result.case.query!r}{tail}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("eval_sets", nargs="+", type=Path)
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--plugin-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "plugins" / "embedded-sple",
        help="plugin to load; defaults to this repository's, not the installed one",
    )
    args = parser.parse_args(argv)

    green = True
    for path in args.eval_sets:
        eval_set = load_eval_set(path)
        total = len(eval_set.cases) * args.runs
        print(
            f"\n=== {eval_set.skill} — {path.name}, {total} calls on {args.model}"
            f"\n    plugin under test: {args.plugin_dir} ==="
        )
        outcome = evaluate(
            eval_set,
            runs=args.runs,
            threshold=args.threshold,
            model=args.model,
            cwd=args.cwd,
            timeout=args.timeout,
            plugin_dir=args.plugin_dir,
        )
        green &= outcome.passed
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
