| Field              | Value                                                  |
|--------------------|--------------------------------------------------------|
| **Component**      | `<component_name>`                                     |
| **Date**           | [YYYY-MM-DD]                                           |
| **Review Start**   | [HH:MM:SS]                                             |
| **Review End**     | [HH:MM:SS]                                             |
| **Duration**       | [HH:MM:SS]                                             |
| **Reviewer**       | [reviewer name / AI model]                             |
| **Git Branch**     | [branch name]                                          |
| **Commit Hash**    | [short hash]                                           |
| **Commit Author**  | [author name]                                          |
| **Jira Ticket**    | [TICKET-XXX or N/A]                                    |
| **Branch Type**    | [feature / fix / refactor / chore / hotfix / ...]      |
| **Files Reviewed** | List every individual file that was opened and read (one per line): `path/to/file.c`, `path/to/file.h`, ... |

# Comprehensive Code Review Protocol

---

## Executive Summary

### Overall Assessment: **<PASS / PASS WITH IMPROVEMENTS / NEEDS WORK / FAIL>**

<Brief 2-3 sentence summary of overall code quality and key findings>

**Key Strengths:**

- ✅ <strength 1>
- ✅ <strength 2>

**Primary Concerns:**

- ⚠️ <concern 1>
- ⚠️ <concern 2>

---

## Review Scope

All areas below were performed (all mandatory):

- [x] 🔒 **Static Analysis (Polyspace/QAC)**
- [x] 🔒 **CHK_Code Checklist** (41 items)
- [x] 🔒 **BARR-C:2018 Compliance** (c-coding-standards skill)
- [x] 🔒 **MISRA C:2012 Compliance**
- [x] 🔒 **Clean Code Assessment**
- [x] 🔒 **Defensive Programming**
- [x] 🔒 **Legacy Code / Testability**
- [x] 🔒 **HIS Metrics Analysis**
- [x] 🔒 **Architecture Review**
- [x] 🔒 **Test Coverage Analysis**

---

## 1. CHK_Code Checklist

Reference: [CHK_Code Checklist](../../c-code-review-checklist/references/chk-code-checklist.md)

### Summary

| Metric            | Count |
|-------------------|-------|
| Checks performed  | X/41  |
| ✅ Passed         | X     |
| ❌ Failed         | X     |
| ⏭️ Not applicable | X     |

### Critical Findings

<List CHK items that failed with status Critical>

### Warnings

<List CHK items that failed with status Warning>

---

## 2. BARR-C:2018 Compliance

Reference: [Quick Scan](../../c-coding-standards/checklists/11-quick-scan.md) | [PR Review](../../c-coding-standards/checklists/12-pr-review.md)

### Quick Scan Results

<Summary of BARR-C quick scan>

### Detailed Findings

<List specific BARR-C violations if any>

---

## 3. MISRA C:2012 Compliance

Reference: [MISRA Checklist](../checklists/misra-c-checklist.md)

### Summary

| Category  | Checked | Violations |
|-----------|---------|------------|
| Mandatory | X       | X          |
| Required  | X       | X          |
| Advisory  | X       | X          |

### Violations

<List MISRA rule violations with code locations>

---

## 4. Clean Code Assessment

Reference: [Clean Code Checklist](../checklists/clean-code-checklist.md)

### Assessment

| Category       | Status    | Notes |
|----------------|-----------|-------|
| Naming         | ⬜/✅/⚠️  |       |
| Functions      | ⬜/✅/⚠️  |       |
| Comments       | ⬜/✅/⚠️  |       |
| Formatting     | ⬜/✅/⚠️  |       |
| Error Handling | ⬜/✅/⚠️  |       |

### Notable Findings

<List Clean Code improvements with examples>

---

## 5. Defensive Programming

Reference: [Defensive Programming Checklist](../checklists/defensive-programming-checklist.md)

### Assessment

| Category            | Status    |
|---------------------|-----------|
| Input Validation    | ⬜/✅/⚠️  |
| Pointer Safety      | ⬜/✅/⚠️  |
| Resource Management | ⬜/✅/⚠️  |
| Error Handling      | ⬜/✅/⚠️  |

