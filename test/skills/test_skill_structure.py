"""Mechanical consistency checks for the skill documents.

Reading a long process document critically yields an unlimited supply of
inconsistencies, so review rounds never converge. Most of those findings are
mechanically checkable, which makes them a job for this suite rather than for
another review round.

These tests read markdown only. They never call a model and run in
milliseconds, so they belong in the pull-request pipeline.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

SKILLS_ROOT = Path(__file__).resolve().parents[2] / "plugins" / "embedded-sple" / "skills"
WORKFLOW_ENGINE = SKILLS_ROOT / "shared" / "roadmap-common" / "roadmap-workflow-engine.md"

# The step id is the join between the shared base and every consuming skill.
# Both sides already carry it, so nothing has to be duplicated to compare them.
STEP_ID = re.compile(r"^(\d+\.\d+[a-z]?)\b")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _anchored_block(text: str, anchor: str, source: Path) -> str:
    """The text between `<!-- anchor:begin -->` and `<!-- anchor:end -->`.

    An HTML comment is invisible in rendered markdown and exact for a parser,
    so the block stays human-readable prose while staying machine-locatable.
    Locating it by heading instead would break on every rename.
    """
    match = re.search(
        rf"<!--\s*{re.escape(anchor)}:begin\s*-->(.*?)<!--\s*{re.escape(anchor)}:end\s*-->",
        text,
        re.DOTALL,
    )
    if match is None:
        pytest.fail(f"{source}: no `{anchor}` block — expected <!-- {anchor}:begin/end --> markers")
    return match.group(1)


def _table_step_ids(block: str) -> list[str]:
    """Step ids from the first column of a markdown table."""
    ids = []
    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        first = line.strip().strip("|").split("|")[0].strip()
        found = STEP_ID.match(first)
        if found:
            ids.append(found.group(1))
    return ids


def _box_step_ids(block: str) -> list[str]:
    """Step ids from the rows of an ASCII definition-of-done box."""
    ids = []
    for line in block.splitlines():
        row = line.strip()
        if not row.startswith("║"):  # box drawing double vertical
            continue
        found = STEP_ID.match(row.lstrip("║").strip())
        if found:
            ids.append(found.group(1))
    return ids


def _consuming_skills() -> list[Path]:
    """Skills that delegate their workflow to the shared roadmap engine.

    Discovered from the reference itself, so a new roadmap skill is covered
    without editing this test.
    """
    found = [
        skill
        for skill in sorted(SKILLS_ROOT.glob("*/SKILL.md"))
        if "roadmap-common/roadmap-workflow-engine.md" in _read(skill)
    ]
    assert found, "no skill references the roadmap workflow engine — check the path"
    return found


def _skill_id(path: Path) -> str:
    return path.parent.name


def _reference_id(path: Path) -> str:
    return f"{path.parent.parent.name}/{path.name}"


DOD_HEADING = re.compile(r"^#{2,4}\s+Definition of Done\s*$", re.MULTILINE)
NEXT_BLOCK = re.compile(r"^(#{1,4}\s|---\s*$)", re.MULTILINE)


def _dod_sections(path: Path) -> list[str]:
    """Every `Definition of Done` section of a document, body only."""
    text = _read(path)
    sections = []
    for heading in DOD_HEADING.finditer(text):
        rest = text[heading.end() :]
        end = NEXT_BLOCK.search(rest)
        sections.append(rest[: end.start()] if end else rest)
    return sections


REQUIRED_SKILLS_HEADING = re.compile(r"^#{2,3}\s+Required Skill Invocations\s*$", re.MULTILINE)
FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
BACKTICKED = re.compile(r"`([a-z0-9][a-z0-9-]*)`")
# Only an explicit "Invoke `x`" counts as an invocation. The documents also
# name sibling skills to hand work over or to cite evidence, and those are
# references, not invocations - matching them would cry wolf.
INVOCATION = re.compile(r"[Ii]nvoke\s+(?:the\s+)?`([a-z0-9][a-z0-9-]*)`")


TEST_FILE_TOKEN = re.compile(r"[A-Za-z0-9_<>.-]*[Tt]est[A-Za-z0-9_<>.-]*\.(?:cc|cpp|cxx)\b")
# `BACKTICKED` matches skill names, which are lower-case and hyphenated. A
# file-name glob also needs underscores, dots, slashes and the star itself.
BACKTICKED_GLOB = re.compile(r"`([A-Za-z0-9_*./<>-]+)`")
# A placeholder such as <Component> is part of a documented example, so the
# glob has to accept the angle brackets as ordinary name characters.
GLOB_SEGMENT = r"[A-Za-z0-9_<>-]+"


def _declared_test_file_globs() -> dict[str, Path]:
    """Test-file name globs, each declared by the skill that owns the level.

    Ownership stays with the testing skills: `c-unit-testing` decides how a
    unit test file is named, `c-integration-testing` how an integration test
    file is named. This test only enforces the union across all documents.
    """
    globs = {}
    for skill in sorted(SKILLS_ROOT.glob("*/SKILL.md")):
        text = _read(skill)
        if "test-file-naming:begin" not in text:
            continue
        block = _anchored_block(text, "test-file-naming", skill)
        for name in BACKTICKED_GLOB.findall(block):
            if "*" in name and name.endswith((".cc", ".cpp", ".cxx")):
                globs[name] = skill
    return globs


def _glob_to_regex(glob: str) -> re.Pattern[str]:
    parts = [re.escape(part) for part in glob.split("*")]
    return re.compile(GLOB_SEGMENT.join(parts) + r"\Z")


def _sibling_skills() -> set[str]:
    return {skill.parent.name for skill in SKILLS_ROOT.glob("*/SKILL.md")}


def _section(text: str, heading: re.Pattern[str]) -> str:
    match = heading.search(text)
    if match is None:
        return ""
    rest = text[match.end() :]
    end = re.search(r"^#{1,3}\s", rest, re.MULTILINE)
    return rest[: end.start()] if end else rest


def _required_skills(text: str) -> set[str]:
    """Sibling skills listed in the Required Skill Invocations table."""
    section = _section(text, REQUIRED_SKILLS_HEADING)
    return {name for name in BACKTICKED.findall(section) if name in _sibling_skills()}


def _body_without_table(text: str) -> str:
    """The skill body, minus the frontmatter and the required-skills table.

    The frontmatter's `compatibility` line lists every dependency, so leaving
    it in would let a skill satisfy the check by being declared a dependency
    while no step ever uses it — exactly finding F11.
    """
    body = FRONTMATTER.sub("", text)
    table = _section(text, REQUIRED_SKILLS_HEADING)
    return body.replace(table, "") if table else body


def _checkbox_lines(section: str) -> list[str]:
    """The `- [ ]` items of a section, without its prose.

    A never-skippable row must be an actual checkbox. Searching the whole
    section would let a passing mention in an explanatory sentence satisfy the
    check while the checkbox itself is gone — a real miss, found by the
    negative control for this test.
    """
    return [line.strip() for line in section.splitlines() if line.strip().startswith("- [")]


def _reference_files() -> list[Path]:
    return sorted(
        reference
        for skill in CONSUMING_SKILLS
        for reference in (skill.parent / "references").glob("*.md")
    )


CONSUMING_SKILLS = _consuming_skills()


REFERENCE_FILES = _reference_files()


def _base_dod_block() -> str:
    """Resolved per test, not at import time.

    A missing anchor must fail one test, not abort collection of the whole
    file and hide every other check.
    """
    return _anchored_block(_read(WORKFLOW_ENGINE), "base-dod", WORKFLOW_ENGINE)


def _base_dod_ids() -> list[str]:
    return _table_step_ids(_base_dod_block())


def _never_skippable_steps() -> list[str]:
    """Step numbers whose own engine section heading says NEVER SKIPPABLE."""
    return [
        found.group(1)
        for line in _read(WORKFLOW_ENGINE).splitlines()
        if line.startswith("#") and "NEVER SKIP" in line.upper()
        for found in [re.search(r"Step (\d+\.\d+)", line)]
        if found
    ]


def _never_skip_ids() -> list[str]:
    """Base rows the shared engine itself marks as never skippable.

    Derived, not hardcoded: the engine stays the single place that decides
    which rows may never be dropped.
    """
    ids = []
    for line in _base_dod_block().splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        found = STEP_ID.match(cells[0])
        if found and "NEVER SKIP" in cells[1].upper():
            ids.append(found.group(1))
    return ids


class TestBaseDefinitionOfDone:
    """Every roadmap skill must carry all base DoD rows of the shared engine.

    Divergent DoD lists were finding F2/F6/F9 of the 2026-08-12 review round.
    A red pipeline settles that instead of a discussion.
    """

    def test_the_base_is_not_empty(self) -> None:
        assert _base_dod_ids(), f"{WORKFLOW_ENGINE}: base DoD block has no step rows"

    def test_every_base_row_has_a_parseable_step_id(self) -> None:
        """A malformed id must fail loudly, not drop the row from enforcement.

        Without this, a typo in the first column silently shrinks the base and
        every consuming skill keeps passing. Found by the negative control for
        this test.
        """
        unparseable = []
        for line in _base_dod_block().splitlines():
            row = line.strip()
            if not row.startswith("|"):
                continue
            first = row.strip("|").split("|")[0].strip()
            if not first or first == "Step" or set(first) <= set("-: "):
                continue  # header or separator
            if not STEP_ID.fullmatch(first):
                unparseable.append(first)
        assert not unparseable, (
            f"{WORKFLOW_ENGINE}: base DoD rows with an unusable step id: {unparseable}. "
            f"Expected <major>.<minor> with an optional single letter, e.g. 2.8a."
        )

    def test_base_step_ids_are_unique(self) -> None:
        """A duplicated id cannot be joined against a consuming skill."""
        ids = _base_dod_ids()
        duplicates = {i for i in ids if ids.count(i) > 1}
        assert not duplicates, f"{WORKFLOW_ENGINE}: base DoD ids appear twice: {sorted(duplicates)}"

    def test_every_base_step_has_a_section_in_the_engine(self) -> None:
        """A DoD row nobody executes is finding F11 in another shape."""
        engine = _read(WORKFLOW_ENGINE)
        missing = [i for i in _base_dod_ids() if f"Step {i.rstrip('ab')}" not in engine]
        assert not missing, f"{WORKFLOW_ENGINE}: base DoD rows without a step section: {missing}"

    @pytest.mark.parametrize("skill", CONSUMING_SKILLS, ids=_skill_id)
    def test_consuming_skill_covers_every_base_row(self, skill: Path) -> None:
        own = _box_step_ids(_anchored_block(_read(skill), "step-dod", skill))
        missing = [i for i in _base_dod_ids() if i not in own]
        assert not missing, (
            f"{_skill_id(skill)}: DoD is missing base rows {missing}. "
            f"The shared engine defines them, so every consuming skill must present them."
        )

    def test_at_least_one_base_row_is_marked_never_skippable(self) -> None:
        assert _never_skip_ids(), (
            f"{WORKFLOW_ENGINE}: no base DoD row is marked NEVER SKIP, "
            f"so the template exception check below has nothing to enforce"
        )

    def test_a_never_skippable_step_marks_all_of_its_base_rows(self) -> None:
        """Cross-check against the engine's own step headings.

        Deriving "never skippable" from the DoD table alone lets someone drop a
        marker and silently switch the enforcement off. The engine states the
        same fact twice — in the step heading and in the table — so the two must
        agree. Found by the negative control for this test.
        """
        marked = _never_skip_ids()
        for step in _never_skippable_steps():
            rows = [i for i in _base_dod_ids() if i.startswith(step)]
            assert rows, f"{WORKFLOW_ENGINE}: Step {step} is NEVER SKIPPABLE but has no base DoD row"
            unmarked = [i for i in rows if i not in marked]
            assert not unmarked, (
                f"{WORKFLOW_ENGINE}: the section for Step {step} says NEVER SKIPPABLE, but the "
                f"base DoD rows {unmarked} are not marked NEVER SKIP. The document contradicts "
                f"itself, and the template exception check stops enforcing those rows."
            )


ALL_SKILL_DOCS = sorted(SKILLS_ROOT.rglob("*.md"))

MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# "See the `c-unit-testing` skill section "Choosing the Test Level"" and the
# "`skill` → *Section*" form used in the reference tables.
SECTION_REFERENCES = (
    re.compile(r'`([a-z0-9-]+)`\s+skill\s+section\s+"([^"]+)"'),
    re.compile(r'`([a-z0-9-]+)`\s*(?:skill\s*)?(?:—|->|→)\s*\*([^*\n]+)\*'),
)


def _prose(text: str) -> str:
    """The document without its fenced code blocks.

    A C++ lambda such as `[&](uint8_t val)` is indistinguishable from a
    markdown link, and there are three of them in the integration patterns
    reference. Scanning code as prose reports them as broken links.
    """
    out, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def _has_heading(text: str, title: str) -> bool:
    return re.search(rf"^#{{1,4}}\s+.*{re.escape(title.strip())}", text, re.MULTILINE) is not None


def _doc_id(path: Path) -> str:
    return str(path.relative_to(SKILLS_ROOT)).replace("\\", "/")


ALL_SKILLS = sorted(SKILLS_ROOT.glob("*/SKILL.md"))

# Fields the documents actually use. The authority is the Agent Skills
# specification; extend this list when the spec grows a field rather than
# dropping the check, because a typo such as `descripton:` disables triggering
# silently.
KNOWN_FRONTMATTER_KEYS = {"name", "description", "compatibility"}
# The specification's hard ceiling for a description. `writing-skills` also
# suggests staying under 500 characters "if possible" — a guideline, and
# deliberately not enforced here. The defect it points at is a description that
# summarises the workflow, and no character count detects that. The suspicion
# that such a description also over-triggers was measured with
# `scripts/trigger_eval.py` and is wrong: the long descriptions held every
# positive and every negative case, while the review cluster failed the other
# way round, with too little reach. Whether the agent then follows the
# description instead of reading the body is a different question, and a
# trigger eval cannot see it.
DESCRIPTION_LIMIT = 1024

DOCUMENTED_PATH = re.compile(r"`([A-Za-z0-9_./<>-]*/[A-Za-z0-9_./<>-]*)`")
DOCUMENT_DETECTION_HEADING = re.compile(r"^#{2,3}\s+Document Detection\s*$", re.MULTILINE)
METRIC_FIELD = re.compile(r"\b([a-z_]+_metrics)\.([a-z_]+)\b")


def _frontmatter_groups(text: str) -> dict[str, set[str]]:
    """Top-level frontmatter keys mapped to their indented child keys.

    Checking only that a field name occurs somewhere in the frontmatter was the
    first attempt, and its negative control walked through: the same name also
    sits under `baseline_metrics` and `current_metrics`, so removing it from
    `target_metrics` stayed invisible. The group has to be part of the lookup.
    """
    groups: dict[str, set[str]] = {}
    current = None
    for line in _frontmatter(text).splitlines():
        top = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*$", line)
        if top:
            current = top.group(1)
            groups.setdefault(current, set())
            continue
        if re.match(r"^[A-Za-z_]", line):  # a top-level key that carries a value
            current = None
            continue
        child = re.match(r"^\s+([A-Za-z_][A-Za-z0-9_-]*):", line)
        if child and current:
            groups[current].add(child.group(1))
    return groups


def _detection_globs(skill: Path) -> set[str]:
    """The globs a roadmap skill hands to the shared engine's state machine."""
    text = _read(skill)
    if "document-detection:begin" not in text:
        return set()
    block = _anchored_block(text, "document-detection", skill)
    return {glob for glob in BACKTICKED_GLOB.findall(block) if "*" in glob and "/" in glob}


