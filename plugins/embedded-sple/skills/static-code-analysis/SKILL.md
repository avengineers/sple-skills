---
name: static-code-analysis
description: Run static analysis tools (Polyspace As You Code, Cppcheck) on C components and analyze findings. Use when running static analysis, reviewing findings, checking MISRA compliance, or evaluating runtime error detections. Invoke with "run static analysis", "run Polyspace", "run cppcheck", "check MISRA", "static analysis", or "analyze findings".
---

# Static Code Analysis Skill

Orchestrates static analysis for C components using one or more tools.
Supports **Polyspace As You Code** (MISRA, RTE detection) and **Cppcheck** (general defect detection).

## Agent Workflow

### Step 1: Identify Component Under Analysis

Determine the target component path (e.g., `components/light_controller/`).
If not provided by user, ask:

> Which component should I analyze? (e.g., `components/<component_name>/`)

### Step 2: Tool Selection

**Auto-detect recommendation:** Before asking the user, search for a `static_analysis.json` file in the variant directory (typical path: `variants/<Platform>/<Product>/static_analysis.json`). If found, read the `"tool"` field and use it as the recommended default.

Present the recommendation with the option to override:

> Based on `static_analysis.json`, the configured tool for this variant is **{detected_tool}**.
> Should I proceed with **{detected_tool}**, or would you prefer a different tool?
> 1. **Polyspace** — MISRA compliance + runtime error proofs (requires VS Code extension)
> 2. **Cppcheck** — General defect detection (null pointers, leaks, style)
> 3. **Both** — Run both tools and merge findings

If no `static_analysis.json` is found, fall back to asking without a recommendation:

> Which static analysis tool(s) should I run?
> 1. **Polyspace** — MISRA compliance + runtime error proofs (requires VS Code extension)
> 2. **Cppcheck** — General defect detection (null pointers, leaks, style)
> 3. **Both** — Run both tools and merge findings

Record the selection and proceed to Step 3.

### Step 3: Execute Tool-Specific Workflow

Based on the selection in Step 2, load and follow the corresponding reference:

| Selection | Reference | Notes |
|-----------|-----------|-------|
| Polyspace | `references/polyspace-payc.md` | Contains a **blocking step** — user must trigger analysis in VS Code |
| Cppcheck | `references/cppcheck.md` | Method B (VS Code Extension) is unvalidated — prefer Method A (CLI) or C (SPL Extension) |
| Both | Execute Polyspace first, then Cppcheck | Polyspace blocking step applies |

> **IMPORTANT**: Follow ALL steps in the tool-specific reference(s) in order.
> For Polyspace, Step P3 is a blocking gate — do NOT proceed until user confirms.

### Step 4: Categorize and Report Findings

Categorize all findings using the severity mapping and reporting template in `references/unified-severity-model.md`.

**If both tools were run**: merge findings, deduplicate same-location issues, and attribute each finding to its source tool.

### Step 5: Provide Recommendations

1. **For Critical findings**: Suggest concrete code fixes — these are definite bugs
2. **For Warning findings**: Either fix the code or provide a justification/suppression template appropriate to the tool
3. **For unjustified MISRA violations** (Polyspace): Provide polyspace justification comment template
4. **For questionable existing justifications/suppressions**: Flag for review

### Step 6: Project Memory Integration

After completing static analysis, document significant findings using the `project-knowledge-base` skill:

- **Definite bugs (Critical findings)** → `doc/project_notes/bugs.md`
- **MISRA deviation decisions** → `doc/project_notes/decisions.md`

## Usage Examples

```text
"Run static analysis on light_controller component"
"Run Polyspace on components/light_controller/"
"Run cppcheck on this component"
"Check MISRA compliance of this component"
"Run both Polyspace and cppcheck, then merge findings"
"Review polyspace comments in this file"
```

## Tool References

- `references/polyspace-payc.md` — Full Polyspace PAYC workflow (prerequisites, steps, MISRA tables, check codes, justification examples)
- `references/cppcheck.md` — Cppcheck workflow (draft — prerequisites, invocation, check IDs, suppression format)
- `references/unified-severity-model.md` — Severity mapping across tools and reporting template

> **SKILL REFERENCE**: Use the `project-knowledge-base` skill to ensure static analysis findings persist across sessions.

## Agent Actions Summary

1. **Verify** options file exists (`build/sca_ps_payc_options_file.txt`)
2. **Search** existing polyspace justification comments in source files
3. **Request** user to run Polyspace analysis (requires UI context)
4. **Retrieve** findings using `get_errors` tool after analysis
5. **Evaluate** justification validity and completeness
6. **Recommend** fixes or proper justifications for findings
