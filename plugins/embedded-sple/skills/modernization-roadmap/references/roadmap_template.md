---
component: <COMPONENT_PATH>
created: <YYYY-MM-DD>
last_updated: <YYYY-MM-DD HH:MM>
status: IN_PROGRESS
current_step: 0
total_steps: <N>

baseline_metrics:
  ram_bytes: <NNNN>
  rom_bytes: <NNNN>
  test_coverage_percent: <NN>
  his_metrics:
    v_g: <cyclomatic_complexity>
    stpth: <statement_path>
    stcyc: <statement_cyclomatic>
    calling: <calling_functions>
    called: <called_functions>
    comment_density: <percent>

current_metrics:
  ram_bytes: <NNNN>
  rom_bytes: <NNNN>
  test_coverage_percent: <NN>

human_stakeholders:
  - name: <Name>
    role: <Role>

risks:
  - id: R1
    description: <Risk description>
    probability: low | medium | high
    impact: low | medium | high
    mitigation: <Mitigation strategy>
    status: open | mitigated | closed
---

# Modernization Roadmap: <Component Name>

## Overview

| Field              | Value                          |
| ------------------ | ------------------------------ |
| Component          | `<COMPONENT_PATH>`             |
| Start Date         | <YYYY-MM-DD>                   |
| Target Completion  | <YYYY-MM-DD>                   |
| Current Status     | Step <N> of <M>                |
| Lead               | <Name>                         |

## Goals

1. <Primary goal, e.g., "Improve testability">
2. <Secondary goal, e.g., "Reduce cyclomatic complexity">
3. <Tertiary goal, e.g., "Decouple from hardware dependencies">

## Scope

### In Scope

- <File or module 1>
- <File or module 2>

### Out of Scope

- <Explicitly excluded item>

## Baseline Analysis

### Comprehensive Review Summary

**Review document**: `doc/reviews/<component>_review_<YYYYMMDD>.md`

Key findings:

1. <Finding 1>
2. <Finding 2>
3. <Finding 3>

### Metrics Baseline

| Metric                | Baseline | Target   | Current  |
| --------------------- | -------- | -------- | -------- |
| RAM (bytes)           | <NNNN>   | <NNNN>   | <NNNN>   |
| ROM (bytes)           | <NNNN>   | <NNNN>   | <NNNN>   |
| Test Coverage (%)     | <NN>     | <NN>     | <NN>     |
| Cyclomatic Complexity | <N>      | <N>      | <N>      |

## Test Safety Net

### Characterization Tests

| Test Suite            | Tests | Coverage | Status  |
| --------------------- | ----- | -------- | ------- |
| <component>_unittests | <N>   | <NN>%    | ✅ Pass |

### Critical Paths Covered

- [ ] <Critical function 1>
- [ ] <Critical function 2>
- [ ] <State machine transitions>

---

## Modernization Steps

### Step 1: <Step Name>

**Status**: `NOT_STARTED` | `IN_PROGRESS` | `COMPLETED` | `BLOCKED`

| Field      | Value            |
| ---------- | ---------------- |
| Started    | <YYYY-MM-DD>     |
| Completed  | <YYYY-MM-DD>     |
| Approved by| <Name>           |

#### Objective

<What this step achieves in 1-2 sentences>

#### Changes

- [ ] <Specific change 1>
- [ ] <Specific change 2>
- [ ] <Specific change 3>

#### Definition of Done

- [ ] All unit tests pass
- [ ] RAM delta < 10% (actual: <N>%)
- [ ] ROM delta < 10% (actual: <N>%)
- [ ] Human review approved
- [ ] Retrospective completed
- [ ] Changes committed and pushed

#### Retrospective Notes

<Brief notes from retrospective, or link to full retrospective>

#### Commit

- SHA: `<commit_sha>`
- Message: `modernization(<component>): <description>`

---

### Step 2: <Step Name>

**Status**: `NOT_STARTED`

...

---

## Lessons Learned Reference

See: `doc/project_notes/modernization_lessons_learned.md`

Key lessons applied in this roadmap:

1. <Lesson from previous modernizations>
2. <Lesson from previous modernizations>

---

## Completion Checklist

- [ ] All steps completed
- [ ] Final comprehensive review performed
- [ ] Metrics targets achieved
- [ ] Final lessons learned documented
- [ ] Stakeholder sign-off received
- [ ] Roadmap archived as completed

## Final Metrics Comparison

| Metric                | Baseline | Final    | Delta    |
| --------------------- | -------- | -------- | -------- |
| RAM (bytes)           | <NNNN>   | <NNNN>   | <+/- N%> |
| ROM (bytes)           | <NNNN>   | <NNNN>   | <+/- N%> |
| Test Coverage (%)     | <NN>     | <NN>     | <+/- N>  |
| Cyclomatic Complexity | <N>      | <N>      | <+/- N>  |

---

**Document History**

| Date       | Author  | Change                        |
| ---------- | ------- | ----------------------------- |
| YYYY-MM-DD | <Name>  | Initial roadmap created       |
| YYYY-MM-DD | <Name>  | Step 1 completed              |
