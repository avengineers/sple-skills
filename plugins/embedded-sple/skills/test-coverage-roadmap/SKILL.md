---
name: test-coverage-roadmap
description: Use this skill when improving unit test coverage for C components toward a 90%+ target. Guides systematic, incremental test additions with one function per step, human approval checkpoints, and file-based progress tracking. Starts with a comprehensive review to identify coverage gaps, then creates a prioritized roadmap. Trigger whenever the user wants to increase test coverage, write missing unit tests, create a test plan for untested code, or reach a coverage target — even casual requests like "we need more tests for this module".
compatibility: "Requires PowerShell 5.1+. Depends on sibling skills - build-execution, c-unit-testing, c-code-review-comprehensive, retrospective, conventional-commits, project-knowledge-base."
---

# Test Coverage Roadmap

This skill guides systematic unit test coverage improvement for C components using an incremental approach with human stakeholder involvement at every step.

> **Philosophy**: Small, focused test additions in incremental steps. Target: 90%+ coverage.

## Workflow Engine

This skill uses the shared incremental roadmap framework.  
**READ FILE**: [Roadmap Workflow Engine](../shared/roadmap-common/roadmap-workflow-engine.md) — for the document state machine, step execution cycle, human checkpoint patterns, and commit workflow.

All common workflow rules (forbidden behaviors, retrospective requirements) from the shared engine apply here. The sections below define **coverage-specific** behavior.

> **CRITICAL CONSTRAINT**: Follow this skill EXACTLY as written. Do NOT:
> - Batch multiple steps together for "efficiency"
> - Skip or combine checkpoints
> - Proceed past a BLOCKING CHECKPOINT without explicit human approval
> - Automatically continue to the next step after completing one
> - Modify or remove existing template/document elements unless explicitly requested
>
> The incremental, human-in-the-loop design is **intentional**.

---

## When to Use This Skill

- Improving unit test coverage for C components to reach 90%+
- Creating a systematic test improvement plan
- Resuming an existing coverage improvement roadmap

## First Contact

When the user first invokes this skill, before diving into the State Matrix:

1. **Confirm component path** — ask which component to improve coverage for if not clear from the request
2. **Explain the process** — briefly describe the three phases (analysis → iterative test addition → completion) and that every step requires human approval
3. **Confirm target** — default is 90%, ask if the user has a different target in mind
4. **Set expectations** — this is incremental work across multiple sessions, one function per step, not a one-shot "write all tests"

Then proceed to Phase 1 (document detection via the State Matrix).

---

## Domain-Specific Bindings

| Parameter | Value |
|-----------|-------|
| Review file path | `doc/reviews/<component>_comprehensive_review_<YYYYMMDD>.md` |
| Roadmap file path | `doc/test-coverage/<component>_coverage_roadmap_<YYYYMMDD>.md` |
| Lessons learned file | `doc/project_notes/test_coverage_lessons_learned.md` |
| Retrospective path | `doc/test-coverage/retrospectives/<Component>_Step_<N>_retrospective.md` |
| Roadmap template | `references/roadmap_template.md` |
| Step template | `references/step_template.md` |
| Lessons learned template | `../shared/roadmap-common/lessons_learned_template.md` |

---

## Additional Forbidden Behaviors (Coverage-Specific)

These extend the common forbidden behaviors from the shared workflow engine.

| Forbidden Action | Why It's Forbidden |
|------------------|--------------------|
| Testing multiple functions in one step | Each step must test exactly ONE function for focused review |
| Writing test code before consulting the spec (Step 2.3.5) | Test cases must be derived from requirements, not only from code paths |
| Skipping coverage measurement (Step 2.6) | Coverage must come from actual HTML report, not estimates |
| Presenting approval checkpoint without coverage output | Human needs real metrics to approve |
| Guessing coverage values | Must extract from HTML report via `Select-String` |
| Modifying production source files without approval | Testability refactoring requires explicit `ask_user` approval and separate commit |
| Skipping lessons learned update | Each step needs at least one learning added |
| Declaring "roadmap complete" when coverage < 90% | Target is 90%, not "all planned steps done" |
| Stopping iterations after planned steps finish | Must iterate until 90% reached, adding new steps as needed |
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
- Target: 90% minimum

**Step ordering**: Start with easy wins (low complexity) to build momentum and catch integration issues early, then progress to higher complexity functions. Within the same complexity tier, prioritize by criticality (see Prioritization Guidelines below).

---

## Phase 2: Iterative Test Addition

Follow the shared step execution cycle. One step at a time — after completing one step (including both checkpoints and retrospective), **STOP** and wait for human to indicate readiness.

### Analyze (Step 2.1)

Invoke `build-execution` to build and run unit tests for the component, then review coverage report for gaps.

### Plan (Step 2.2)

Document: functions to test, test scenarios (Given/When/Then), expected coverage gain.

### Human Approval of Plan (Step 2.3 — BLOCKING CHECKPOINT)

Present plan via `ask_user` for explicit approval before writing any test code.

