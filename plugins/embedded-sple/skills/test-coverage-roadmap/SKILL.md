---
name: test-coverage-roadmap
description: Use this skill when improving unit test coverage for C components toward a 90%+ target. Guides systematic, incremental test additions with one function per step, human approval checkpoints, and file-based progress tracking. Starts with a comprehensive review to identify coverage gaps, then creates a prioritized roadmap. Trigger whenever the user wants to increase test coverage, write missing unit tests, create a test plan for untested code, reach a coverage target, or resume an existing coverage roadmap — even casual requests like "we need more tests for this module".
compatibility: "Requires PowerShell 5.1+. Depends on sibling skills - build-execution, c-unit-testing, c-integration-testing, c-code-review-comprehensive, retrospective, conventional-commits, project-knowledge-base."
---

# Test Coverage Roadmap

This skill guides systematic unit test coverage improvement for C components using an incremental approach with human stakeholder involvement at every step.

> **Philosophy**: Small, focused test additions in incremental steps, until the agreed coverage target is reached.

## Workflow Engine

This skill uses the shared incremental roadmap framework.  
**READ FILE**: [Roadmap Workflow Engine](../shared/roadmap-common/roadmap-workflow-engine.md) — for the document state machine, step execution cycle, human checkpoint patterns, and commit workflow.

All common workflow rules (forbidden behaviors, retrospective requirements) from the shared engine apply here. The sections below define **coverage-specific** behavior.

---

## First Contact

When the user first invokes this skill:

1. **Confirm component path** — ask which component to improve coverage for if not clear from the request
2. **Run the document detection** — the globs in *Document Detection* below, before asking anything else. What is worth asking depends on whether a roadmap already exists, so a question asked first can overwrite an agreement that was already made
3. **A roadmap exists** — report where it stands: current step of total, current line coverage against the **agreed** target from its frontmatter, and the date of the file you picked. Resume there. Do **not** re-negotiate the target — the value in the roadmap is the agreement. Change it only if the user asks, and then say what it was before
4. **No roadmap exists** — explain the three phases (analysis → iterative test addition → completion) and that every step requires human approval; agree the target, proposing the default from the Domain-Specific Bindings table, and record it in the roadmap frontmatter (`target_metrics.line_coverage_percent`); set expectations — incremental work across multiple sessions, one function per step, not a one-shot "write all tests"

Then proceed to Phase 1.

---

## Domain-Specific Bindings

| Parameter | Value |
|-----------|-------|
| Review file path | `doc/reviews/<component>_comprehensive_review_<YYYYMMDD>.md` |
| Roadmap file path | `doc/test-coverage/<component>_coverage_roadmap_<YYYYMMDD>.md` |
| Lessons learned file | `doc/project_notes/test_coverage_lessons_learned.md` |
| Retrospective path | `doc/test-coverage/retrospectives/<component>_Step_<N>_retrospective.md` |
| Roadmap template | `references/roadmap_template.md` |
| Step template | `references/step_template.md` |
| Lessons learned template | `../shared/roadmap-common/lessons_learned_template.md` |
| Coverage target | `target_metrics.line_coverage_percent` in the roadmap frontmatter (default 90%, confirmed in First Contact) |
| Gate metric | Line coverage. Function and branch coverage are measured and reported; branch coverage must not regress. |
| NOT_TESTABLE register | `## Untestable Code` section of the roadmap, plus `not_testable_lines` in its frontmatter |

### Document Detection

The shared engine's State Matrix runs these globs; it does not define them. Run them **before
anything else**. A roadmap the detection misses is a roadmap that gets written a second time, and
the progress recorded in the first one is lost.

<!-- document-detection:begin -->

| Document | Glob |
|----------|------|
| Comprehensive review | `doc/reviews/<component>_comprehensive_review_*.md` |
| Coverage roadmap | `doc/test-coverage/<component>_coverage_roadmap_*.md` |

| Situation | Rule |
|-----------|------|
| Several files match | Take the one with the newest date in its file name and say which one you took. Never merge two roadmaps, and never start a third. |
| Newest unclear | Two files carry the same date, or one carries none: stop and ask which to resume. Guessing here discards somebody's work. |

<!-- document-detection:end -->

---

## Additional Forbidden Behaviors (Coverage-Specific)

These extend the common forbidden behaviors from the shared workflow engine.

