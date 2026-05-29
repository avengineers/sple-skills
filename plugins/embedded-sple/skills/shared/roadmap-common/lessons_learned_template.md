# Lessons Learned Template

Use this structure for lessons learned files (e.g., `doc/project_notes/modernization_lessons_learned.md` or `doc/project_notes/test_coverage_lessons_learned.md`).

---

# Lessons Learned

This document captures lessons learned from all improvement efforts. **Consult before starting any step.**

> **Rule**: Every roadmap step MUST read this file before starting and update it after completing.

## Quick Reference

### Do's ✅

- <Short actionable lesson>
- <Short actionable lesson>
- <Short actionable lesson>

### Don'ts ❌

- <What to avoid>
- <What to avoid>
- <What to avoid>

---

## Lessons by Category

> **Note**: Not all categories apply to every roadmap type. Use the categories
> relevant to your domain and skip the rest. Add new categories as needed
> using a two-letter prefix (e.g., `TD-01` for Test Design).

### Test Safety

| ID    | Lesson                                          | Source          |
| ----- | ----------------------------------------------- | --------------- |
| TS-01 | <Lesson about testing>                          | <Component>     |
| TS-02 | <Lesson about testing>                          | <Component>     |

### Test Design & Coverage

| ID    | Lesson                                          | Source          |
| ----- | ----------------------------------------------- | --------------- |
| TD-01 | <Lesson about test design, mocking, BDD>        | <Component>     |
| TD-02 | <Lesson about coverage measurement>             | <Component>     |

### Refactoring Techniques

| ID    | Lesson                                          | Source          |
| ----- | ----------------------------------------------- | --------------- |
| RF-01 | <Lesson about refactoring>                      | <Component>     |
| RF-02 | <Lesson about refactoring>                      | <Component>     |

### Resource Management (RAM/ROM)

| ID    | Lesson                                          | Source          |
| ----- | ----------------------------------------------- | --------------- |
| RM-01 | <Lesson about memory>                           | <Component>     |

### Human Factors

| ID    | Lesson                                          | Source          |
| ----- | ----------------------------------------------- | --------------- |
| HF-01 | <Lesson about stakeholder interaction>          | <Component>     |

### Tool & Process

| ID    | Lesson                                          | Source          |
| ----- | ----------------------------------------------- | --------------- |
| TP-01 | <Lesson about tools/process>                    | <Component>     |

---

## Failed Approaches (What NOT to do)

Document approaches that were tried and failed to prevent repeating mistakes.

### FA-01: <Failed Approach Title>

**Component**: <Component name>
**Date**: YYYY-MM-DD
**Step**: <Step number>

**What was tried**:
<Description of the approach>

**Why it failed**:
<Root cause of failure>

**Better approach**:
<What worked instead or should be tried next time>

---

## Detailed Lessons

### Lesson TS-01: <Title>

**Context**: <When this lesson applies>

**Problem**: <What went wrong or was discovered>

**Solution**: <What works>

**Example**:

```c
// Bad
<code example>

// Good
<code example>
```

**Source**: <Component>, Step <N>, YYYY-MM-DD

---

## Adding New Lessons

When adding a lesson:

1. Assign an ID using the category prefix (TS, TD, RF, RM, HF, TP, FA — or a new two-letter prefix)
2. Add to the quick reference table
3. Add detailed entry if needed
4. Reference the source (component, step, date)

Keep entries **concise** - this file must be scannable quickly.