def _frontmatter(text: str) -> str:
    match = FRONTMATTER.match(text)
    return match.group(0) if match else ""


def _frontmatter_field(text: str, key: str) -> str | None:
    found = re.search(rf"^{key}:\s*(.*)$", _frontmatter(text), re.MULTILINE)
    return found.group(1).strip() if found else None


class TestFrontmatter:
    """Only the constraints that break something when violated.

    A description over the specification's limit, a name that does not match
    the directory, or a misspelled key all stop the skill from being found or
    loaded. Style guidance is deliberately not enforced.
    """

    @pytest.mark.parametrize("skill", ALL_SKILLS, ids=_skill_id)
    def test_required_fields_are_present(self, skill: Path) -> None:
        text = _read(skill)
        missing = [key for key in ("name", "description") if _frontmatter_field(text, key) is None]
        assert not missing, f"{_skill_id(skill)}: frontmatter is missing {missing}"

    @pytest.mark.parametrize("skill", ALL_SKILLS, ids=_skill_id)
    def test_name_matches_the_directory(self, skill: Path) -> None:
        name = _frontmatter_field(_read(skill), "name")
        assert name == _skill_id(skill), (
            f"{_skill_id(skill)}: frontmatter name is {name!r}. It must equal the directory name, "
            f"which is how the skill is invoked."
        )

    @pytest.mark.parametrize("skill", ALL_SKILLS, ids=_skill_id)
    def test_description_is_within_the_specification_limit(self, skill: Path) -> None:
        description = _frontmatter_field(_read(skill), "description") or ""
        assert len(description) <= DESCRIPTION_LIMIT, (
            f"{_skill_id(skill)}: description is {len(description)} characters, "
            f"over the specification limit of {DESCRIPTION_LIMIT}"
        )

    @pytest.mark.parametrize("skill", ALL_SKILLS, ids=_skill_id)
    def test_no_unknown_frontmatter_key(self, skill: Path) -> None:
        keys = set(re.findall(r"^([A-Za-z_][A-Za-z0-9_-]*):", _frontmatter(_read(skill)), re.MULTILINE))
        unknown = sorted(keys - KNOWN_FRONTMATTER_KEYS)
        assert not unknown, (
            f"{_skill_id(skill)}: unknown frontmatter keys {unknown}. A misspelled key is ignored "
            f"silently — fix the spelling, or add the field here if the specification gained it."
        )


