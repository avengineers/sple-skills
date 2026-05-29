---
name: c-code-review-comprehensive
description: Deep, holistic review of C components — orchestrates architecture, checklist, static analysis, HIS metrics, and test coverage skills, then adds MISRA C:2012, Clean Code, Defensive Programming, and Legacy Code assessments. Use for periodic quality assessments, pre-refactoring analysis, technical debt evaluation, or onboarding to unfamiliar code. Invoke with "comprehensive review", "deep review", "full review", or "quality assessment". For simple bug fixes or PR reviews, use `c-code-review-checklist` instead.
---

# C Code Review — Comprehensive

This skill **orchestrates** a deep-dive review of C components. It delegates specialized work to sub-skills and adds its own assessments for MISRA, Clean Code, Defensive Programming, and Legacy Code.

> **When to use**: Periodic quality assessments, pre-refactoring analysis, technical debt evaluation, or onboarding to unfamiliar code. For feature branches and PR reviews, use `c-code-review-checklist` instead.

## Communication Style

Follow the guidelines in [shared communication style](../shared/review-common/communication-style.md).

## Review Workflow

### Step 0: Collect Review Context

Follow [Review Context Workflow](../shared/review-common/review-context-workflow.md) — collect git metadata, populate protocol header, enumerate source files.

### Step 1: Confirm Review Scope

- Clarify which C component(s) to analyze
- Determine file paths and boundaries
- Identify any specific focus areas requested

> ⚠️ **AGENT INSTRUCTION**: ALL review areas listed below are **MANDATORY**. Perform ALL of them without exception. Do NOT skip any area, do NOT ask the user which areas to perform, do NOT treat any area as optional or not applicable.

All areas must be performed:

- [x] 🔒 **Static Analysis** — delegated to `static-code-analysis` skill
- [x] 🔒 **CHK_Code + BARR-C:2018** — delegated to `c-code-review-checklist` skill
- [x] 🔒 **Architecture Review** — delegated to `c-architecture-review` skill
- [x] 🔒 **HIS Metrics** — delegated to `his-metrics` skill
- [x] 🔒 **Test Coverage** — uses shared [coverage-analysis.md](../shared/test-reports/coverage-analysis.md)
- [x] 🔒 **MISRA C:2012 Compliance** — own checklist (below)
- [x] 🔒 **Clean Code Assessment** — own checklist (below)
- [x] 🔒 **Defensive Programming** — own checklist (below)
- [x] 🔒 **Legacy Code / Testability** — own checklist (below)

### Step 2: Read and Map Code

- Systematically read all source and header files
- Map component structure, interfaces, and dependencies
- Identify entry points and key functions

### Step 3: Delegated Analysis (invoke sub-skills)

Run these sub-skills in this order. Each skill has its own workflow — follow it completely.

**3a. Static Analysis (must run first — results feed all checklists)**

Invoke the `static-code-analysis` skill. This is MANDATORY and BLOCKING:
- The skill will ask the user to trigger Polyspace in VS Code
- **WAIT for explicit user confirmation** before proceeding
- Do NOT use cached `ide-get_diagnostics` results — only fresh analysis

**3b. CHK_Code + BARR-C:2018**

Invoke the `c-code-review-checklist` skill. Skip its Step 0 (context already collected) and Step 3 (static analysis already done — pass results forward). Execute Steps 4-7 (checklist application, BARR-C check, findings, recommendations).

**3c. Architecture Review**

Invoke the `c-architecture-review` skill. Skip its Step 0 (context already collected). Results are embedded in the comprehensive report — do not save a separate architecture report.

**3d. HIS Metrics**

Execute: `.venv/Scripts/python plugins/embedded-sple/skills/his-metrics/scripts/his_metrics.py <component_path>`

**3e. Test Coverage**

Use the shared [Coverage Analysis](../shared/test-reports/coverage-analysis.md) reference:
1. Run report target (runs tests + generates coverage): invoke `build-execution` with buildKit=test, variant=\<VARIANT\>, target=components\_\<path\>\_report
2. Parse `build/<VARIANT>/test/Release_fast/components/<path>/coverage.json` for metrics

### Step 4: Apply Own Checklists

These checklists are owned by this skill and provide assessments beyond what the delegated sub-skills cover:

| Area        | Checklist Location                                                         | Focus                        |
|-------------|----------------------------------------------------------------------------|------------------------------|
| MISRA C     | [checklists/misra-c-checklist.md](checklists/misra-c-checklist.md)         | Safety-critical rules        |
| Clean Code  | [checklists/clean-code-checklist.md](checklists/clean-code-checklist.md)   | Readability, maintainability |
| Defensive   | [checklists/defensive-programming-checklist.md](checklists/defensive-programming-checklist.md) | Robustness, error handling |
| Legacy Code | [checklists/legacy-code-checklist.md](checklists/legacy-code-checklist.md) | Testability, refactoring     |

> **Ownership note**: Coupling, cohesion, and architectural smells are owned by `c-architecture-review` — do not re-analyze them here. If the Legacy Code checklist references coupling/cohesion, cross-reference the architecture results instead of duplicating that analysis.

### Step 5: Document Findings