| Forbidden Action | Why It's Forbidden |
|------------------|--------------------|
| Testing multiple functions in one step | Each step must test exactly ONE function for focused review |
| Planning or writing test scenarios before the spec is read (Step 2.1b) | Test cases must be derived from requirements, not only from code paths |
| Writing tests at a test level the human did not approve | The level decides mocking, test file location and scenario shape — it belongs in the plan (Step 2.2), not in the writing step |
| Skipping coverage measurement (Step 2.6) | Coverage must come from the actual `coverage.json`, not estimates |
| Presenting approval checkpoint without coverage output | Human needs real metrics to approve |
| Guessing coverage values | Must extract from `coverage.json` — HTML scraping is unreliable |
| Modifying production source files without approval | Testability refactoring requires explicit `ask_user` approval and separate commit |
| Skipping lessons learned update | Each step needs at least one learning added |
| Declaring "roadmap complete" below the agreed target with an unexplained gap | The gate is line coverage vs. the agreed target; a shortfall is only acceptable where the NOT_TESTABLE register explains it |
| Writing a test whose only purpose is to reach a line in the NOT_TESTABLE register | An alibi test carries maintenance cost and catches no defect |
| Adding a NOT_TESTABLE entry without human approval, or without the required evidence | Every entry lowers the bar, so it may only grow by an approved and evidenced decision |
| Stopping iterations after planned steps finish | Must iterate until the agreed target is reached or the gap is explained, adding new steps as needed |
| Using placeholder values in completed DoD | The template uses `____` as prompts, but the presented DoD must contain real values |

---

## Step Size Rule

> **MANDATORY**: Each step covers **exactly ONE function** for focused human review.

| Guideline | Value |
|-----------|-------|
| Functions per step | **1** (mandatory) |
| Test cases | Based on function complexity (cover all scenarios) |

**Step 0 Exception**: Infrastructure setup (CMakeLists.txt, mock generation) may be a separate step.
**Large functions**: May span multiple steps, but each step still targets ONE function (different paths/branches).

---

## Phase 1: Setup & Analysis

Follow the shared Phase 1 skeleton (check docs → comprehensive review → create roadmap).

### Create Coverage Roadmap (Step 1.3)

Focus on coverage improvement only:
- Identify all uncovered functions
- Identify uncovered branches/paths in covered functions
- **ONE FUNCTION PER STEP**
- Target: the agreed line coverage target

**Step ordering**: Start with easy wins (low complexity) to build momentum and catch integration issues early, then progress to higher complexity functions. Within the same complexity tier, prioritize by criticality (see Prioritization Guidelines below).

---

## Phase 2: Iterative Test Addition

Follow the shared step execution cycle. One step at a time — after completing one step (including both checkpoints and retrospective), **STOP** and wait for human to indicate readiness.

### Analyze Coverage Gaps (Step 2.1a)

Invoke `build-execution` with `buildKit=test, buildType=Debug` to build and run unit tests for the
component, then review the coverage report for gaps. **The build type is not optional**:
`coverage.json` is only generated in a Debug build, so any other build type leaves Step 2.6 with
nothing to extract.

Uncovered lines that **no test can reach** are not planned as work. Classify them instead — see
*Untestable Code* below — and carry the candidates into the plan (Step 2.2).

### Consult the Specification (Step 2.1b — before planning test scenarios)

> **MANDATORY — NEVER SKIP**: Derive test cases from the specification, not only from the code paths.

1. Read the relevant spec/requirement documents for the function under test (component
   `doc/index.md`, software/unit specification). Record the spec IDs you read. If no spec exists for
   this function, record that too — it is a finding.
2. Compare the spec against the current implementation: does the code do something the spec does not
   describe, or omit behaviour the spec requires?
3. If a discrepancy is found: record it and put both options into the plan (Step 2.2), with a
   recommendation and the reasoning — **A)** the test verifies the CURRENT IMPLEMENTATION (test
   passes, potential defect stays hidden), or **B)** the test verifies the SPECIFICATION (test
   FAILS, documents a potential defect).
4. Do **not** open a separate checkpoint for the A/B decision. The human decides it together with
   the plan approval in Step 2.3. This satisfies the "stop and ask" rule of `c-unit-testing`.

See the `c-unit-testing` skill section "Specification-First Test Design" for the full rule and conflict-handling template.

### Plan (Step 2.2)

Document: functions to test, the **test level** (unit / integration) with the reason for it, test
scenarios (Given/When/Then) derived from the spec read in Step 2.1b, expected coverage gain, and —
if Step 2.1b found a spec/implementation discrepancy — the A/B options with your recommendation.

See the `c-unit-testing` skill section "Choosing the Test Level" for the decision rule.

