---
component: <COMPONENT_PATH>
created: <YYYY-MM-DD>
last_updated: <YYYY-MM-DD HH:MM>
status: IN_PROGRESS
current_step: 0
total_steps: <N>

baseline_metrics:
  line_coverage_percent: <NN>
  branch_coverage_percent: <NN>
  total_functions: <N>
  covered_functions: <N>
  total_branches: <N>
  covered_branches: <N>

target_metrics:
  line_coverage_percent: <TARGET>

current_metrics:
  line_coverage_percent: <NN>
  branch_coverage_percent: <NN>
  total_functions: <N>
  covered_functions: <N>
  not_testable_lines: <N>
---

# Test Coverage Roadmap: <Component Name>

## Overview

| Field              | Value                          |
| ------------------ | ------------------------------ |
| Component          | `<COMPONENT_PATH>`             |
| Start Date         | <YYYY-MM-DD>                   |
| Current Status     | Step <N> of <M>                |
| Baseline Line Coverage | <NN>%                      |
| Target Line Coverage   | <TARGET>%                  |
| Current Line Coverage  | <NN>%                      |

## Goal

Achieve `<TARGET>`%+ line coverage for this component through incremental test additions.

## Scope

### Source Files to Cover

| File | Current Coverage | Target | Priority |
|------|------------------|--------|----------|
| `<file1.c>` | <NN>% | <TARGET>% | High |
| `<file2.c>` | <NN>% | <TARGET>% | Medium |

### Out of Scope

- <Files explicitly excluded, e.g., auto-generated code>

## Baseline Analysis

### Comprehensive Review Reference

**Review document**: `doc/reviews/<component>_comprehensive_review_<YYYYMMDD>.md`

### Coverage Breakdown

| Category | Covered | Total | Percentage |
|----------|---------|-------|------------|
| Functions | <N> | <N> | <NN>% |
| Branches | <N> | <N> | <NN>% |
| Lines | <N> | <N> | <NN>% |

### Uncovered Functions (Prioritized)

| Function | File | Complexity | Priority | Reason |
|----------|------|------------|----------|--------|
| `<function1>` | `<file.c>` | <N> | High | Critical path |
| `<function2>` | `<file.c>` | <N> | Medium | Error handling |

### Uncovered Branches in Covered Functions

| Function | File | Missing Branch | Priority |
|----------|------|----------------|----------|
| `<function>` | `<file.c>` | Error case | High |
| `<function>` | `<file.c>` | Boundary check | Medium |

---

## Coverage Steps

> **MANDATORY**: Each step covers **exactly ONE function** for focused human review.
> Step 0 is reserved for test infrastructure setup (no function coverage).

### Step 0: Test Infrastructure Setup

**Status**: `NOT_STARTED`

| Field | Value |
|-------|-------|
| Started | - |
| Completed | - |

#### Deliverables

- Create test CMakeLists.txt
- Verify hammocking mocks generated
- Create empty test file structure
- Verify build compiles

#### Definition of Done

<!-- dod:exception -->

Step 0 sets up infrastructure and tests no function, so the rows about a function under test do
not apply: 2.1b (no spec to consult), 2.6 (no coverage delta to measure). Everything else holds,
including the never-skippable 2.8a (retrospective) and 2.8b (lessons learned).

- [ ] Test infrastructure created
- [ ] Build compiles successfully
- [ ] Human review approved (2.7)
- [ ] Retrospective written — 2.8a, never skippable
- [ ] Lessons learned updated — 2.8b, never skippable
- [ ] Roadmap updated and committed (2.9a, 2.9b)

---

### Step 1: <FUNCTION_NAME>

**Status**: `NOT_STARTED` | `IN_PROGRESS` | `COMPLETED`

| Field | Value |
|-------|-------|
| Function | `<function_name>` |
| Line | <line_number> |
| Complexity | Low/Medium/High |
| Started | - |
| Completed | - |
| Line Coverage Before | <NN>% |
| Line Coverage After | <NN>% |
| Line Coverage Gain | +<N>% |

#### Description

<Brief description of what the function does>

#### Test Scenarios

| Scenario | Given | When | Then |
|----------|-------|------|------|
| Happy path | <precondition> | <action> | <expected result> |
| Error case | <precondition> | <action> | <expected result> |
| Boundary | <precondition> | <action> | <expected result> |

#### Definition of Done

<!-- dod:delegated -->

The DoD is the checklist in the skill — `SKILL.md` → *Step Definition of Done (DoD) Checklist*.
Do not restate it here; paste the completed box with real evidence instead. A second list drifts
from the first, and the copy that has lost a mandatory row is the one somebody works from.

#### Tests Added

| Test File | Test Case | Status |
|-----------|-----------|--------|
| `test_<Component>_<Function>.cc` | `<TestName>` | Pass |

---

### Step 2: <FUNCTION_NAME>

**Status**: `NOT_STARTED`

| Field | Value |
|-------|-------|
| Function | `<function_name>` |
| Line | <line_number> |
| Complexity | Low/Medium/High |
| Started | - |
| Completed | - |
| Line Coverage Before | <NN>% |
| Line Coverage After | <NN>% |
| Line Coverage Gain | +<N>% |

...

---

## Untestable Code

Lines no test can reach. The reported coverage is **not** adjusted for them — this register
explains the remaining gap instead. Only two reasons are allowed, and each needs its evidence.
See the skill section *Untestable Code (NOT_TESTABLE Register)*.

| Location | Lines | Reason | Evidence | Approved |
|----------|-------|--------|----------|----------|
| `<file.c>:<NN>` (`default:` case) | <N> | `DEFENSIVE_BY_DESIGN` | defensive-programming-checklist: enum values validated | <YYYY-MM-DD> |
| `<file.c>:<NN>-<NN>` | <N> | `UNREACHABLE_DEFECT` | UNR `<finding-id>` — removal recommended, handed to `modernization-roadmap` | <YYYY-MM-DD> |

| Field | Value |
|-------|-------|
| Lines in register | <N> |
| Gap to target | <N.N>% |
| Of that explained by the register | <N.N>% |
| Testable remainder | <N.N>% |

## Progress Tracking

| Step | Function | Expected Gain | Actual Gain | Status |
|------|----------|---------------|-------------|--------|
| 0 | Test Infrastructure | - | - | NOT_STARTED |
| 1 | `<function1>` | +X% | - | NOT_STARTED |
| 2 | `<function2>` | +X% | - | NOT_STARTED |
| 3 | `<function3>` | +X% | - | NOT_STARTED |

## Completion Checklist

- [ ] All steps completed
- [ ] Line coverage >= `<TARGET>`% verified, or the gap fully explained by the register
- [ ] NOT_TESTABLE register confirmed — every entry has a reason and its evidence
- [ ] All tests pass
- [ ] Lessons learned documented
- [ ] Roadmap archived as completed

## Final Metrics

| Metric | Baseline | Final | Delta |
|--------|----------|-------|-------|
| Line coverage (%) | <NN> | <NN> | +<N> |
| Branch coverage (%) | <NN> | <NN> | +<N> |
| Function coverage (%) | <NN> | <NN> | +<N> |
| Test Cases | <N> | <N> | +<N> |
| Test Files | <N> | <N> | +<N> |
| Lines in NOT_TESTABLE register | <N> | <N> | +<N> |

---

## Lessons Learned Reference

See: `doc/project_notes/test_coverage_lessons_learned.md`

---

**Document History**

| Date | Author | Change |
|------|--------|--------|
| YYYY-MM-DD | <Name> | Initial roadmap created |
| YYYY-MM-DD | <Name> | Step 1 completed |
