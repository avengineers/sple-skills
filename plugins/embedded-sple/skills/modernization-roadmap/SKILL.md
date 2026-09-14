---
name: modernization-roadmap
description: Use this skill when refactoring, modernizing, or decomposing legacy C components. Guides incremental code improvements with human-in-the-loop checkpoints, test safety nets, and file-based state tracking. Starts with a comprehensive review (static analysis, coverage, HIS metrics) then creates a step-by-step roadmap. Trigger on any mention of modernizing embedded code, reducing technical debt in C modules, refactoring tightly-coupled components, creating a refactoring plan, or resuming an existing modernization roadmap — even if the user just says "clean up this legacy mess".
compatibility: "Requires PowerShell 5.1+ and Python 3.8+. Depends on sibling skills - build-execution, c-unit-testing, c-code-review-comprehensive, retrospective, conventional-commits, project-knowledge-base."
---

# Legacy Modernization Roadmap

This skill guides systematic modernization of legacy C components using an incremental, test-safe approach with human stakeholder involvement at every step.

> **Philosophy**: Small, verifiable steps with human approval. Never big-bang rewrites.

## Workflow Engine

This skill uses the shared incremental roadmap framework.  
**READ FILE**: [Roadmap Workflow Engine](../shared/roadmap-common/roadmap-workflow-engine.md) — for the document state machine, step execution cycle, human checkpoint patterns, and commit workflow.

All common workflow rules (forbidden behaviors, retrospective requirements) from the shared engine apply here. The sections below define **modernization-specific** behavior.

---

## First Contact

When the user first invokes this skill:

1. **Confirm component path** — ask which component to modernize if not clear from the request
2. **Run the document detection** — the globs in *Document Detection* above, before asking anything else. What is worth asking depends on whether a roadmap already exists, so a question asked first can overwrite an agreement that was already made
3. **A roadmap exists** — report where it stands: current step of total, the metrics against their targets, and the date of the file you picked. Resume there. Do **not** re-ask for the stakeholders or the goals — the roadmap records them. Change them only if the user asks, and then say what they were before
4. **No roadmap exists** — explain the three phases (analysis → iterative steps → completion) and that every step requires human approval; ask who should review and approve changes, for the roadmap document; set expectations — incremental work across multiple sessions, not a one-shot refactoring

Then proceed to Phase 1.

---

## Additional Modernization Principles

| Principle             | Description                                                    |
| ----------------------| -------------------------------------------------------------- |
| **Safety First**      | Freeze behavior with tests before any change                   |
| **Resource Limits**   | Max 10% RAM/ROM increase per step                              |

---

## Domain-Specific Bindings

These paths and parameters fill the consuming-skill slots in the shared workflow engine.

| Parameter | Value |
|-----------|-------|
| Review file path | `doc/reviews/<component>_comprehensive_review_<YYYYMMDD>.md` |
| Roadmap file path | `doc/modernization/<component>_modernization_roadmap_<YYYYMMDD>.md` |
| Lessons learned file | `doc/project_notes/modernization_lessons_learned.md` |
| Retrospective path | `doc/modernization/retrospectives/<component>_Step_<N>_retrospective.md` |
| Roadmap template | `references/roadmap_template.md` |
| Step template | `references/step_template.md` |
| Lessons learned template | `../shared/roadmap-common/lessons_learned_template.md` |

### Document Detection

The shared engine's State Matrix runs these globs; it does not define them. Run them **before
anything else**. A roadmap the detection misses is a roadmap that gets written a second time, and
the progress recorded in the first one is lost.

<!-- document-detection:begin -->

| Document | Glob |
|----------|------|
| Comprehensive review | `doc/reviews/<component>_comprehensive_review_*.md` |
| Modernization roadmap | `doc/modernization/<component>_modernization_roadmap_*.md` |

