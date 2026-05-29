---
name: c-coding-standards
description: Use when writing, reviewing, refactoring, or formatting Embedded C code. Applies BARR-C:2018 bug-reducing rules with prioritized findings and minimal diffs. Defines MISRA and HIS metrics best practices. Invoke when asking about C coding standards, naming conventions, formatting rules, BARR-C compliance, code style, or variable naming.
---

# Embedded C (BARR-C:2018) Reviewer & Coach

## Mission

Reduce defects and improve portability/maintainability in Embedded C (C99) by applying
Barr Group’s BARR-C:2018 rule set. Use enforceable, review-friendly recommendations.
(See BARR-C structure: General, Comments, White Space, Modules, Data Types, Procedures,
Variables, Statements.)

## How to use references (progressive disclosure)

Only load the topic docs you need for the current task:

- General rules & core bug traps → `references/01-general.md`
- Commenting standards & Doxygen style → `references/02-comments.md`
- Formatting/spacing/indent rules → `references/03-whitespace.md`
- Headers, includes, module boundaries → `references/04-modules.md`
- Fixed-width types, signed/unsigned, structs, floats, bool → `references/05-data-types.md`
- Functions, macros, tasks/threads, ISRs → `references/06-procedures.md`
- Variable naming, init, globals/pointers/booleans → `references/07-variables.md`
- Conditionals, switch, loops, jumps, comparisons → `references/08-statements.md`
- Deviation process & templates → `references/09-deviations.md`
- Tooling + grep/static analysis hooks → `references/10-automation.md`
- MISRA C:2012 mandatory-by-design guidance → `references/17-misra-mandatory.md`
- HIS source code metrics guidance & thresholds → `references/18-his-metrics.md`

Examples (load as needed):

- ISR/concurrency patterns → `examples/14-isr-and-concurrency.md`
- MMIO register mapping patterns → `examples/15-mmio-register-maps.md`
- Macro do/don’t patterns → `examples/16-macros.md`

Checklists (load for reviews):

- Fast scan → `checklists/11-quick-scan.md`
- PR review checklist → `checklists/12-pr-review.md`
- Safety/portability deep dive → `checklists/13-safety-portability.md`

## Default output format

1) Executive summary (conformance + top risks)
2) Findings (severity, BARR-C section ref, location, evidence, why, fix)
3) Suggested patch (minimal diff)
4) Deviations (only if necessary, local comment + rationale)
5) Automation hooks (prevent recurrence)

## Linter bundle (install-on-demand)

If the user asks to "set up linting", "add linter config", "run clang-tidy", or "add CI lint step":

1) Load `references/10-automation.md` and `resources/lint/.../README.md`.
2) Offer two modes:
   - **Clang-Tidy mode** (preferred): copy `resources/lint/clang-tidy/.clang-tidy` to repo root and
     copy scripts to `tools/` (or `scripts/`).
   - **GCC analyzer mode** (optional): copy `resources/lint/gcc-analyzer/*` similarly.

3) Do not run scripts automatically. Provide commands for the user/CI to run.
4) Explain that clang-tidy expects `compile_commands.json` and that `-p <build-dir>` points to it.

## Static Code Analysis tools

This skill assumes the project uses **Cppcheck** and **Polyspace** for coding rule checks and metrics.
Refer to a build system skill to invoke static analysis tools to verify your code.
Instead:

1) Write and review code so that it will pass Cppcheck/Polyspace checks on the first run.
2) When asked to fix findings, propose minimal diffs that directly resolve the rule/metric violation.

## MISRA C:2012 Mandatory guidelines — consider from the beginning

When the user states MISRA compliance is required, treat all **Mandatory** guidelines as non-negotiable:

- deviation from mandatory guidelines is not permitted.

### Mandatory-by-design workflow (what the agent must do)

When authoring or reviewing code under MISRA:

1) Proactively apply “mandatory catches” while writing (not after the fact).
2) Use explicit, conservative constructs that reduce undefined/unspecified behavior risk.
3) Assume the static analysis tool is part of the compliance story; MISRA expects tool configuration and process.
4) If a violation appears “unavoidable”, stop and redesign (mandatory rules cannot be deviated).

### Minimal mandatory focus list (high-frequency traps)

Always be extra vigilant about:

- Rule 9.1: no read of uninitialized automatic objects.
- Rule 12.5: avoid `sizeof` on array-typed function parameters.
- Rule 13.6: `sizeof` operand must not have side effects.
- Rule 17.4: all exit paths of non-void functions return a value.
- Rule 17.6 (C99): no `static` in array parameter declarators.

Load `references/17-misra-mandatory.md` for detailed “how to write it right” guidance.

## HIS Source Code Metrics — apply as design constraints

When HIS metrics are required, treat them as design constraints and refactor triggers.
HIS provides recommended upper limits for function-level metrics.

### How the agent must respond under HIS constraints

When writing/refactoring:

1) Keep functions small and cohesive; split before exceeding thresholds.
2) Reduce nesting via guard clauses + helper functions (but keep MISRA control-flow rules in mind).
3) Avoid `goto` entirely (HIS expects 0).
4) Prefer a single return point when feasible (HIS return ≤ 1).

Load `references/18-his-metrics.md` for thresholds + refactoring recipes.

## Project Memory Integration

After applying BARR-C fixes or making coding standard decisions, use the `project-knowledge-base` skill to document:

- **Coding standard or MISRA deviation decisions** → `doc/project_notes/decisions.md`
- **Recurring bug patterns avoided** → `doc/project_notes/bugs.md`

> **SKILL REFERENCE**: Use the `project-knowledge-base` skill to ensure decisions persist across sessions.
