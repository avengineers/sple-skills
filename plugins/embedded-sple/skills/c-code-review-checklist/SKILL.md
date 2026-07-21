---
name: c-code-review-checklist
description: C code review workflow with CHK_Code checklist and BARR-C:2018 compliance. Use when reviewing C source files/components for quality, style, MISRA compliance, Polyspace findings, and defects. Invoke when asked to "review code", "check quality", "code review", "inspect C files", "run checklist", or "review component". This is the standard review for feature branches and PR reviews — use `c-code-review-comprehensive` for deep periodic assessments instead.
---

# C Code Review — Checklist

Systematic code review for C source following company standards and safety requirements.

## Communication Style

Follow the guidelines in [shared communication style](../shared/review-common/communication-style.md).

## Workflow

0. **Collect review context**: Follow [Review Context Workflow](../shared/review-common/review-context-workflow.md) — collect git metadata, populate protocol header, enumerate source files.

1. **Identify files**: Confirm which C files to analyze
2. **Read code**: Examine source and headers
3. **Run static analysis**: Invoke the `static-code-analysis` skill using the `skill` tool. Follow ALL steps of that skill in order, including Step 3 which requires asking the user to trigger Polyspace in VS Code. **PAUSE and wait for user confirmation before continuing to Step 4.**

> ⚠️ **AGENT INSTRUCTION**: Step 3 (static analysis via `static-code-analysis` skill) is **MANDATORY** and must ALWAYS be performed. Do NOT skip it. Do NOT proceed past static analysis without user confirmation that Polyspace has run. The review is incomplete without static analysis results.
>
> 🚫 **BLOCKING — existing IDE diagnostics (`ide-get_diagnostics`) MUST NOT be used without a fresh analysis.** Cached results may be stale and can miss new findings or reference changed code. Use `ask_user` to request a fresh Polyspace run and wait for explicit user confirmation before calling `ide-get_diagnostics`.

4. **Apply checklist**: Work through applicable CHK_Code criteria
5. **Check Barr-C:2018**: compliance to coding guidelines (see skill 'c-coding-standards', use the 11-quick-scan.md and 12-pr-review.md checklists)
6. **Document findings**: Create structured report with severity levels
7. **Recommend fixes**: Provide concrete improvements
8. **Record end time**: Follow the "Recording End Time" section in the [Review Context Workflow](../shared/review-common/review-context-workflow.md).

## Quick Checks

Before full review, verify these common issues:

