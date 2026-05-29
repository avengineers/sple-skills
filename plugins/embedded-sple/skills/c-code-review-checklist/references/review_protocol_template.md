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

# Code Review Report

## Executive Summary

### Overall Assessment: **<PASS / PASS WITH IMPROVEMENTS / NEEDS WORK / FAIL>**

<Brief 2-3 sentence summary of overall code quality and key findings>

**Strengths:**

- ✅ <strength 1>
- ✅ <strength 2>

**Areas for Improvement:**

- ⚠️ <area 1>
- ⚠️ <area 2>

## Static Analysis Results (Polyspace / PAYC)

### Summary

| Category          | Count |
|-------------------|-------|
| Red (RTE)         |       |
| Orange            |       |
| Gray              |       |
| MISRA Violations  |       |

### Unresolved Findings

| # | Rule / Category | Location | Status |
|---|----------------|----------|--------|
| 1 |                |          |        |

---

## CHK_Code Checklist Results

### CHK #01: Pull request has minimum approvals (at least 1 senior engineer)

- **Status:** ✅ Passed
- **File:** filename.c, Line: XXX
- **Rationale:** The pull request received approvals from senior engineers as required.
- **Recommendation:** No action needed.

### CHK #03: Templates used (organization .c/.h templates, standard type headers)

- **Status:** ⚠️ Failed
- **File:** filename.c, Line: XXX
- **Rationale:** The pull request received approvals from senior engineers as required.
- **Recommendation:** No action needed.

### for all CHK elements

### Summary

| Metric           | Count                    |
| ---------------- | ------------------------ |
| Checks performed | X/41                     |
| Passed           | X                        |
| Failed           | X                        |
| **Assessment**   | PASS / NEEDS WORK / FAIL |

## Barr-C:2018: Quick Scan Results

- add the quick scan results here -

## Barr-C:2018 PR Review Results

- add the PR review results here -

## 💡 Recommendations

- list of recommendation for rework by priority.