class TestDocumentedPaths:
    """One spelling per placeholder in the file paths of one skill.

    A path placeholder decides the name of a file the workflow writes. When the
    skill says `doc/test-coverage/<component>_…` for the roadmap and
    `<Component>_…` for the retrospective, two sessions produce differently
    named files and the document detection of the state machine no longer finds
    the roadmap — it starts over. That is the part of finding F15 that breaks
    something.

    The rule is consistency, not a fixed case. Enforcing lower case was tried
    first and was wrong: `<YYYYMMDD>` is a date format token, `<N>` an index,
    and `<VARIANT>`/`<COMPONENT>` are build variables whose upper case says
    "substitute a value here". All of those are already spelled consistently.
    A file name built from a C identifier keeps its own casing too, because
    `test_<Component>_<Function>.cc` follows the language convention — those
    segments are recognised from the declared test-file globs and skipped.
    """

    @pytest.mark.parametrize("skill", ALL_SKILLS, ids=_skill_id)
    def test_a_path_placeholder_has_one_spelling_per_skill(self, skill: Path) -> None:
        test_file_patterns = [_glob_to_regex(glob) for glob in _declared_test_file_globs()]
        spellings: dict[str, set[str]] = {}
        for doc in sorted(skill.parent.rglob("*.md")):
            for path in DOCUMENTED_PATH.findall(_prose(_read(doc))):
                for segment in path.split("/"):
                    if any(regex.match(segment) for regex in test_file_patterns):
                        continue
                    for placeholder in re.findall(r"<([A-Za-z][A-Za-z0-9_]*)>", segment):
                        spellings.setdefault(placeholder.lower(), set()).add(placeholder)
        clashes = {word: sorted(seen) for word, seen in spellings.items() if len(seen) > 1}
        assert not clashes, (
            f"{_skill_id(skill)}: the same path placeholder is spelled several ways: {clashes}. "
            f"Two sessions then write differently named files, and the document detection fails "
            f"to find them."
        )