- No TODO/FIXME markers in production code
- No magic numbers (use symbolic constants)
- All pointers validated before use (!=NULL)
- No divisions without zero-check
- `static`, `volatile`, `const` used appropriately
- `#define`/`enum` values owned by the provider/server module, not redefined by clients/receivers (→ CHK_Code #43)
- No hollow Polyspace justifications (see below)

## Hollow Justification Detection

Polyspace suppression comments (`/* polyspace ... */`) require a meaningful technical rationale. During review, **actively search for and flag justifications that explain nothing**. These undermine the entire deviation process because they suppress findings without documenting *why* the code is safe.

**Grep for `polyspace` comments in reviewed files and check each justification text.**

Red-flag patterns (non-exhaustive — use judgment for similar hollow phrases):

| Pattern | Why it's inadequate |
|---------|---------------------|
| "I know what I do" | Asserts competence, explains nothing about the code |
| "justified" / "approved" | Circular — repeats the act of justifying without content |
| "This needs to be that way" | Describes the status quo, not why it's safe |
| "needed for architectural reasons" | Vague hand-wave — which architecture constraint? |
| "not relevant" / "not applicable" | Dismisses without explaining why the rule doesn't apply here |
| "legacy code" / "historical reasons" | Explains origin, not safety |
| "works in practice" / "tested" | Testing doesn't prove absence of UB; not a valid rationale |
| "no impact" / "no risk" | Claim without evidence |
| "see ticket" / "see Jira" (without ID) | Untraceable reference |
| Single word: "ok", "fine", "checked" | No content at all |

**What a valid justification looks like:**

- "Rule 11.3: Cast from `uint32_t*` to `volatile GPIO_TypeDef*` is required for memory-mapped I/O register access. Address 0x40020000 is guaranteed by hardware datasheet §4.2 to be aligned and valid."
- "Rule 14.3: Condition `if (BUFFER_SIZE > 0)` is always true for current config but protects against future configuration changes where BUFFER_SIZE could be 0."

A valid justification states: (1) what the code does, (2) why it's safe despite the violation, and (3) what guarantees that safety (datasheet, hardware behavior, design constraint).

**Severity**: Flag hollow justifications as **Medium** in the review protocol. They are not immediate bugs, but they represent hidden risk — a suppressed finding with no rationale is a finding nobody can assess anymore.

## Full Review

For comprehensive review, load the complete checklist:

- **[CHK_Code Checklist](references/chk-code-checklist.md)**: Full 43-item company review checklist
- **[Barr-C:2018 Quick Scan](../c-coding-standards/checklists/11-quick-scan.md)**: Fast pass for high-risk patterns
- **[Barr-C:2018 PR Review Checklist](../c-coding-standards/checklists/12-pr-review.md)**: Structured PR review process

## Report Format

Create a review protocol report as defined in **[Review Protocol Template](references/review_protocol_template.md)**.

Follow the [Report Naming Convention](../shared/review-common/report-naming-convention.md). Skill name for filename: `c-code-review-checklist`.

## Definition of Done (DoD)

A code review is considered **complete** when the following criteria are met:

| # | Criterion | Description |
|---|-----------|-------------|
| 0 | **Review Context Collected** | Git metadata (branch, commit hash, author, Jira ticket, branch type) read and filled into protocol header |
| 1 | **All Reviewed Files Listed** | Every individual `.c` and `.h` file that was opened and read is listed by full path in the protocol header |
| 2 | **Static Analysis Reviewed** | Fresh Polyspace analysis triggered by user and confirmed complete; findings retrieved via `ide-get_diagnostics` **after** user confirmation — pre-existing cached results never accepted |
| 3 | **No Red/Critical Findings** | Zero unaddressed Red (RTE) Polyspace findings (see `static-code-analysis` skill) |
| 4 | **MISRA Mandatory Rules** | All mandatory rule violations addressed or formally deviated (see `static-code-analysis` skill) |
| 5 | **CHK_Code Checklist Applied** | All applicable items from the 42-item CHK_Code checklist reviewed — using SCA results for MISRA/RTE-related items |
| 6 | **BARR-C:2018 Compliance** | Quick scan checklist completed, no high-severity violations |
| 7 | **Review Protocol Created** | Findings documented following [Report Naming Convention](../shared/review-common/report-naming-convention.md) — never overwrite an existing report |
| 8 | **Recommendations Provided** | Each finding has actionable fix recommendations |
| 9 | **Review Duration Documented** | Start time, end time, and total duration recorded in the protocol header |

### Static Analysis DoD

Static analysis is **MANDATORY** for every component review. Always invoke the `static-code-analysis` skill in step 3.

- [ ] Polyspace Bug Finder executed locally (or CI results available)
- [ ] All Red (RTE) findings resolved
- [ ] Orange findings reviewed and either:
  - Fixed, or
  - Justified with valid `/* polyspace ... */` comment
- [ ] MISRA mandatory violations resolved
- [ ] MISRA required violations resolved or deviated with documentation
- [ ] Findings stored in `doc/reviews/<component>_polyspace_<YYYYMMDD_HHMMSS>.md`

> **SKILL REFERENCE**: Use the `static-code-analysis` skill for all Polyspace and MISRA checks. That skill owns the complete Static Analysis DoD (options file, Red/Orange findings, MISRA violations, justification comments).

## Project Memory Integration

After completing the code review, document significant findings using the `project-knowledge-base` skill:

- **Bugs or defects found** → `doc/project_notes/bugs.md`
- **Coding standard decisions** → `doc/project_notes/decisions.md`
- **Completed review work** → `doc/project_notes/issues.md`

> **SKILL REFERENCE**: Use the `project-knowledge-base` skill to ensure review findings persist across sessions.
