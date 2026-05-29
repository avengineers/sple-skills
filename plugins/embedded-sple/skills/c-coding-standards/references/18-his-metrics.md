# 12 — HIS Source Code Metrics Guidance (Thresholds + Refactoring Recipes)

**Purpose:** Keep complexity low and code maintainable by applying HIS thresholds as *design constraints*.
**Use when:** HIS metrics are required (common in automotive), or when code must remain simple/testable.

---

## A) HIS metric limits (recommended thresholds)

### Function-level limits (typical HIS)

Polyspace’s HIS summary lists these recommended upper limits:

- Cyclomatic complexity (VG) **≤ 10**
- Language scope / vocabulary (VOCF) **≤ 4**
- Call levels / nesting (LEVEL) **≤ 4**
- Number of callers (CALLING) **≤ 5**
- Number of callees (CALLS) **≤ 7**
- Function parameters (PARAM) **≤ 5**
- Goto statements (GOTO) **= 0**
- Statements per function (STMT) **≤ 50**
- Number of paths (PATH) **≤ 80**
- Return statements (RETURN) **≤ 1**

A commonly cited HIS “metrics with limits” list matches the same values and also expresses comment density as a ratio > 0.2 and return points 0–1. [3](https://emenda.com/his/)

### File-level comment density (COMF)

- Polyspace notes comment density recommended lower limit **20** (i.e., 20%).
- Other HIS summaries express this as ratio **> 0.2**.

### Project-level recursion

- Polyspace lists project-level recursion metrics with recommended upper limit **0** (no recursion).

---

## B) How to design code to stay within HIS limits (practical recipes)

### 1) Cyclomatic complexity ≤ 10

**Refactor triggers:** long if/else chains, multi-case switches, nested loops. **Refactor patterns:**

- Extract helper functions for cohesive steps
- Replace nested conditionals with guard clauses + early exit (ensure MISRA control-flow rules still satisfied)
- Use tables of function pointers or data-driven dispatch where permitted

### 2) LEVEL ≤ 4 (nesting/call level)

**Refactor triggers:** nested if/while/for inside switch inside loop.
**Refactor patterns:**

- Flatten with guard clauses
- Split into “validate → compute → apply” functions
- Use state machine structure rather than nested branching

### 3) PARAM ≤ 5 (function parameters)

**Refactor triggers:** too many parameters, poor cohesion.
**Refactor patterns:**

- Introduce a configuration struct (`*_cfg_t`) passed by pointer-to-const
- Group related arguments into a single struct
- Provide a builder/init function for config structs

### 4) STMT ≤ 50 (statements per function)

**Refactor triggers:** functions doing multiple responsibilities.
**Refactor patterns:**

- Split responsibilities into private `static` helpers
- Move parsing/validation into dedicated functions

### 5) RETURN ≤ 1 (single return point)

**Design approach:**

- Use a `result` variable + single return at end to stay ≤ 1 return.
- If project allows early returns, keep them minimal and justify; but HIS “RETURN ≤ 1” is a strong refactor hint.

### 6) GOTO = 0

**Design approach:** do not use `goto`.
Use structured cleanup or dedicated helper functions instead.

---

## C) How this agent should review under HIS constraints

When HIS metrics apply:

1) If any function exceeds a limit, flag it as **High** and propose a refactor plan.
2) Prefer minimal diffs, but if the only safe fix is refactoring, propose a staged plan:
   - Stage 1: extract helpers, preserve behavior
   - Stage 2: simplify control flow, reduce nesting/complexity
3) Ensure refactors do not violate MISRA Mandatory rules (if MISRA also applies).

---

## D) Minimal HIS checklist

- [ ] VG ≤ 10
- [ ] LEVEL ≤ 4
- [ ] PARAM ≤ 5
- [ ] STMT ≤ 50
- [ ] PATH ≤ 80
- [ ] RETURN ≤ 1
- [ ] GOTO = 0
- [ ] Comment density ≥ 20% (or >0.2)
- [ ] No recursion (project-level)
