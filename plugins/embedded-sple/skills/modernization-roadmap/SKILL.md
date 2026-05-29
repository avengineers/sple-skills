---
name: modernization-roadmap
description: Use this skill when refactoring, modernizing, or decomposing legacy C components. Guides incremental code improvements with human-in-the-loop checkpoints, test safety nets, and file-based state tracking. Starts with a comprehensive review (static analysis, coverage, HIS metrics) then creates a step-by-step roadmap. Trigger on any mention of modernizing embedded code, reducing technical debt in C modules, refactoring tightly-coupled components, or creating a refactoring plan — even if the user just says "clean up this legacy mess".
compatibility: "Requires PowerShell 5.1+ and Python 3.8+. Depends on sibling skills - build-execution, c-unit-testing, c-code-review-comprehensive, retrospective, conventional-commits, project-knowledge-base."
---

# Legacy Modernization Roadmap

This skill guides systematic modernization of legacy C components using an incremental, test-safe approach with human stakeholder involvement at every step.

> **Philosophy**: Small, verifiable steps with human approval. Never big-bang rewrites.

## Workflow Engine

This skill uses the shared incremental roadmap framework.  
**READ FILE**: [Roadmap Workflow Engine](../shared/roadmap-common/roadmap-workflow-engine.md) — for the document state machine, step execution cycle, human checkpoint patterns, and commit workflow.

All common workflow rules (forbidden behaviors, retrospective requirements) from the shared engine apply here. The sections below define **modernization-specific** behavior.

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

- Modernizing monolithic C components
- Decomposing tightly coupled code
- Improving maintainability and testability
- Reducing technical debt incrementally

## First Contact

When the user first invokes this skill, before diving into the State Matrix:

1. **Confirm component path** — ask which component to modernize if not clear from the request
2. **Explain the process** — briefly describe the three phases (analysis → iterative steps → completion) and that every step requires human approval
3. **Identify stakeholders** — ask who should review and approve changes (for the roadmap document)
4. **Set expectations** — this is incremental work across multiple sessions, not a one-shot refactoring

Then proceed to Phase 1 (document detection via the State Matrix).

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
| Retrospective path | `doc/modernization/retrospectives/<Component>_Step_<N>_retrospective.md` |
| Roadmap template | `references/roadmap_template.md` |
| Step template | `references/step_template.md` |
| Lessons learned template | `../shared/roadmap-common/lessons_learned_template.md` |

---

## Additional Forbidden Behaviors (Modernization-Specific)

These extend the common forbidden behaviors from the shared workflow engine.

| Forbidden Action | Why It's Forbidden |
|------------------|--------------------|
| Exceeding 10% RAM/ROM increase per step | Resource constraints are hard limits for embedded targets |
| Skipping characterization tests when coverage < 90% | Behavior must be frozen before refactoring |

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

After creating the roadmap (Step 1.3), extract coverage from comprehensive review results:

- If coverage ≥ 90%: proceed to Phase 2
- If coverage < 90%: add characterization tests first

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

Invoke `build-execution` to build and run unit tests for the component.

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

Invoke `retrospective` skill. Save file, verify with `Test-Path`. Update lessons learned file.

### Step 2.9: Document & Commit

Update roadmap (step → COMPLETED), verify DoD complete, commit using `conventional-commits` skill.

### Step 2.10: Check Target

Evaluate whether modernization goals are met. If more steps remain, report progress and wait for human to initiate next step.

---

## Step Definition of Done (DoD) Checklist

> Present this completed DoD before asking about the next step. Every checkbox needs real evidence.

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
║      (NEVER SKIP)                │      │ Test-Path result: True/False       ║
║ 2.8b Lessons learned updated     │ [ ]  │ Entry added: Yes/No                ║
║      (NEVER SKIP)                │      │                                    ║
║ 2.9a Roadmap updated             │ [ ]  │ Step marked: COMPLETED             ║
║ 2.9b Committed & pushed          │ [ ]  │ Commit: (git log --oneline -1)     ║
║ 2.10 Target checked              │ [ ]  │ Goals met: Yes/No / Next action    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Rules**: Fill ALL fields with actual values (no `____` placeholders in final output). Steps 2.8a and 2.8b are NEVER skippable. If any other item cannot be completed, use `ask_user` for explicit skip approval.

---

## Phase 3: Completion

Invoke `c-code-review-comprehensive` as final comparison review.

1. Compare metrics: before vs after
2. Update roadmap with final metrics
3. Document final lessons learned
4. Set roadmap status to `COMPLETED`

---

## Required Skill Invocations

| Phase       | Skill to Invoke                | Mandatory |
|-------------|--------------------------------|-----------|
| Analysis    | `c-code-review-comprehensive`  | YES — initial + final review |
| Test Safety | `c-unit-testing`           | If coverage < 90% |
| Each Step   | `retrospective`               | YES |
| Commit      | `conventional-commits`         | YES |
| Branching   | `conventional-commits`         | YES |
| Decisions   | `project-knowledge-base`               | YES |

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