FIRST_CONTACT_HEADING = re.compile(r"^#{2,3}\s+First Contact\s*$", re.MULTILINE)
NUMBERED_ITEM = re.compile(r"^(\d+)\.\s+(.*)$", re.MULTILINE)


# Names that only exist inside one host. Two of them are recognised by shape —
# an MCP server prefix and an IDE tool prefix — because those are host-specific
# by construction and a list would always lag behind.
HOST_TOOL_SHAPES = (re.compile(r"^ide-[a-z_]+$"), re.compile(r"^mcp__"))
HOST_TOOL_NAMES = {
    "AskUserQuestion",
    "NotebookEdit",
    "TodoWrite",
    "SlashCommand",
    "BashOutput",
    "KillShell",
    "str_replace_editor",
}


BUILD_INVOCATION = re.compile(r"^.*[Ii]nvoke `build-execution`.*$", re.MULTILINE)


class TestCoverageBuildParameters:
    """A build that is meant to produce coverage must say so.

    `coverage.json` exists only in a Debug build. A build invocation that does
    not name the build type therefore leaves the coverage step with nothing to
    read, and the failure surfaces far away from its cause — the agent reports
    a missing file, not a wrong build. Only skills that read `coverage.json`
    are held to this; the modernization build measures a `.map` file and has no
    business being forced into Debug.
    """

    @pytest.mark.parametrize("doc", ALL_SKILL_DOCS, ids=_doc_id)
    def test_a_coverage_build_names_the_debug_build_type(self, doc: Path) -> None:
        text = _read(doc)
        if "coverage.json" not in text:
            return
        offenders = [
            line.strip()
            for line in BUILD_INVOCATION.findall(text)
            if "buildType=Debug" not in line
        ]
        assert not offenders, (
            f"{_doc_id(doc)}: this document reads coverage.json, but invokes the build without "
            f"buildType=Debug: {offenders}. No Debug build, no coverage.json."
        )


