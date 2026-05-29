# Unified Severity Model

Maps tool-specific severity levels into a common model used for the unified reporting step.

## Severity Mapping

| Unified Level | Polyspace | Cppcheck | Action Required |
|---------------|-----------|----------|-----------------|
| **Critical** | Red (RTE — definite runtime error) | `error` | Must fix before merge |
| **Warning** | Orange (potential issue) | `warning`, `portability` | Review and fix or justify |
| **Style** | — | `style`, `performance` | Consider fixing; low priority |
| **Info** | Gray (unreachable code) | `information` | Verify intent; may indicate dead code |
| **Safe** | Green (proven safe) | — | No action needed |

## MISRA Violations (Polyspace-specific)

MISRA findings use their own priority model regardless of Polyspace color:

| MISRA Level | Unified Level | Action |
|-------------|---------------|--------|
| Mandatory | **Critical** | Always fix — no deviation allowed |
| Required | **Warning** | Fix or formally document deviation |
| Advisory | **Style** | Consider fixing where practical |

## Reporting Template

When presenting findings to the user, group by unified severity:

```markdown
### 🔴 Critical (N findings)
| # | Tool | Check | File | Line | Description |
|---|------|-------|------|------|-------------|

### 🟠 Warning (N findings)
| # | Tool | Check | File | Line | Description |
|---|------|-------|------|------|-------------|

### 🔵 Style (N findings)
| # | Tool | Check | File | Line | Description |
|---|------|-------|------|------|-------------|

### ℹ️ Info (N findings)
| # | Tool | Check | File | Line | Description |
|---|------|-------|------|------|-------------|
```

## Rules for Merged Reports

1. **Deduplicate**: If both tools flag the same location for the same issue (e.g., null pointer), report once and note both tools found it.
2. **Highest severity wins**: If tools disagree on severity for the same finding, use the higher unified level.
3. **Tool attribution**: Always show which tool produced each finding so the user knows where to apply suppressions/justifications.
4. **Actionable recommendations**: For Critical and Warning findings, always provide a concrete fix suggestion or justification template.