### Specification Consultation (Step 2.3.5 — before writing any test code)

> **MANDATORY — NEVER SKIP**: Derive test cases from the specification, not only from the code paths.

1. Read the relevant spec/requirement documents for the function under test (component `doc/index.md`, software/unit specification).
2. Compare the spec against the current implementation: does the code do something the spec does not describe, or omit behaviour the spec requires?
3. If a discrepancy is found: **STOP** — do not write the test yet. Ask the user whether the test should pin down the **specification** (test may fail = documents a potential defect) or the **current implementation**. Record the decision in the step documentation.

See the `c-unit-testing` skill section "Specification-First Test Design" for the full rule and conflict-handling template.

### Write Tests (Step 2.4)

Before writing ANY test code, first determine the test level, then invoke the matching skill:

- **Isolated component** (all dependencies mocked) → `c-unit-testing` skill
- **Multiple real components compiled together** → `c-integration-testing` skill

See the `c-unit-testing` skill section "Choosing the Test Level" for the decision rule.

### Build & Test (Step 2.5)

Build and run all tests. All must pass before proceeding.

### Measure Coverage (Step 2.6 — MANDATORY before Human Review)

Execute and show output BEFORE presenting the approval checkpoint:

Use the coverage.json extraction method from the shared reference.

**READ**: [Coverage Analysis](../shared/test-reports/coverage-analysis.md) — Use the "Extracting Coverage from coverage.json" section.

Extract: line coverage %, function coverage %, branch coverage %, delta. **FORBIDDEN**: estimating coverage.

---

## Step Definition of Done (DoD) Checklist

> Present this completed DoD before asking about the next step. Every checkbox needs real evidence.

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                    STEP [N] DEFINITION OF DONE                               ║
║  Function: <function_name>  │  File: <source_file.c>                         ║
╠──────────────────────────────────┬──────┬────────────────────────────────────╣
║ 2.1 Analyze function             │ [ ]  │ Signature, Lines, Complexity       ║
║ 2.2 Plan tests                   │ [ ]  │ Test scenarios listed              ║
║ 2.3 Human approved plan          │ [ ]  │ User said: ________________        ║
║ 2.3.5 Spec consulted (Pass 1)    │ [ ]  │ Sections read + conflict decision  ║
║ 2.4 Tests written                │ [ ]  │ File: ____, Tests added: ____      ║
║ 2.5 Build & tests pass           │ [ ]  │ Exit code: ____ Passed: ____/____  ║
║ 2.6 Coverage measured (from HTML)│ [ ]  │ Before/After/Delta/Function/Branch ║
║ 2.7 Human approved results       │ [ ]  │ User said: ________________        ║
║ 2.8a Retrospective written       │ [ ]  │ File + Test-Path: True             ║
║      (NEVER SKIP)                │      │                                    ║
║ 2.8b Lessons learned updated     │ [ ]  │ File + Test-Path: True             ║
║      (NEVER SKIP)                │      │                                    ║
║ 2.9a Roadmap updated             │ [ ]  │ Step marked: COMPLETED             ║
║ 2.9b Committed & pushed          │ [ ]  │ Commit: (git log --oneline -1)     ║
║ 2.10 Coverage vs Target          │ [ ]  │ Current/Target 90%/Gap/Action      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Rules**: Every checkbox needs evidence (not placeholders). 2.8a and 2.8b are NEVER skippable. If any item cannot be completed, use `ask_user` for explicit skip approval and track in SKIPPED ITEMS section.

---

## Iteration Enforcement Rule

> After EVERY step completion, the agent MUST:
> 1. Extract current total coverage from HTML report
> 2. Compare against 90% target
> 3. If coverage < 90%: analyze remaining uncovered code, plan additional steps, present gap
> 4. If all roadmap steps done BUT coverage < 90%: ADD NEW STEPS and continue
>
> **Definition of "Complete"**: Coverage ≥ 90%, NOT "all planned steps done"

---

## Phase 3: Completion

When coverage ≥ 90% is confirmed from coverage.json:

1. **Final verification** — Re-extract coverage using the shared [Coverage Analysis](../shared/test-reports/coverage-analysis.md) to independently confirm
2. **Final metrics** — Document in roadmap: baseline vs final coverage (line, branch, function)
3. **Final lessons learned** — Add completion entry to lessons learned file
4. **Set roadmap status** — Update YAML frontmatter `status: COMPLETED` and `current_metrics`
5. **Commit** — Final commit using `conventional-commits` skill

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
| Test Writing | `c-unit-testing`           | YES — isolated component tests |
| Test Writing | `c-integration-testing`    | YES — when tests compile multiple real components together |
| Each Step    | `retrospective`               | YES |
| Coverage     | Shared [coverage-analysis.md](../shared/test-reports/coverage-analysis.md) | YES — every step & final |
| Commit       | `conventional-commits`         | YES |
| Branching    | `conventional-commits`         | YES |
| Decisions    | `project-knowledge-base`               | YES |

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