class TestHarnessNeutrality:
    """No skill names a tool that only one host has.

    `AGENTS.md` states these skills work across Copilot CLI, VS Code Copilot
    and Claude Code. A tool name from one of them is an instruction the other
    two cannot follow. The generic placeholders — `ask_user` for asking the
    human, "the IDE diagnostics" for reading analyser findings — are the
    portable form, and they are what finding F16 mistook for a defect.
    """

    @pytest.mark.parametrize("doc", ALL_SKILL_DOCS, ids=_doc_id)
    def test_no_host_specific_tool_name(self, doc: Path) -> None:
        offenders = sorted(
            {
                name
                for name in BACKTICKED_GLOB.findall(_read(doc))
                if name in HOST_TOOL_NAMES or any(shape.match(name) for shape in HOST_TOOL_SHAPES)
            }
        )
        assert not offenders, (
            f"{_doc_id(doc)}: names host-specific tools {offenders}. These skills run under "
            f"several agents, so describe the capability instead — `ask_user` to ask the human, "
            f"'the IDE diagnostics' to read analyser findings."
        )


class TestFirstContact:
    """Look for the documents before asking what they already answer.

    Both skills opened by agreeing something that belongs in a roadmap — the
    coverage target, the stakeholders — and only then ran the document
    detection. On a resume that re-negotiates an agreement the existing roadmap
    already records, and the fresh answer overwrites it. Finding F8.
    """

    @pytest.mark.parametrize("skill", CONSUMING_SKILLS, ids=_skill_id)
    def test_document_detection_is_one_of_the_first_two_steps(self, skill: Path) -> None:
        section = _section(_read(skill), FIRST_CONTACT_HEADING)
        items = NUMBERED_ITEM.findall(section)
        assert items, f"{_skill_id(skill)}: First Contact has no numbered steps"
        detecting = [int(n) for n, body in items if "document detection" in body.lower()]
        assert detecting, (
            f"{_skill_id(skill)}: no First Contact step runs the document detection. Everything "
            f"asked before it risks overwriting what an existing roadmap already agreed."
        )
        assert min(detecting) <= 2, (
            f"{_skill_id(skill)}: document detection is step {min(detecting)} of First Contact. "
            f"It has to come first, right after the component is known — the questions that "
            f"follow depend on whether a roadmap already exists."
        )


