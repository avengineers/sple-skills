# Report Naming Convention

Shared naming and save rules for all C code review reports.

## File Naming Pattern

```
doc/reviews/<component>_<skill-name>_<JIRA-ID>_<YYYYMMDD_HHMMSS>.md
```

- `<component>`: Name of the reviewed component (e.g. `StateMgr`, `auto_off`)
- `<skill-name>`: Name of the skill that produced the report (e.g. `c-architecture-review`, `c-code-review-checklist`, `c-code-review-comprehensive`)
- `<JIRA-ID>`: Jira ticket from branch name (e.g. `PROJ-123`). If no Jira ticket is found, **omit this segment entirely**
- `<YYYYMMDD_HHMMSS>`: Timestamp in 24-hour format (e.g. `20260428_133045`)

### Examples

With Jira ticket:
```
doc/reviews/StateMgr_c-code-review-checklist_PROJ-123_20260428_133045.md
```

Without Jira ticket:
```
doc/reviews/StateMgr_c-code-review-checklist_20260428_133045.md
```

## Overwrite Protection

> ⚠️ **AGENT INSTRUCTION — NEVER OVERWRITE AN EXISTING REPORT**

Before saving, **always check** if the target file already exists:

```powershell
Test-Path "doc/reviews/<target_filename>.md"
```

- If the file does **not** exist → save with the base name.
- If the file **already exists** → append a numeric suffix: `_2`, `_3`, … until a free name is found.
  Example sequence: `StateMgr_c-code-review-checklist_PROJ-123_20260428.md` → `…_2.md` → `…_3.md`

**Do NOT use `create` on an existing path. Do NOT overwrite or modify a previous review report.**
