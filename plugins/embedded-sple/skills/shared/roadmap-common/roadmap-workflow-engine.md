# Incremental Roadmap Workflow Engine

Shared workflow framework for skills that guide incremental, human-in-the-loop improvement of C components. Used by `modernization-roadmap` and `test-coverage-roadmap`.

Each skill that uses this engine defines its own **domain-specific bindings** (paths, metrics, thresholds, step content) while following this common execution framework.

---

## Core Principles

| Principle             | Description                                                    |
| ----------------------| -------------------------------------------------------------- |
| **Human Checkpoints** | Wait for stakeholder approval before proceeding                |
| **Incremental Steps** | Small, verifiable changes — one step at a time                 |
| **Persistent State**  | All progress documented in files, not just chat context        |
| **Lessons Learned**   | Consult and update lessons learned before/after every step     |
| **Verification**      | Verify required artifacts exist before proceeding              |

---

## Document State Machine

When the skill is invoked, the agent determines current state by checking for two documents:
1. **Comprehensive Review** — baseline analysis from `c-code-review-comprehensive`
2. **Roadmap Document** — the step-by-step plan

### State Matrix

| Comprehensive Review | Roadmap | Action |
|------------------|---------|--------|
| Exists | Exists | **RESUME**: Load roadmap, find current step (IN_PROGRESS or next NOT_STARTED), continue |
| Exists | Missing | **CREATE_ROADMAP**: Create roadmap from existing review |
| Missing | Exists | **REGENERATE**: Review is prerequisite — run review first, then regenerate roadmap |
| Missing | Missing | **FRESH_START**: Run comprehensive review, then create roadmap |

### Document Detection

The consuming skill defines the concrete glob patterns for its review and roadmap files.  
The agent executes those globs, determines which documents exist, and maps to the state matrix above.

### Resume Behavior

When both documents exist:
1. Read the existing roadmap file
2. Find the current step from YAML frontmatter or step status markers
3. Identify which step is IN_PROGRESS or the next NOT_STARTED step
4. Report state to user and continue from that step

---

## Common Forbidden Agent Behaviors

These rules apply to every roadmap-based skill. Each skill may add additional domain-specific forbidden behaviors.

| Forbidden Action | Why It's Forbidden | How User Catches It |
|------------------|-------------------|---------------------|
| Batching multiple steps together | Prevents human review between steps | User doesn't see intermediate outputs |
| Skipping plan approval checkpoint | Human must validate approach before coding | No `ask_user` for plan approval |
| Skipping result approval checkpoint | Human must validate quality before proceeding | No `ask_user` for result approval |
| Proceeding after BLOCKING without response | Defeats human-in-the-loop design | Agent continues without user response |
| Auto-continuing to next step | Each step requires explicit human initiation | No pause between steps |
| Skipping retrospective | Each step needs learnings captured | No retrospective file created |
| Asking "next step?" without retrospective file | Retrospective must exist on disk before proceeding | No retrospective file created |
| Not updating roadmap after step | Progress must be tracked | Roadmap not updated with metrics |
| Removing or rewriting existing template or document elements without being asked | The roadmap document carries the state across sessions — silent edits destroy content the user agreed to | Sections the user wrote are gone or reworded |
| Committing with incomplete DoD | Required artifacts must exist before commit | DoD items missing evidence |
| Proceeding without presenting completed DoD | All checkboxes must be filled with evidence | No DoD table shown |

---

## Phase 1: Setup & Analysis (Common Skeleton)

Every roadmap skill follows this Phase 1 sequence. Domain-specific details (what to extract from the review, how to structure the roadmap) are defined in each skill.

### Step 1.1: Check for Existing Documents

Execute document detection commands defined by the consuming skill. Map result to the State Matrix above and follow the corresponding action.

### Step 1.2: Comprehensive Review

Invoke the `c-code-review-comprehensive` skill against the target component. This provides:
- Current test coverage baseline
- Code complexity analysis
- Static analysis findings
- Metrics baseline

The comprehensive review output is saved to the review file path defined by the consuming skill. Wait for the review to complete before proceeding.

If the state was ROADMAP_ONLY, archive the old roadmap first (rename with `_outdated` suffix), then regenerate after the review.

### Step 1.3: Create Roadmap from Review

1. Create the roadmap output directory if needed
2. Read the roadmap template from the skill's `references/roadmap_template.md`
3. Fill the template using findings from the comprehensive review
4. Save to the roadmap file path defined by the consuming skill

---

## Phase 2: Iterative Execution (Common Pattern)

Each step in the roadmap follows this execution cycle. The consuming skill defines what happens inside each sub-step (refactoring code vs. writing tests, etc.).

### Step Execution Cycle

```
2.1 Evaluate → 2.2 Plan → 2.3 HumanApproval → 2.4 Execute → 2.5 Build&Test → 2.6 Measure → 2.7 HumanReview → 2.8 Retrospective → 2.9 Document&Commit → 2.10 CheckTarget
```