class TestRoadmapFrontmatterFields:
    """A field the skill reads must exist in the roadmap template it reads it from.

    The skill names fields such as `target_metrics.test_coverage_percent` in
    prose, and the template defines them. Renaming one without the other leaves
    the skill looking for a key no roadmap carries, and the failure is silent:
    the value simply reads as absent.
    """

    @pytest.mark.parametrize("skill", CONSUMING_SKILLS, ids=_skill_id)
    def test_referenced_metric_fields_exist_in_the_template(self, skill: Path) -> None:
        template = skill.parent / "references" / "roadmap_template.md"
        if not template.exists():
            pytest.skip("skill has no roadmap template")
        defined = _frontmatter_groups(_read(template))
        missing = sorted(
            {
                f"{group}.{field}"
                for group, field in METRIC_FIELD.findall(_read(skill))
                if field not in defined.get(group, set())
            }
        )
        assert not missing, (
            f"{_skill_id(skill)}: reads {missing}, which the roadmap template does not define. "
            f"The skill would find no value and fail silently."
        )


class TestDocumentDetection:
    """The globs the state machine detects with, and the paths that must match them.

    The shared engine delegates document detection to the consuming skill and
    expects concrete globs — finding F7 was that neither skill supplied any. A
    roadmap the detection does not find is a roadmap that gets created a second
    time, and the progress in the first one is lost. Measuring it also showed
    `modernization-roadmap` naming its review file `_comprehensive_review_` in
    the skill and `_review_` in the template.
    """

    @pytest.mark.parametrize("skill", CONSUMING_SKILLS, ids=_skill_id)
    def test_the_skill_declares_its_detection_globs(self, skill: Path) -> None:
        globs = _detection_globs(skill)
        assert globs, (
            f"{_skill_id(skill)}: no document-detection globs. The shared engine states that the "
            f"consuming skill defines them, so without a block here the state machine has nothing "
            f"to run."
        )

    @pytest.mark.parametrize("skill", CONSUMING_SKILLS, ids=_skill_id)
    def test_the_skill_says_which_file_wins_when_several_match(self, skill: Path) -> None:
        """Checks the rows exist, not that their prose is sensible.

        Searching the whole section for the word "newest" was the first
        attempt and its negative control walked straight through: the word
        appears twice, so deleting the rule left the other mention behind. The
        rules are rows inside the anchored block now, and deleting one fails.
        Rewriting a row's text into nonsense still passes — prose cannot be
        checked, and pretending otherwise would be worse than saying so.
        """
        rows = {
            line.strip().strip("|").split("|")[0].strip().lower()
            for line in _anchored_block(_read(skill), "document-detection", skill).splitlines()
            if line.strip().startswith("|")
        }
        missing = [rule for rule in ("several files match", "newest unclear") if rule not in rows]
        assert not missing, (
            f"{_skill_id(skill)}: the document-detection block has no rule for {missing}. "
            f"Picking arbitrarily among several matches resumes the wrong roadmap."
        )

    @pytest.mark.parametrize("skill", CONSUMING_SKILLS, ids=_skill_id)
    def test_every_documented_path_matches_a_declared_glob(self, skill: Path) -> None:
        globs = _detection_globs(skill)
        offenders = set()
        for doc in sorted(skill.parent.rglob("*.md")):
            for path in DOCUMENTED_PATH.findall(_prose(_read(doc))):
                # Only paths the detection could ever return: same directory,
                # same depth. A retrospective one level deeper is not a
                # candidate and must not be judged against a roadmap glob.
                peers = [
                    glob
                    for glob in globs
                    if glob.rsplit("/", 1)[0] == path.rsplit("/", 1)[0]
                    and glob.count("/") == path.count("/")
                ]
                if peers and not any(_glob_to_regex(glob).match(path) for glob in peers):
                    offenders.add(f"{path} (expected one of {sorted(peers)})")
        assert not offenders, (
            f"{_skill_id(skill)}: documented paths that the document detection would never "
            f"find: {sorted(offenders)}"
        )


