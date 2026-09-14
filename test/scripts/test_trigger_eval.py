"""Tests for the trigger-eval harness.

Only the parts that need no model: reading an eval set, deciding pass or fail
from a trigger rate, and reading a skill name out of a recorded event stream.
The calls themselves cost money and are driven by hand.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from trigger_eval import (  # noqa: E402
    Case,
    EvalSet,
    Outcome,
    check_plugin_under_test,
    invoked_skills,
    load_eval_set,
    loaded_plugins,
    verdict,
)


def _init_event(*plugins: dict) -> str:
    return json.dumps({"type": "system", "subtype": "init", "plugins": list(plugins)})


class TestLoadedPlugins:
    """Which plugin a run actually had loaded.

    The CLI reports this in its init event. Reading it is the only way to know
    that a measurement refers to the working tree and not to the version
    installed for the account — the two differ by exactly the edit under test.
    """

    def test_reads_name_and_path(self) -> None:
        stream = _init_event({"name": "a-plugin", "path": r"C:\repo\plugins\a"})

        assert loaded_plugins(stream) == {"a-plugin": r"C:\repo\plugins\a"}

    def test_ignores_everything_but_the_init_event(self) -> None:
        stream = json.dumps({"type": "assistant", "plugins": [{"name": "x", "path": "y"}]})

        assert loaded_plugins(stream) == {}

    def test_no_init_event_is_empty_not_an_error(self) -> None:
        assert loaded_plugins("") == {}


class TestCheckPluginUnderTest:
    """A run that loaded the wrong plugin must stop, not report a number."""

    def test_accepts_the_expected_directory(self, tmp_path: Path) -> None:
        wanted = tmp_path / "embedded-sple"
        stream = _init_event({"name": "p", "path": str(wanted)})

        check_plugin_under_test(stream, wanted)  # does not raise

    def test_rejects_a_plugin_loaded_from_somewhere_else(self, tmp_path: Path) -> None:
        wanted = tmp_path / "embedded-sple"
        stream = _init_event({"name": "p", "path": str(tmp_path / "cache" / "0.1.6")})

        with pytest.raises(RuntimeError, match="not loaded from"):
            check_plugin_under_test(stream, wanted)

    def test_rejects_a_run_that_loaded_no_plugin_at_all(self, tmp_path: Path) -> None:
        with pytest.raises(RuntimeError, match="not loaded from"):
            check_plugin_under_test(_init_event(), tmp_path / "embedded-sple")

    def test_accepts_any_path_when_none_was_requested(self) -> None:
        check_plugin_under_test(_init_event({"name": "p", "path": "anywhere"}), None)


class TestInvokedSkills:
    """Which skill a recorded run actually used."""

    @staticmethod
    def _stream(*blocks: dict) -> str:
        return "\n".join(
            json.dumps({"type": "assistant", "message": {"content": [b]}}) for b in blocks
        )

    def test_reads_the_skill_from_a_tool_use(self) -> None:
        stream = self._stream({"type": "tool_use", "name": "Skill", "input": {"skill": "a-skill"}})

        assert invoked_skills(stream) == {"a-skill"}

    def test_strips_the_plugin_prefix(self) -> None:
        """A skill is addressed as `plugin:skill`, the eval set names the skill."""
        stream = self._stream(
            {"type": "tool_use", "name": "Skill", "input": {"skill": "embedded-sple:a-skill"}}
        )

        assert invoked_skills(stream) == {"a-skill"}

    def test_ignores_other_tools(self) -> None:
        stream = self._stream({"type": "tool_use", "name": "Read", "input": {"file_path": "x"}})

        assert invoked_skills(stream) == set()

    def test_collects_every_skill_used(self) -> None:
        stream = self._stream(
            {"type": "tool_use", "name": "Skill", "input": {"skill": "first"}},
            {"type": "tool_use", "name": "Skill", "input": {"skill": "second"}},
        )

        assert invoked_skills(stream) == {"first", "second"}

    def test_survives_a_line_that_is_not_json(self) -> None:
        """The CLI prints warnings into the same stream; they must not abort a run."""
        stream = "not json\n" + self._stream(
            {"type": "tool_use", "name": "Skill", "input": {"skill": "a-skill"}}
        )

        assert invoked_skills(stream) == {"a-skill"}

    def test_no_skill_at_all_is_an_empty_set_not_an_error(self) -> None:
        assert invoked_skills("") == set()


class TestVerdict:
    """Pass or fail from a trigger rate, for both kinds of case."""

    def test_a_positive_case_passes_above_the_threshold(self) -> None:
        case = Case(query="q", should_trigger=True)

        assert verdict(case, hits=2, runs=3, threshold=0.5).passed is True

    def test_a_positive_case_fails_below_the_threshold(self) -> None:
        case = Case(query="q", should_trigger=True)

        assert verdict(case, hits=1, runs=3, threshold=0.5).passed is False

    def test_the_threshold_itself_counts_as_passing(self) -> None:
        case = Case(query="q", should_trigger=True)

        assert verdict(case, hits=1, runs=2, threshold=0.5).passed is True

    def test_a_negative_case_inverts_the_comparison(self) -> None:
        """`should_trigger: false` means the skill must stay below the threshold."""
        case = Case(query="q", should_trigger=False)

        assert verdict(case, hits=0, runs=3, threshold=0.5).passed is True
        assert verdict(case, hits=2, runs=3, threshold=0.5).passed is False

    def test_the_rate_is_reported_for_the_eye(self) -> None:
        case = Case(query="q", should_trigger=True)

        assert verdict(case, hits=1, runs=4, threshold=0.5).rate == pytest.approx(0.25)

    def test_zero_runs_cannot_pass_silently(self) -> None:
        """A run that never executed must not be reported as a success."""
        case = Case(query="q", should_trigger=True)
        result = verdict(case, hits=0, runs=0, threshold=0.5)

        assert result.passed is False
        assert result.rate == 0.0


class TestExpectedSkill:
    """A case may name which skill should win, instead of only yes or no.

    Three review skills overlap on purpose, and the interesting question there
    is not "does this one fire" but "which of the three". Naming the winner per
    case lets one run cover the whole cluster instead of one run per skill.
    """

    def test_a_case_without_expect_falls_back_to_the_set(self) -> None:
        assert Case(query="q", should_trigger=True).target("set-skill") == "set-skill"

    def test_expect_overrides_the_set(self) -> None:
        case = Case(query="q", should_trigger=True, expect="other-skill")

        assert case.target("set-skill") == "other-skill"

    def test_naming_a_winner_implies_it_should_trigger(self, tmp_path: Path) -> None:
        path = tmp_path / "set.json"
        path.write_text(
            json.dumps(
                {"skill": "cluster", "cases": [{"query": "q", "expect": "a-skill"}]}
            ),
            encoding="utf-8",
        )

        loaded = load_eval_set(path)

        assert loaded.cases == [Case(query="q", should_trigger=True, expect="a-skill")]


class TestLoadEvalSet:
    """The eval set is data in the repository, so a broken one must say why."""

    def _write(self, tmp_path: Path, payload: object) -> Path:
        target = tmp_path / "set.json"
        target.write_text(json.dumps(payload), encoding="utf-8")
        return target

    def test_reads_skill_and_cases(self, tmp_path: Path) -> None:
        path = self._write(
            tmp_path,
            {
                "skill": "test-coverage-roadmap",
                "cases": [
                    {"query": "raise coverage", "should_trigger": True},
                    {"query": "write one test", "should_trigger": False},
                ],
            },
        )

        loaded = load_eval_set(path)

        assert loaded == EvalSet(
            skill="test-coverage-roadmap",
            cases=[
                Case(query="raise coverage", should_trigger=True),
                Case(query="write one test", should_trigger=False),
            ],
        )

    def test_a_missing_skill_name_is_refused(self, tmp_path: Path) -> None:
        path = self._write(tmp_path, {"cases": []})

        with pytest.raises(ValueError, match="skill"):
            load_eval_set(path)

    def test_an_empty_case_list_is_refused(self, tmp_path: Path) -> None:
        """An eval set with no cases would report a green run that proved nothing."""
        path = self._write(tmp_path, {"skill": "x", "cases": []})

        with pytest.raises(ValueError, match="cases"):
            load_eval_set(path)

    def test_a_case_without_an_expectation_is_refused(self, tmp_path: Path) -> None:
        path = self._write(tmp_path, {"skill": "x", "cases": [{"query": "q"}]})

        with pytest.raises(ValueError, match="should_trigger"):
            load_eval_set(path)


class TestOutcome:
    """The summary a human reads."""

    def test_a_run_is_green_only_when_every_case_passed(self) -> None:
        assert Outcome(results=[verdict(Case("q", True), 3, 3, 0.5)]).passed is True
        assert (
            Outcome(
                results=[
                    verdict(Case("q", True), 3, 3, 0.5),
                    verdict(Case("r", True), 0, 3, 0.5),
                ]
            ).passed
            is False
        )

    def test_an_empty_run_is_not_green(self) -> None:
        assert Outcome(results=[]).passed is False