| Step | Phase | Description |
|------|-------|-------------|
| 2.1 | Evaluate & Analyze | Consult lessons learned, read step definition |
| 2.2 | Plan | Detail the step, define DoD |
| 2.3 | Human Approval | BLOCKING CHECKPOINT — present plan via `ask_user` |
| 2.4 | Execute | Implement changes (domain-specific) |
| 2.5 | Build & Test | Build component, verify all tests pass |
| 2.6 | Measure & Verify | Collect metrics (domain-specific measurement) |
| 2.7 | Human Review | BLOCKING CHECKPOINT — present results via `ask_user` |
| 2.8 | Retrospective & Lessons | Write retrospective file + update lessons learned |
| 2.9 | Document & Commit | Update roadmap, verify DoD complete, commit |
| 2.10 | Check Target | Evaluate progress against target, decide next action |

Each consuming skill defines what happens inside each step (especially 2.4 Execute, 2.6 Measure, and 2.10 Check Target).

### Evaluate & Analyze (Step 2.1)

1. Check if the lessons learned file exists (path defined by consuming skill)
2. If exists, read and summarize relevant lessons for the current step
3. Read the current step definition from the roadmap file

### Plan (Step 2.2)

1. Read the step template from the skill's `references/step_template.md`
2. Update the roadmap with detailed step information (status: IN_PROGRESS, planned changes, DoD)
3. Present the plan to the user

### Human Approval of Plan (Step 2.3 — BLOCKING CHECKPOINT)

The agent stops and uses `ask_user` to present the step plan for explicit approval.

Present:
1. What will be changed/added
2. Which files will be modified
3. Expected impact/metrics
4. Definition of Done

If rejected: revise the plan based on feedback.  
If approved: proceed to execution.

### Execute (Step 2.4)

Domain-specific — defined by each consuming skill (refactoring vs. test writing).

### Build & Test (Step 2.5)

Build and test using the `build-execution` skill.  
If tests fail: fix and re-test.  
If tests pass: proceed to measurement.

### Measure & Verify (Step 2.6)

Domain-specific measurement — defined by each consuming skill (coverage report vs. RAM/ROM delta). Collect metrics BEFORE presenting to human for review.

### Human Review of Results (Step 2.7 — BLOCKING CHECKPOINT)

The agent stops and uses `ask_user` to present the completed work for approval.

Present:
1. Summary of changes made
2. Test results
3. Metrics delta (from Step 2.6)
4. Any deviations from plan

If rejected: address feedback and re-execute.  
If approved: proceed to retrospective.

### Retrospective & Lessons (Step 2.8 — MANDATORY — NEVER SKIPPABLE)

Without the retrospective file, the agent cannot proceed to the next step.

1. Invoke the `retrospective` skill
2. Save retrospective file to the path defined by the consuming skill
3. Verify the file exists
4. Update the shared lessons learned file

Retrospective content:
- What went well
- What could be improved
- Lessons learned
- Metrics delta achieved

### Document & Commit (Step 2.9)

1. Update roadmap: step status → `COMPLETED`, timestamp, actual metrics
2. Update or create lessons learned file
3. Verify all DoD items are complete before committing
4. Commit using `conventional-commits` skill
5. Execute and show `git log --oneline -1` to record the commit hash

### Check Target (Step 2.10)

Domain-specific evaluation of progress against the overall goal. The consuming skill defines what "done" means (e.g., the agreed coverage target reached, all modernization steps complete). If the target is not met, the agent identifies what remains and plans additional steps.

---

## Base Definition of Done (DoD) Pattern

Every roadmap skill must present a completed DoD checklist before transitioning to the next step. The base pattern includes these mandatory items that every step must verify:

| Step | Base DoD Item | Evidence Required |
|------|---------------|-------------------|
| 2.2 | Plan created and approved | User approval captured |
| 2.4 | Implementation complete | Files changed listed |
| 2.5 | Build & tests pass | Exit code + test results |
| 2.6 | Metrics measured | Domain-specific measurement evidence |
| 2.7 | Human approved results | User approval captured |
| 2.8 | Retrospective written (NEVER SKIP) | File path + existence check output |
| 2.8 | Lessons learned updated | Entry added confirmation |
| 2.9 | Roadmap step updated | Step marked COMPLETED |
| 2.9 | Committed & pushed | `git log --oneline -1` output |
| 2.10 | Target checked | Progress vs goal documented |

Each consuming skill extends this base with domain-specific items (metrics, coverage data, resource impact, etc.). The DoD template may use `____` as fill-in prompts, but the presented (completed) DoD must contain real evidence — never placeholders.

---

## Phase 3: Completion (Common Pattern)

When all steps are complete (or the target metric is achieved):

1. Run a final verification (defined by consuming skill)
2. Document final metrics in roadmap
3. Document final lessons learned
4. Set roadmap status to `COMPLETED`

---

## State Persistence

All state must be in files, not chat context. The roadmap file uses YAML frontmatter for machine-parseable state:

```yaml
---
component: <component_path>
created: YYYY-MM-DD
last_updated: YYYY-MM-DD HH:MM
status: IN_PROGRESS | COMPLETED | PAUSED
current_step: N
total_steps: M
---
```

Each consuming skill extends this frontmatter with domain-specific fields (metrics, targets, etc.).