class TestCrossDocumentReferences:
    """Guards a coupling that spans documents, so it prevents rather than finds.

    Both checks pass today. Their value is that renaming a section in one
    skill, or moving a reference file, silently breaks a pointer in another
    skill — and no review round catches that reliably.
    """

    @pytest.mark.parametrize("doc", ALL_SKILL_DOCS, ids=_doc_id)
    def test_every_relative_link_resolves(self, doc: Path) -> None:
        dangling = []
        for target in MARKDOWN_LINK.findall(_prose(_read(doc))):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            path = target.split("#")[0]
            if path and not (doc.parent / path).exists():
                dangling.append(target)
        assert not dangling, f"{_doc_id(doc)}: links point at nothing: {sorted(set(dangling))}"

    @pytest.mark.parametrize("doc", ALL_SKILL_DOCS, ids=_doc_id)
    def test_every_referenced_section_of_another_skill_exists(self, doc: Path) -> None:
        problems = []
        prose = _prose(_read(doc))
        for pattern in SECTION_REFERENCES:
            for skill_name, title in pattern.findall(prose):
                if skill_name not in _sibling_skills() or skill_name == _skill_id(doc):
                    continue
                target = SKILLS_ROOT / skill_name / "SKILL.md"
                if not _has_heading(_read(target), title):
                    problems.append(f"{skill_name} has no section {title.strip()!r}")
        assert not problems, (
            f"{_doc_id(doc)}: {sorted(set(problems))}. Either the section was renamed or the "
            f"pointer is wrong — both leave the reader at a heading that does not exist."
        )