### Human Approval of Plan (Step 2.3 — BLOCKING CHECKPOINT)

Present plan via `ask_user` for explicit approval before writing any test code. The test level is
part of this approval. If the plan contains a spec/implementation discrepancy, the A/B decision is
part of it too. Record both decisions in the step documentation.

### Write Tests (Step 2.4)

Invoke the skill that matches the test level approved in Step 2.3:

- **Isolated component** (all dependencies mocked) → `c-unit-testing` skill
- **Multiple real components compiled together** → `c-integration-testing` skill

Changing the level while writing needs a new approval — go back to Step 2.2.

### Build & Test (Step 2.5)

Invoke `build-execution` with `buildKit=test, buildType=Debug` to build and run all tests. All must
pass before proceeding, and the Debug build is what produces the `coverage.json` that Step 2.6 reads.

### Measure Coverage (Step 2.6 — MANDATORY before Human Review)

Execute and show output BEFORE presenting the approval checkpoint:

**READ**: [Coverage Analysis](../shared/test-reports/coverage-analysis.md) — "Extracting Coverage from coverage.json" for the totals, and "Per File and Per Function" for the numbers the roadmap and step templates ask for per source file and per function under test.

Extract: line coverage %, function coverage %, branch coverage %, delta. **FORBIDDEN**: estimating coverage.

Then compare branch coverage against the previous step. **Branch coverage must not regress** — that
is a gate, not a remark, so state the before and after explicitly even when it is unchanged. A step
that raises line coverage while dropping branch coverage has replaced real cases with shallow ones,
and the DoD row for 2.6 is where that becomes visible. If it dropped, report it and propose a step
to recover it before asking for approval.

---

## Untestable Code (NOT_TESTABLE Register)

Lines no test can reach are not work. Record them in the roadmap's **NOT_TESTABLE register** and
they explain the remaining gap at completion, instead of forcing an alibi test or a broken rule.

| Rule | |
|------|--|
| Reasons | Exactly two: `DEFENSIVE_BY_DESIGN` (a checklist demands the branch) or `UNREACHABLE_DEFECT` (genuinely dead code). **Never a third** — if neither fits, the code is testable and belongs in a step |
| Evidence | Every entry names the checklist item, the UNR finding ID, or the MISRA rule. A claim without it is a guess, not an entry |
| Coverage figure | **Never adjusted.** The raw value from `coverage.json` stays the number; the register sits beside it as the explanation |
| Dead code | Recorded and handed to `modernization-roadmap`. This skill does not remove production code, so the entry parks a defect rather than resolving it — say so |
| Approval | With the plan in Step 2.3, no separate checkpoint. The whole register is confirmed once more in Phase 3 before `status: COMPLETED` |

**READ FILE**: [references/untestable-code.md](references/untestable-code.md) — when classifying a
line, writing an entry, or justifying the gap to a reviewer.

---

## Step Definition of Done (DoD) Checklist

> Present this completed DoD before asking about the next step. Every checkbox needs real evidence.

<!-- step-dod:begin -->

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                    STEP [N] DEFINITION OF DONE                               ║
║  Function: <function_name>  │  File: <source_file.c>                         ║
╠──────────────────────────────────┬──────┬────────────────────────────────────╣
║ 2.1 Lessons consulted            │ [ ]  │ Lessons applied: ____ / none yet   ║
║ 2.1a Analyze coverage gaps       │ [ ]  │ Uncovered lines + untestable found ║
║ 2.1b Spec consulted              │ [ ]  │ Spec IDs read + conflict A/B       ║
║ 2.2 Plan tests                   │ [ ]  │ Scenarios, level, NOT_TESTABLE     ║
║ 2.3 Human approved plan          │ [ ]  │ User said: ____ (incl. level, A/B) ║
║ 2.4 Tests written                │ [ ]  │ File: ____, Tests added: ____      ║
║ 2.5 Build & tests pass           │ [ ]  │ Exit code: ____ Passed: ____/____  ║
║ 2.6 Coverage from coverage.json  │ [ ]  │ Line/Branch/Func, branch not down  ║
║ 2.7 Human approved results       │ [ ]  │ User said: ________________        ║
║ 2.8a Retrospective written       │ [ ]  │ File: ____ (existence verified)    ║
║      (NEVER SKIP)                │      │                                    ║
║ 2.8b Lessons learned updated     │ [ ]  │ File: ____ (existence verified)    ║
║      (NEVER SKIP)                │      │                                    ║
║ 2.9a Roadmap updated             │ [ ]  │ Step marked: COMPLETED             ║
║ 2.9b Committed & pushed          │ [ ]  │ Commit: (git log --oneline -1)     ║
║ 2.10 Coverage vs Target          │ [ ]  │ current/target/gap/explained/next  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