### Risk Areas

<List defensive programming gaps>

---

## 6. Legacy Code / Testability Assessment

Reference: [Legacy Code Checklist](../checklists/legacy-code-checklist.md)

### Testability Score

| Criterion                    | Status    |
|------------------------------|-----------|
| Seams exist for mocking      | ⬜/✅/⚠️  |
| Dependencies mockable        | ⬜/✅/⚠️  |
| Functions callable from test | ⬜/✅/⚠️  |
| State controllable           | ⬜/✅/⚠️  |

### Refactoring Barriers

<List what makes the code hard to test or change>

---

## 7. HIS Metrics Analysis

### Command Used

```powershell
.venv/Scripts/python plugins/embedded-sple/skills/his-metrics/scripts/his_metrics.py <component_path>
```

### Results

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| COMF   |       | > 0.2     |        |
| CYCLO  |       | ≤ 10      |        |
| LEVEL  |       | ≤ 4       |        |
| PARAM  |       | ≤ 5       |        |
| GOTO   |       | = 0       |        |
| STMT   |       | 1-50      |        |

### Functions Exceeding Thresholds

<List functions with metric violations>

---

## 8. Architecture Review

### Component Structure

- **Source files**: X
- **Header files**: X
- **Total lines**: X
- **Public functions**: X
- **Internal functions**: X

### Coupling Assessment

<Analysis of dependencies and coupling>

### Cohesion Assessment

<Analysis of module cohesion>

### Architectural Concerns

<List architectural issues>

---

## 9. Static Analysis Findings

### Polyspace Results

| Category  | Count |
|-----------|-------|
| Red (RTE) | X     |
| Orange    | X     |
| Gray      | X     |

### Unresolved Findings

<List critical Polyspace/QAC findings without justification>

---

## 10. Test Coverage Analysis

### Commands Used

```powershell
# Run unit tests
.\build.ps1 -build -buildKit test -buildType Debug -variant <VARIANT> -target <COMPONENT>_unittests

# Generate coverage report
.\build.ps1 -build -buildKit test -buildType Debug -variant <VARIANT> -target <COMPONENT>_reports
```

### Test Execution

| Metric            | Value |
|-------------------|-------|
| Status            | ✅ Passed / ❌ Failed |
| Test cases        | X passed, Y failed |
| Duration          | X.Xs |

### Coverage Summary

|                   | Exec | Total | Coverage | Target | Status |
|-------------------|------|-------|----------|--------|--------|
| Lines             |      |       |          | ≥ 80%  | ⬜     |
| Functions         |      |       |          | 100%   | ⬜     |
| Branches          |      |       |          | ≥ 70%  | ⬜     |

### Test Files

<!-- List the test files for this component below -->
- test_file_1.cc
- test_file_2.cc

### Untested Functions

<List public functions without test coverage>

### Report Location

`build/<VARIANT>/test/Debug/<COMPONENT>/coverage.json`

---

## Consolidated Findings

### 🔴 Critical (Must Fix)

| # | Finding | Location | Source |
|---|---------|----------|--------|
| 1 |         |          |        |

### 🟠 High Priority (Should Fix)

| # | Finding | Location | Source |
|---|---------|----------|--------|
| 1 |         |          |        |

### 🟡 Medium Priority (Consider Fixing)

| # | Finding | Location | Source |
|---|---------|----------|--------|
| 1 |         |          |        |

### 🟢 Low Priority (Nice to Have)

| # | Finding | Location | Source |
|---|---------|----------|--------|
| 1 |         |          |        |

---

## Recommendations

### Immediate Actions

1. <Action 1>
2. <Action 2>

### Short-term Improvements

1. <Improvement 1>
2. <Improvement 2>

### Long-term Considerations

1. <Consideration 1>
2. <Consideration 2>

---

## Appendix

### Files Analyzed

| File | Lines | Purpose |
|------|-------|---------|
|      |       |         |

---

Generated by c-code-review-comprehensive skill