class TestTestFileNaming:
    """Every test file name in the documents must follow a declared convention.

    The coverage-roadmap templates prescribed `<Component>_<Function>_test.cpp`
    while `c-unit-testing` mandates `test_*.cc`, so following the template
    produced wrongly named tests — finding F4. Measuring it also showed
    `c-integration-testing` using both styles at once.
    """

    def test_a_convention_is_declared_somewhere(self) -> None:
        globs = _declared_test_file_globs()
        assert globs, (
            f"no skill declares a test-file naming convention. Expected an "
            f"<!-- test-file-naming:begin/end --> block in the skill that owns the test level."
        )

    @pytest.mark.parametrize("doc", ALL_SKILL_DOCS, ids=_doc_id)
    def test_every_test_file_name_matches_a_declared_glob(self, doc: Path) -> None:
        declared = _declared_test_file_globs()
        # Inside the documents of the skill that owns a test level, only that
        # level's glob is allowed. Elsewhere any declared glob will do. Without
        # this narrowing the unit glob `test_*.cc` swallows an integration test
        # that lost its `_integration` suffix, because it is a superset — found
        # by the negative control for this test.
        owner = _skill_id(doc) if doc.name == "SKILL.md" else doc.parent.parent.name
        own = {glob for glob, skill in declared.items() if skill.parent.name == owner}
        allowed = own or set(declared)
        patterns = {glob: _glob_to_regex(glob) for glob in allowed}
        offenders = sorted(
            {
                token
                for token in TEST_FILE_TOKEN.findall(_read(doc))
                if not any(regex.match(token) for regex in patterns.values())
            }
        )
        assert not offenders, (
            f"{_doc_id(doc)}: test file names {offenders} match none of the conventions that "
            f"apply here, {sorted(patterns)}. Following such an example produces a wrongly "
            f"named test."
        )


class TestRequiredSkillInvocations:
    """The table and the workflow steps must agree, in both directions.

    A skill listed as mandatory that no step ever uses is a rule nobody can
    follow (finding F11). A skill a step invokes but that the table omits makes
    the table useless as a dependency list (finding F12).
    """

    @pytest.mark.parametrize("skill", CONSUMING_SKILLS, ids=_skill_id)
    def test_every_listed_skill_is_used_by_a_step(self, skill: Path) -> None:
        body = _body_without_table(_read(skill))
        engine = _read(WORKFLOW_ENGINE)
        unused = [
            name for name in sorted(_required_skills(_read(skill)))
            if name not in body and name not in engine
        ]
        assert not unused, (
            f"{_skill_id(skill)}: the Required Skill Invocations table lists {unused}, but no "
            f"step in the skill or in the shared engine uses them. Either wire them into a step "
            f"or drop the row — a mandatory skill nobody invokes cannot be followed."
        )

    @pytest.mark.parametrize("skill", CONSUMING_SKILLS, ids=_skill_id)
    def test_every_invoked_skill_is_listed(self, skill: Path) -> None:
        text = _read(skill)
        listed = _required_skills(text)
        invoked = {
            name
            for name in INVOCATION.findall(_body_without_table(text))
            if name in _sibling_skills() and name != _skill_id(skill)
        }
        missing = sorted(invoked - listed)
        assert not missing, (
            f"{_skill_id(skill)}: steps invoke {missing}, but the Required Skill Invocations "
            f"table does not list them. The table is the dependency list — an invocation that "
            f"is missing from it is invisible to anyone reading the table."
        )


class TestTemplateDefinitionOfDone:
    """A template must not carry a DoD list of its own.

    Three divergent DoD lists — the skill's box plus one per template — were
    finding F2, and the templates were the copies that had lost the mandatory
    rows. A template therefore either delegates to the skill's box, or declares
    an exception that still names the never-skippable rows (finding F3).
    """

    @pytest.mark.parametrize("reference", REFERENCE_FILES, ids=_reference_id)
    def test_every_dod_section_delegates_or_declares_an_exception(self, reference: Path) -> None:
        for number, section in enumerate(_dod_sections(reference), start=1):
            delegated = "<!-- dod:delegated -->" in section
            exception = "<!-- dod:exception -->" in section
            assert delegated or exception, (
                f"{_reference_id(reference)}: 'Definition of Done' section {number} restates the "
                f"DoD. Add <!-- dod:delegated --> and point at the skill's DoD box, or "
                f"<!-- dod:exception --> and say why this step deviates."
            )
            assert not (delegated and exception), (
                f"{_reference_id(reference)}: 'Definition of Done' section {number} is marked both "
                f"delegated and exception — it can only be one."
            )

    @pytest.mark.parametrize("reference", REFERENCE_FILES, ids=_reference_id)
    def test_an_exception_still_names_the_never_skippable_rows(self, reference: Path) -> None:
        never_skip = _never_skip_ids()
        for number, section in enumerate(_dod_sections(reference), start=1):
            if "<!-- dod:exception -->" not in section:
                continue
            checkboxes = "\n".join(_checkbox_lines(section))
            missing = [step for step in never_skip if step not in checkboxes]
            assert not missing, (
                f"{_reference_id(reference)}: DoD exception in section {number} has no checkbox "
                f"for the never-skippable rows {missing}. An exception may narrow the DoD, never "
                f"remove a row the engine marks NEVER SKIP — and a mention in prose is not a row."
            )