| Situation | Rule |
|-----------|------|
| Several files match | Take the one with the newest date in its file name and say which one you took. Never merge two roadmaps, and never start a third. |
| Newest unclear | Two files carry the same date, or one carries none: stop and ask which to resume. Guessing here discards somebody's work. |

<!-- document-detection:end -->

---

## Additional Forbidden Behaviors (Modernization-Specific)

These extend the common forbidden behaviors from the shared workflow engine.

| Forbidden Action | Why It's Forbidden |
|------------------|--------------------|
| Exceeding 10% RAM/ROM increase per step | Resource constraints are hard limits for embedded targets |
| Skipping characterization tests when line coverage < 90% | Behavior must be frozen before refactoring |

---

## Phase 1: Setup & Analysis

Follow the shared Phase 1 skeleton (check docs → comprehensive review → create roadmap).

### Comprehensive Review (Step 1.2)

Invoke `c-code-review-comprehensive`. The comprehensive review includes:

- **CHK_Code Checklist** (41 items) — mandatory
- **BARR-C:2018 Compliance** — mandatory
- Architecture and dependencies analysis
- Technical debt assessment
- Static Analysis (Polyspace/QAC findings)
- Test Coverage baseline
- HIS Metrics baseline
- Code quality findings with IDs (CQ-001, etc.)
- Security findings with IDs (SEC-001, etc.)

The roadmap MUST reference findings from this review by their IDs.

### Coverage Check (after Step 1.3)

After creating the roadmap (Step 1.3), extract **line coverage** from the comprehensive review
results. Line coverage is the gate here, the same metric `test-coverage-roadmap` gates on, so a
component does not pass one skill and fail the other:

- If line coverage ≥ 90%: proceed to Phase 2
- If line coverage < 90%: add characterization tests first

Before writing ANY test code, invoke the `c-unit-testing` skill for project conventions (BDD/Gherkin, hammocking, traceability).

---

## Phase 2: Iterative Modernization

Follow the shared step execution cycle. Domain-specific details for each sub-step:

### Step 2.1: Evaluate & Analyze

Read lessons learned file and current step definition from roadmap.

### Step 2.2: Plan

Update the roadmap with:
- Specific refactoring changes planned
- Files to modify
- Expected RAM/ROM impact
- Definition of Done (including resource constraints)

### Step 2.3: Human Approval of Plan (BLOCKING CHECKPOINT)

Present plan via `ask_user` for explicit approval before any code changes.

### Step 2.4: Execute

- Only changes defined in the step plan
- Run unit tests after each file modification
- Stop immediately if tests fail

### Step 2.5: Build & Test

Invoke `build-execution` with `buildKit=test` to build and run unit tests for the component.

### Step 2.6: Measure & Verify

Run `resource_tracker.py` to verify RAM/ROM delta is within the 10% limit. Record metrics before presenting to human.

**First step** (create baseline from the build before changes):

```powershell
$mapFile = "build/<VARIANT>/components/<path>/<component>.map"
python <skill-path>/scripts/resource_tracker.py baseline $mapFile doc/modernization/<component>_baseline.json
```

**After changes** (compare against baseline):

```powershell
python <skill-path>/scripts/resource_tracker.py compare doc/modernization/<component>_baseline.json $mapFile
```

> **Note**: The map file path depends on the build variant and component location.
> Use `build-execution` to build the component first, then locate the `.map`
> file in the build output directory. If no map file is produced, ask the user
> for the correct path or check the linker settings.

### Step 2.7: Human Review of Results (BLOCKING CHECKPOINT)

Present via `ask_user`:
1. Summary of changes made
2. Test results (all pass)
3. RAM/ROM delta (from Step 2.6)
4. Any deviations from plan

### Step 2.8: Retrospective & Lessons (MANDATORY)

Invoke `retrospective` skill. Save the file, then verify that the file exists. Update lessons learned file.

### Step 2.9: Document & Commit

Update roadmap (step → COMPLETED), verify DoD complete, commit using `conventional-commits` skill.