<!-- step-dod:end -->

**Rules**: Every checkbox needs evidence (not placeholders). 2.8a and 2.8b are NEVER skippable. If any item cannot be completed, use `ask_user` for explicit skip approval and track in SKIPPED ITEMS section.

---

## Iteration Enforcement Rule

> After EVERY step completion, the agent MUST:
> 1. Extract line, function and branch coverage from `coverage.json`
> 2. Compare line coverage against the agreed target (roadmap frontmatter)
> 3. If line coverage < target: analyze the remaining uncovered code. Lines no test can reach go into
>    the NOT_TESTABLE register; everything else becomes additional steps. Present the gap split into
>    "testable" and "explained"
> 4. If all roadmap steps are done BUT line coverage < target: ADD NEW STEPS for the testable
>    remainder and continue. Stop only once that remainder is empty — every uncovered line is then
>    either tested or an approved register entry
> 5. If branch coverage dropped below the baseline: report it and propose a step to recover it
>
> **Definition of "Complete"**: line coverage ≥ agreed target, **or** the whole gap to the target
> explained by approved register entries. Never "all planned steps done".

---

## Phase 3: Completion

When line coverage ≥ the agreed target is confirmed from coverage.json — or the gap to the target is
fully explained by the NOT_TESTABLE register:

1. **Final verification** — Re-extract coverage using the shared [Coverage Analysis](../shared/test-reports/coverage-analysis.md) to independently confirm
2. **Confirm the register** — Present every NOT_TESTABLE entry with its reason and evidence for one final approval. An entry that cannot be evidenced now leaves the register, and its lines go back into the gap
3. **Final metrics** — Document in roadmap: baseline vs final coverage (line, branch, function), and how much of the gap the register explains
4. **Final lessons learned** — Add completion entry to lessons learned file
5. **Record the decisions that outlive this roadmap** — Invoke `project-knowledge-base` for anything a future maintainer needs but would never find in an archived roadmap: every `DEFENSIVE_BY_DESIGN` register entry, each testability refactoring of production code, and each spec-vs-implementation A/B decision. Skip this step when none of those occurred — say so rather than writing an empty entry
6. **Set roadmap status** — Update YAML frontmatter `status: COMPLETED`, `current_metrics` and `not_testable_lines`
7. **Commit** — Final commit using `conventional-commits` skill

---

## Prioritization Guidelines

When deciding which functions to include in the roadmap, consider these factors. Functions matching multiple criteria get higher priority:

1. **Critical paths** — Core business logic, safety-critical code
2. **High complexity** — Functions with high cyclomatic complexity (more branches = more risk)
3. **Frequently changed** — Code that changes often benefits most from tests
4. **Bug-prone** — Areas with history of defects

> **Note**: Step ordering (easy wins first) is separate from prioritization.
> High-priority functions are always included in the roadmap, but simple
> ones are scheduled earlier to build momentum. See Step 1.3 for ordering rules.

---

## Required Skill Invocations

| Phase        | Skill to Invoke                | Mandatory |
|--------------|--------------------------------|-----------|
| Analysis     | `c-code-review-comprehensive`  | YES |
| Build & Test | `build-execution`              | YES — always `buildKit=test, buildType=Debug` |
| Test Writing | `c-unit-testing`           | YES — isolated component tests |
| Test Writing | `c-integration-testing`    | YES — when tests compile multiple real components together |
| Each Step    | `retrospective`               | YES |
| Coverage     | Shared [coverage-analysis.md](../shared/test-reports/coverage-analysis.md) | YES — every step & final |
| Commit       | `conventional-commits`         | YES |
| Branching    | `conventional-commits`         | YES |
| Decisions    | `project-knowledge-base`       | When a decision outlives the roadmap — see Phase 3 |

## Templates

- [references/roadmap_template.md](references/roadmap_template.md) — Coverage roadmap document
- [references/step_template.md](references/step_template.md) — Individual step documentation
- [Lessons learned template](../shared/roadmap-common/lessons_learned_template.md) — Lessons learned format

## Usage Examples

```text
"Improve test coverage for components/auto_off/ to 90%"
"Create a coverage roadmap for diagnostics.c"
"Resume test coverage improvement for communication_handler"
"Add tests to reach 90% coverage for sensor_driver"
```