Use template: [references/review_protocol_comprehensive_template.md](references/review_protocol_comprehensive_template.md)

Follow the [Report Naming Convention](../shared/review-common/report-naming-convention.md). Skill name for filename: `c-code-review-comprehensive`.

Record end time per the [Review Context Workflow](../shared/review-common/review-context-workflow.md).

### Step 6: Summarize and Recommend

- Consolidate findings by severity
- Highlight systemic risks
- Provide actionable recommendations

## Definition of Done (DoD)

A comprehensive review is considered **complete** when the following criteria are met:

| # | Criterion | Description |
|---|-----------|-------------|
| 0 | **Review Context Collected** | Git metadata (branch, commit hash, author, Jira ticket, branch type) read and filled into protocol header |
| 1 | **All Reviewed Files Listed** | Every individual `.c` and `.h` file that was opened and read is listed by full path in the protocol header |
| 2 | **Review Scope Confirmed** | All mandatory areas performed: Static Analysis, CHK_Code, BARR-C, MISRA, Clean Code, Defensive Programming, Legacy Code, HIS Metrics, Architecture, Test Coverage |
| 3 | **Static Analysis Reviewed** | Fresh Polyspace analysis triggered by user and confirmed complete; findings retrieved via `ide-get_diagnostics` **after** user confirmation — pre-existing cached results never accepted |
| 4 | **No Red/Critical Findings** | Zero unaddressed Red (RTE) Polyspace findings |
| 5 | **MISRA Mandatory Rules** | All mandatory rule violations addressed or formally deviated |
| 6 | **CHK_Code Checklist Applied** | All applicable items from the 41-item CHK_Code checklist reviewed — using SCA results for MISRA/RTE-related items |
| 7 | **BARR-C:2018 Compliance** | Quick scan checklist completed, no high-severity violations |
| 8 | **HIS Metrics Calculated** | Metrics script executed, all functions exceeding thresholds documented |
| 9 | **Architecture Reviewed** | `c-architecture-review` skill invoked, coupling/cohesion analyzed |
| 10 | **Test Coverage Analyzed** | Coverage extracted via shared [coverage-analysis.md](../shared/test-reports/coverage-analysis.md), untested functions documented |
| 11 | **Review Protocol Created** | Findings documented following [Report Naming Convention](../shared/review-common/report-naming-convention.md) — never overwrite an existing report |
| 12 | **Recommendations Provided** | Each finding has actionable fix recommendations |
| 13 | **Review Duration Documented** | Start time, end time, and total duration recorded in the protocol header |

## Orchestrated Skills

This skill delegates to the following specialized skills:

| Skill                    | Purpose                                       | Step  |
|--------------------------|-----------------------------------------------|-------|
| `static-code-analysis`   | Run Polyspace locally and analyze findings    | 3a    |
| `c-code-review-checklist`| CHK_Code checklist + BARR-C:2018    | 3b    |
| `c-architecture-review`  | Architecture, coupling, cohesion analysis     | 3c    |
| `his-metrics`            | HIS metrics calculation                       | 3d    |
| Shared reference           | [coverage-analysis.md](../shared/test-reports/coverage-analysis.md) | 3e    |
| `c-coding-standards`     | BARR-C:2018 coding standards (via checklist)  | 3b    |

## Standards and Methodologies

| Standard                                 | Focus                                                 |
|------------------------------------------|-------------------------------------------------------|
| **BARR-C:2018**                          | Embedded C coding standard (Michael Barr)             |
| **MISRA C:2012 + Amendment 2**           | Safety-critical C rules                               |
| **HIS Metrics**                          | Herstellerinitiative Software maintainability metrics |
| **Clean Code**                           | Readability principles (Robert C. Martin)             |
| **Defensive Programming**                | Robustness and error handling                         |
| **Cyclomatic Complexity**                | McCabe complexity measurement                         |
| **Working Effectively with Legacy Code** | Testability (Michael Feathers)                        |

## Severity Levels

| Level           | Description                                        | Action                  |
|-----------------|----------------------------------------------------|-------------------------|
| 🔴 **Critical** | Safety issue, security vulnerability, definite bug | Must fix before release |
| 🟠 **High**     | Likely bug, standard violation, high risk          | Should fix              |
| 🟡 **Medium**   | Code smell, maintainability issue                  | Consider fixing         |
| 🟢 **Low**      | Style issue, minor improvement                     | Nice to have            |

## Project Memory Integration

After completing the comprehensive review, document significant findings using the `project-knowledge-base` skill:

- **Bugs or defects found** → `doc/project_notes/bugs.md`
- **Architectural decisions** → `doc/project_notes/decisions.md` (as ADRs)
- **Coding standard decisions** → `doc/project_notes/decisions.md`
- **Completed review work** → `doc/project_notes/issues.md`

> **SKILL REFERENCE**: Use the `project-knowledge-base` skill to ensure review findings persist across sessions.

## Usage Examples

```text
"Perform a comprehensive review of components/light_controller/"
"Deep review of auto_off including architecture and testability"
"Quality assessment of this component with all checklists"
"Analyze maintainability and technical debt in components/vsm/"
```