### Step 2.10: Check Target

Evaluate whether modernization goals are met. If more steps remain, report progress and wait for human to initiate next step.

---

## Step Definition of Done (DoD) Checklist

> Present this completed DoD before asking about the next step. Every checkbox needs real evidence.

<!-- step-dod:begin -->

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                    STEP [N] DEFINITION OF DONE                               ║
║  Objective: <step_objective>                                                 ║
╠──────────────────────────────────┬──────┬────────────────────────────────────╣
║ 2.1 Docs evaluated               │ [ ]  │ Lessons consulted: Yes/No          ║
║ 2.2 Plan created                 │ [ ]  │ Files to modify: ____              ║
║                                  │      │ RAM/ROM impact: ____               ║
║ 2.3 Human approved plan          │ [ ]  │ User said: ________________        ║
║ 2.4 Changes implemented          │ [ ]  │ Files changed: ____                ║
║ 2.5 Build & tests pass           │ [ ]  │ Exit code: ____ Tests: ____/____   ║
║ 2.6 Resources measured           │ [ ]  │ RAM delta: ____% ROM delta: ____%  ║
║                                  │      │ Within 10% limit: Yes/No           ║
║ 2.7 Human approved results       │ [ ]  │ User said: ________________        ║
║ 2.8a Retrospective written       │ [ ]  │ File: ________________________     ║
║      (NEVER SKIP)                │      │ Existence check: True/False        ║
║ 2.8b Lessons learned updated     │ [ ]  │ Entry added: Yes/No                ║
║      (NEVER SKIP)                │      │                                    ║
║ 2.9a Roadmap updated             │ [ ]  │ Step marked: COMPLETED             ║
║ 2.9b Committed & pushed          │ [ ]  │ Commit: (git log --oneline -1)     ║
║ 2.10 Target checked              │ [ ]  │ Goals met: Yes/No / Next action    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

<!-- step-dod:end -->

**Rules**: Fill ALL fields with actual values (no `____` placeholders in final output). Steps 2.8a and 2.8b are NEVER skippable. If any other item cannot be completed, use `ask_user` for explicit skip approval.

---

## Phase 3: Completion

Invoke `c-code-review-comprehensive` as final comparison review.

1. Compare metrics: before vs after
2. Update roadmap with final metrics
3. Document final lessons learned
4. **Record the decisions that outlive this roadmap** — Invoke `project-knowledge-base` for anything a future maintainer needs but would never find in an archived roadmap: a rejected refactoring and why, an interface that had to stay for compatibility, a resource budget that was deliberately exceeded. Skip it when none of those occurred — say so rather than writing an empty entry
5. Set roadmap status to `COMPLETED`

---

## Required Skill Invocations

| Phase       | Skill to Invoke                | Mandatory |
|-------------|--------------------------------|-----------|
| Analysis    | `c-code-review-comprehensive`  | YES — initial + final review |
| Build & Test | `build-execution`             | YES — every step |
| Test Safety | `c-unit-testing`           | If coverage < 90% |
| Each Step   | `retrospective`               | YES |
| Commit      | `conventional-commits`         | YES |
| Branching   | `conventional-commits`         | YES |
| Decisions   | `project-knowledge-base`       | When a decision outlives the roadmap — see Phase 3 |

> **Note**: Static Analysis, Test Coverage, and HIS Metrics are all included in `c-code-review-comprehensive` — do NOT invoke them separately.

## Templates

- [references/roadmap_template.md](references/roadmap_template.md) — Master roadmap document
- [references/step_template.md](references/step_template.md) — Individual step documentation
- [Lessons learned template](../shared/roadmap-common/lessons_learned_template.md) — Lessons learned format

## Usage Examples

```text
"Modernize components/auto_off/ using the roadmap skill"
"Create a refactoring roadmap for diagnostics.c"
"Resume modernization of the communication_handler component"
"What's the status of the current modernization?"
```
