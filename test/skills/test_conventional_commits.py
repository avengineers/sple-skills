"""Behavioural tests for the `conventional-commits` issue reference extraction.

The extraction is not Python. It lives as a Bash and a PowerShell snippet inside
`SKILL.md`, and an agent copies it out and runs it. Reading the document cannot
answer whether a given branch name produces the right reference, so these tests
lift the snippets out of the document and execute them against real throwaway
repositories.

The defect they were written for: the snippets used to try a JIRA key first and
only then a GitHub issue number. On a repository hosted at github.com that puts
an internal ticket ID into a permanent public history, and the GitHub fallback
required a slash before the number, so `358-short-description` -- the shape
GitHub generates from an issue -- matched nothing at all.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

SKILL = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "embedded-sple"
    / "skills"
    / "conventional-commits"
    / "SKILL.md"
)

EXTRACTION_HEADING = re.compile(r"^##\s+Issue Reference Extraction\s*$", re.MULTILINE)
NEXT_H2 = re.compile(r"^##\s+", re.MULTILINE)

GITHUB_REMOTE = "https://github.com/avengineers/sple-skills.git"
# A stand-in for any non-GitHub host. This repository is public, so no real
# internal host name belongs in it.
OTHER_REMOTE = "https://git.example.com/scm/proj/component.git"


def _extraction_section() -> str:
    text = SKILL.read_text(encoding="utf-8")
    start = EXTRACTION_HEADING.search(text)
    assert start, f"{SKILL}: no '## Issue Reference Extraction' section"
    rest = text[start.end() :]
    end = NEXT_H2.search(rest)
    return rest[: end.start()] if end else rest


def _snippet(language: str) -> str:
    """The first fenced block of `language` in the extraction section.

    Matching on the fence language rather than on a preceding heading keeps the
    test working when the headings are reworded, which happened once already.
    """
    section = _extraction_section()
    fence = re.search(rf"^```{language}\s*$(.*?)^```\s*$", section, re.MULTILINE | re.DOTALL)
    assert fence, f"{SKILL}: the extraction section has no ```{language} block"
    return fence.group(1)


def _repo(tmp_path: Path, remote: str, branch: str) -> Path:
    """A repository on `branch` whose `origin` points at `remote`.

    The empty commit is not optional. On an unborn HEAD `git rev-parse
    --abbrev-ref HEAD` fails and prints "HEAD", so every case extracted nothing
    and the whole table went green against a broken snippet.
    """
    git = ["git", "-C", str(tmp_path), "-c", "user.name=test", "-c", "user.email=test@example.com"]
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run([*git, "remote", "add", "origin", remote], check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "init"], check=True)
    subprocess.run([*git, "checkout", "-q", "-b", branch], check=True)
    return tmp_path


def _bash() -> str:
    r"""Git Bash on Windows, the system bash elsewhere -- never the WSL launcher.

    Windows resolves a bare `bash` through `C:\Windows\System32` before PATH,
    and on the GitHub Windows runners that is the WSL launcher, which exits 1
    without a Linux distribution. Every Bash case failed there while passing on
    a machine without WSL. Walking PATH explicitly skips it.
    """
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        found = shutil.which("bash", path=directory)
        if found and not any(part in found.lower() for part in ("system32", "windowsapps")):
            return found
    pytest.fail("no bash on PATH other than the WSL launcher")


def _run(command: list[str], repo: Path) -> str:
    """Stdout of `command`, failing with its stderr when it exits non-zero."""
    result = subprocess.run(command, cwd=repo, capture_output=True, encoding="utf-8")
    assert result.returncode == 0, (
        f"{command[0]} exited {result.returncode}. stderr: {result.stderr.strip()!r}"
    )
    return result.stdout


def _reference(output: str) -> str:
    """The reference the snippet printed, or '' when it printed none."""
    match = re.search(r"Issue reference:\s*(\S*)\s*$", output.strip())
    assert match, f"the snippet printed no 'Issue reference:' line, got: {output!r}"
    return match.group(1)


# remote, branch, expected reference
CASES = [
    pytest.param(GITHUB_REMOTE, "358-configure-the-logger", "(#358)", id="github-bare-number"),
    pytest.param(GITHUB_REMOTE, "feature/358-short-description", "(#358)", id="github-prefixed"),
    pytest.param(GITHUB_REMOTE, "feature/PROJ-1234-short", "", id="github-never-leaks-a-jira-key"),
    pytest.param(OTHER_REMOTE, "feature/PROJ-1234-short", "(PROJ-1234)", id="other-host-jira"),
    pytest.param(OTHER_REMOTE, "feature/123-short", "(#123)", id="other-host-number"),
    pytest.param(OTHER_REMOTE, "feature/short-description", "", id="no-reference-in-branch"),
]


@pytest.mark.parametrize("remote,branch,expected", CASES)
def test_bash_snippet_extracts_the_reference(
    tmp_path: Path, remote: str, branch: str, expected: str
) -> None:
    repo = _repo(tmp_path, remote, branch)
    output = _run([_bash(), "-c", _snippet("bash")], repo)
    assert _reference(output) == expected, (
        f"branch {branch!r} on remote {remote!r} must yield {expected!r}. "
        f"The snippet in {SKILL} printed: {output.strip()!r}"
    )


@pytest.mark.skipif(
    shutil.which("pwsh") is None and shutil.which("powershell") is None,
    reason="no PowerShell on this machine",
)
@pytest.mark.parametrize("remote,branch,expected", CASES)
def test_powershell_snippet_extracts_the_reference(
    tmp_path: Path, remote: str, branch: str, expected: str
) -> None:
    shell = shutil.which("pwsh") or shutil.which("powershell")
    repo = _repo(tmp_path, remote, branch)
    output = _run([shell, "-NoProfile", "-Command", _snippet("powershell")], repo)
    assert _reference(output) == expected, (
        f"branch {branch!r} on remote {remote!r} must yield {expected!r}. "
        f"The snippet in {SKILL} printed: {output.strip()!r}"
    )


def test_the_workflow_example_carries_no_host_blind_extraction() -> None:
    """The worked example must not hold a second, simpler copy of the logic.

    The example is what an agent reads when it follows the whole workflow end to
    end, and it used to repeat the extraction with a JIRA-first chain. A second
    copy is a second place to forget. Either it defers to the extraction section
    or it makes the same host distinction -- matching a JIRA key without ever
    looking at the remote is the one thing it may not do.
    """
    text = SKILL.read_text(encoding="utf-8")
    example = re.search(
        r"^##\s+Complete Commit Workflow Example\s*$(.*?)^##\s+", text, re.MULTILINE | re.DOTALL
    )
    assert example, f"{SKILL}: no '## Complete Commit Workflow Example' section"
    body = example.group(1)
    matches_jira = re.search(r"\[A-Z\]\{2,\}-", body)
    assert not matches_jira or "git remote" in body, (
        f"{SKILL}: the workflow example matches a JIRA key without reading the remote, "
        "so following it puts an internal ticket ID into a commit on a public "
        "GitHub-hosted repository. Defer to the extraction section instead of copying it."
    )


COMMIT_EXAMPLES_HEADING = re.compile(r"^##\s+Commit Examples\s*$", re.MULTILINE)
BAD_EXAMPLE_MARKER = "**Before — do not copy:**"
FENCE = re.compile(r"^```[\w-]*\s*$(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
FILE_PATH = re.compile(
    r"\b[\w./-]+\.(?:c|cc|cpp|h|hpp|py|md|json|yaml|yml|toml|lock|txt|cmake|ps1|sh|js|ts|ini|cfg)\b"
)
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
SUBJECT = re.compile(r"^[a-z]+(?:\([^)]*\))?!?: ")


def _example_bodies() -> list[tuple[str, str]]:
    """(subject, body) of every commit example, minus the marked bad example."""
    text = SKILL.read_text(encoding="utf-8")
    start = COMMIT_EXAMPLES_HEADING.search(text)
    assert start, f"{SKILL}: no '## Commit Examples' section"
    rest = text[start.end() :]
    end = NEXT_H2.search(rest)
    section = rest[: end.start()] if end else rest

    bodies = []
    for fence in FENCE.finditer(section):
        preceding = section[: fence.start()].rstrip().splitlines()
        if preceding and preceding[-1].strip() == BAD_EXAMPLE_MARKER:
            continue
        subject, *rest_lines = fence.group(1).strip().splitlines()
        body = "\n".join(rest_lines).strip()
        # A block of one-line subjects is a list of examples, not a body.
        if body and not all(SUBJECT.match(line) for line in body.splitlines() if line.strip()):
            bodies.append((subject, body))
    return bodies


def test_the_examples_include_a_body() -> None:
    """Guards the next test: an empty list would pass it for nothing."""
    assert _example_bodies(), f"{SKILL}: no commit example with a body left to check"


@pytest.mark.parametrize(
    "subject, body", _example_bodies(), ids=[subject for subject, _ in _example_bodies()]
)
def test_an_example_body_does_not_repeat_the_diff(subject: str, body: str) -> None:
    """Agents copy the examples, not the rule above them.

    Bodies that listed files and changed settings taught agents to write commit
    bodies that only repeat what the diff shows. An example body explains why,
    in a few lines of prose. Only a block marked as the bad example may show
    the wrong shape.
    """
    bullets = [line for line in body.splitlines() if LIST_ITEM.match(line)]
    paths = FILE_PATH.findall(body)
    assert not bullets and not paths, (
        f"{SKILL}: the body of '{subject}' lists {bullets or paths}. "
        "A body explains why; the diff already shows what changed."
    )


SKILLS = SKILL.parents[1]
TEMPLATE_MESSAGE = re.compile(r"^.*\bMessage: `([^`]*)`", re.MULTILINE | re.IGNORECASE)
VALID_TYPES = ("feat", "fix", "refactor", "style", "build", "ci", "chore", "docs", "test", "<type>")


def _template_messages() -> list[tuple[str, str]]:
    return [
        (path.relative_to(SKILLS).as_posix(), message)
        for path in sorted(SKILLS.rglob("*.md"))
        for message in TEMPLATE_MESSAGE.findall(path.read_text(encoding="utf-8"))
    ]


def test_the_templates_carry_commit_messages() -> None:
    """Guards the next test: an empty list would pass it for nothing."""
    assert _template_messages(), f"{SKILLS}: no '- Message: `...`' line found in any template"


@pytest.mark.parametrize("path, message", _template_messages())
def test_a_template_commit_message_uses_a_valid_type(path: str, message: str) -> None:
    """Roadmap templates suggest commit subjects, and agents fill them in as given.

    An invented type fails commitlint, and `feat:` on a test-only commit breaks
    the skill's own rule that such commits are always `test:`.
    """
    commit_type = message.split(":", 1)[0]
    assert commit_type in VALID_TYPES, f"{path}: '{message}' uses the type '{commit_type}'"
    if "test-coverage-roadmap" in path:
        assert commit_type == "test", f"{path}: a commit that adds unit tests is `test:`"
