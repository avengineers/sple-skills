---
name: his-metrics
description: Calculate and evaluate HIS (Herstellerinitiative Software) metrics for C components. Use when assessing maintainability, complexity, or code quality metrics. Invoke with "calculate HIS metrics", "check maintainability", "HIS analysis", or "code metrics".
---

# HIS Metrics Skill

This skill calculates and evaluates HIS (Herstellerinitiative Software) metrics for embedded C code.
HIS metrics provide quantitative measures of code quality, complexity, and maintainability.

## Available Metrics

| Metric           | Name                          | Threshold | Description                                 |
|------------------|-------------------------------|-----------|---------------------------------------------|
| **COMF**         | Comment Frequency             | > 0.2     | Ratio of comment lines to code lines        |
| **PATH**         | Number of Paths               | ≤ 80      | Estimated number of execution paths         |
| **GOTO**         | GOTO Statements               | = 0       | Count of goto statements                    |
| **CYCLO** (v(G)) | Cyclomatic Complexity         | ≤ 10      | McCabe complexity measure                   |
| **CALLING**      | Calling Functions             | ≤ 5       | Number of functions calling this function   |
| **CALLS**        | Called Functions              | ≤ 7       | Number of functions called by this function |
| **PARAM**        | Parameters                    | ≤ 5       | Number of function parameters               |
| **STMT**         | Statements                    | 1-50      | Number of statements per function           |
| **LEVEL**        | Nesting Level                 | ≤ 4       | Maximum nesting depth                       |
| **RETURN**       | Return Points                 | 0 or 1    | Number of return statements                 |
| **AP_CG_CYCLE**  | Call Graph Cycles             | = 0       | Cycles in call graph (recursion)            |
| **VOCF**         | Vocabulary Frequency          | ≤ 4       | Halstead vocabulary metric                  |
| **NOMV**         | Modified Global Variables     | = 0       | Global variables modified                   |
| **NOMVPR**       | Modified Globals per Function | = 0       | Globals modified per function               |

## Workflow

1. **Identify target files**: Determine which C files to analyze
2. **Run HIS metrics script**: Execute `plugins/embedded-sple/skills/his-metrics/scripts/his_metrics.py`
3. **Evaluate thresholds**: Compare results against HIS thresholds
4. **Identify violations**: List metrics exceeding thresholds
5. **Provide recommendations**: Suggest refactoring for violations

## Usage

### Command Line

```powershell
# Use the repo's virtual environment
.venv/Scripts/python plugins/embedded-sple/skills/his-metrics/scripts/his_metrics.py components/light_controller/src/light_controller.c
.venv/Scripts/python plugins/embedded-sple/skills/his-metrics/scripts/his_metrics.py components/light_controller/  # entire directory
```

### In Reviews

```text
"Calculate HIS metrics for auto_off.c"
"Evaluate maintainability of this component using HIS metrics"
"Check cyclomatic complexity of all functions"
```

## Output Format

```markdown
## HIS Metrics Report

### File: StateMgr.c

| Metric | Value | Threshold | Status  |
|--------|-------|-----------|---------|
| COMF   | 0.25  | > 0.2     | ✅ OK   |
| CYCLO  | 15    | ≤ 10      | ❌ FAIL |
| LEVEL  | 6     | ≤ 4       | ❌ FAIL |
| PARAM  | 3     | ≤ 5       | ✅ OK   |
| ...    | ...   | ...       | ...     |

### Violations Summary

1. **CYCLO (15 > 10)**: Function `process_message()` has high complexity
   - **Recommendation**: Split into smaller functions, extract conditionals

2. **LEVEL (6 > 4)**: Deep nesting in `validate_input()`
   - **Recommendation**: Use early returns, extract nested blocks
```

## Threshold Justification

The HIS thresholds are industry-standard values established by German automotive OEMs:

- **CYCLO ≤ 10**: Functions above this are hard to test and maintain
- **LEVEL ≤ 4**: Deep nesting indicates overly complex logic
- **GOTO = 0**: Goto statements create unstructured control flow
- **PARAM ≤ 5**: Too many parameters indicate poor function design

## Project Memory Integration

After completing HIS metrics analysis, document significant findings using the `project-knowledge-base` skill:

- **Refactoring decisions triggered by metric violations** → `doc/project_notes/decisions.md`
- **Recurring complexity hotspots** → `doc/project_notes/bugs.md`

> **SKILL REFERENCE**: Use the `project-knowledge-base` skill to ensure metric findings persist across sessions.

## Related Scripts

- `plugins/embedded-sple/skills/his-metrics/scripts/his_metrics.py` - Main HIS metrics calculator

## Environment

Always use the repository's virtual environment:

```powershell
.venv/Scripts/python <script>   # Windows
.venv/bin/python <script>       # Linux/macOS
```
