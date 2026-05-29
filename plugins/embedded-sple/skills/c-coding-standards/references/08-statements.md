# 08 — Statement Rules (BARR‑C:2018, Chapter 8)

**Purpose:** Reduce defects caused by fragile control flow, unclear conditionals, missing `default` cases, loop “magic numbers,” dangerous jump constructs, and typo‑prone comparisons.
**Use this document when:** reviewing/refactoring `if/else`, `switch`, loops, early exits, error handling, comparisons to constants, and any “clever” statement constructs.

---

## 8.1 Variable Declarations (No Comma Operator in Declarations)

### What to check
- Do not declare multiple variables in one declaration using commas.

### Why it matters
- The pointer marker `*` binds to the declarator, not the base type—multi‑decls are easy to misread and cause bugs.

### Common failure modes
```c
char * x, y;   /* y is NOT a pointer */
uint8_t* p_a, p_b; /* p_b is not a pointer */
```

### Preferred fixes (patterns)
**Before:**
```c
uint8_t* p_a, p_b;
```

**After:**
```c
uint8_t * p_a;
uint8_t   p_b;
```

---

## 8.2 Conditional Statements (if / else if / else)

### What to check

#### A) Shortest clause first (preferred practice)
- Order `if` and `else if` clauses so the shortest (fewest lines) appears first when practical.

#### B) Limit nesting depth (max 2 levels)
- Nested `if…else` should not be deeper than **two levels**.
- Refactor deeper nesting into:
  - helper functions (`static`)
  - `switch` on state/event
  - table-driven logic where appropriate

#### C) No assignments in condition tests
- Do not assign within `if` / `else if` condition expressions.

#### D) `else if` requires a final `else`
- Any `if` with one or more `else if` clauses must end with a final `else` clause.

### Why it matters
- Deep nesting is fragile and hard to review; complexity correlates with maintenance defects.
- Assignment-in-condition is a classic typo trap.
- A final `else` is the conditional equivalent of requiring a `default` case in `switch`: it forces explicit handling of “unexpected” states.

### Common failure modes

**Assignment in condition**
```c
if (p_obj = alloc_object())  /* bug: assignment */
{
    ...
}
```

**Missing final else**
```c
if (STATE_A == state)
{
    ...
}
else if (STATE_B == state)
{
    ...
}
/* no else → unhandled state paths */
```

**Excessive nesting**
```c
if (a)
{
    if (b)
    {
        if (c)
        {
            ...
        }
    }
}
```

### Preferred fixes (patterns)

#### A) Separate assignment and test
```c
p_obj = alloc_object();
if (NULL == p_obj)
{
    return ERR_NO_MEM;
}
```

#### B) Add final else
```c
if (STATE_A == state)
{
    handle_a();
}
else if (STATE_B == state)
{
    handle_b();
}
else
{
    /* WARNING: Unexpected state. */
    handle_unexpected_state(state);
}
```

#### C) Reduce nesting with guard clauses or helpers
```c
if (NULL == p_obj)
{
    return ERR_NULL_PTR;
}

if (!obj_is_valid(p_obj))
{
    return ERR_INVALID;
}

/* Normal path */
process_obj(p_obj);
return ERR_OK;
```

---

## 8.3 Switch Statements

### What to check

#### A) Align `break` with `case`
- Indent `break` to align with its `case` label (not with the case body indentation).

#### B) Always include a `default` block
- Every `switch` must have a `default` case.

#### C) Comment intentional fall-through
- If a `case` intentionally falls through to the next, add a clear comment explaining why no `break` exists.

### Why it matters
- Missing `break` is a frequent defect source.
- `default` prevents unhandled cases when enums change or unexpected values occur.
- Fall-through comments make intent explicit for reviewers and future maintainers.

### Common failure modes

**Missing break**
```c
switch (mode)
{
    case MODE_A:
        do_a();
    case MODE_B:
        do_b();
        break;
    default:
        break;
}
```

**No default**
```c
switch (state)
{
    case ST_IDLE: ...
    case ST_RUN:  ...
}
```

### Preferred fixes (patterns)

**Recommended formatting + break alignment**
```c
switch (err)
{
    case ERR_A:
        handle_a();
    break;

    case ERR_B:
        handle_b();
    break;

    default:
        /* WARNING: Unexpected error code. */
        handle_default(err);
    break;
}
```

**Documented fall-through**
```c
switch (err)
{
    case ERR_B:
        handle_b_preamble();
        /* Also perform the steps for ERR_C. */
    case ERR_C:
        handle_c();
    break;

    default:
        handle_default(err);
    break;
}
```

---

## 8.4 Loops (for / while / do…while)

### What to check

#### A) No magic numbers in loop bounds
- Do not use raw numeric constants as start/end bounds for `for`, `while`, `do…while`.
- Use descriptively named constants or derive bounds from data structures where possible.

#### B) No assignments in controlling expressions (except allowed `for`)
- With the exception of:
  - counter initialization in the first `for` clause
  - counter update in the third `for` clause
  do not assign in loop controlling expressions.

#### C) Infinite loops use `for (;;)`
- Implement intentional infinite loops with `for (;;)`.

#### D) Empty loop bodies must have braces and an explanatory comment
- Any loop with an empty body must be written as a braced empty block and include a comment explaining why it is empty.

### Why it matters
- Magic numbers desynchronize from array sizes and protocol dimensions, causing out-of-bounds and missed processing.
- Assignments in conditions hide side effects and are error-prone.
- `for (;;)` avoids confusing constructs like `while (l)` vs `while (1)` and clearly indicates intent.
- Empty loops are easy to misread as “buggy”; comments clarify intent.

### Common failure modes

**Magic number bounds**
```c
for (int row = 0; row < 100; row++)
{
    ...
}
```

**Assignment in condition**
```c
while ((ch = read_char()) != EOF)
{
    ...
}
```

**Empty loop with no comment**
```c
while (0u != (*p_status & BUSY_MASK))
    ;
```

### Preferred fixes (patterns)

#### A) Named bounds
```c
#define MAX_ROWS  (100u)

for (int row = 0; row < (int)MAX_ROWS; row++)
{
    ...
}
```

Better if the data structure determines bounds:
```c
for (uint16_t idx = 0u; idx < ARRAY_LEN(g_items); idx++)
{
    ...
}
```

#### B) Remove assignments from loop controls
```c
int ch;

ch = read_char();
while (EOF != ch)
{
    process_char(ch);
    ch = read_char();
}
```

#### C) Intentional infinite loop
```c
for (;;)
{
    service_watchdog();
    run_state_machine();
}
```

#### D) Empty loop with braces + comment
```c
while (0u != (*p_status_reg & BUSY_MASK))
{
    /* NOTE: Intentional busy-wait for hardware ready. */
}
```

---

## 8.5 Jumps (goto and Forbidden Library Jumps)

### What to check
- `goto` usage is restricted per earlier guidance:
  - avoid when possible
  - if used, jump only forward within same or enclosing block
  - use only to simplify and clarify (commonly for cleanup)
- Do not use C Standard Library functions:
  - `abort()`, `exit()`, `setjmp()`, `longjmp()`

### Why it matters
- Arbitrary jumps create spaghetti flow and make reasoning/testing harder.
- In embedded firmware, `exit()`/`abort()` may not behave as expected, and `setjmp/longjmp` bypass normal cleanup, creating resource/state hazards.

### Common failure modes
- `goto` used as general control flow between states.
- `exit()` used to “fail fast” rather than returning error codes and entering safe state.

### Preferred fixes (patterns)

#### A) Replace jump-based logic with structured control
- Use `switch`-based state machines or helper functions.

#### B) Cleanup `goto` (rare but acceptable)
```c
int rc = ERR_OK;

p_buf = alloc();
if (NULL == p_buf)
{
    rc = ERR_NO_MEM;
    goto cleanup;
}

p_msg = alloc();
if (NULL == p_msg)
{
    rc = ERR_NO_MEM;
    goto cleanup;
}

/* ... work ... */

cleanup:
free(p_msg);
free(p_buf);
return rc;
```

---

## 8.6 Equivalence Tests (Constant on the Left)

### What to check
- When testing equality of a variable against a constant, put the constant on the **left** side of `==`.

### Why it matters
- If `==` is mistyped as `=`, the compiler will catch assigning to a constant on the left, preventing a classic and expensive bug.

### Common failure modes
```c
if (p_obj == NULL)     /* allowed, but less typo-resistant */
{
    ...
}

if (p_obj = NULL)      /* bug: assignment */
{
    ...
}
```

### Preferred fixes (patterns)
```c
if (NULL == p_obj)
{
    return ERR_NULL_PTR;
}

if (0u == flags)
{
    ...
}
```

---

## Cross‑Cutting Control‑Flow Guidance (High-Value Review Heuristics)

### What to check
- Prefer explicitness over cleverness:
  - no hidden side effects in conditions
  - no comma operator in declarations
  - no fall-through without a comment
- Keep complexity low:
  - split long `if` chains into state-based `switch` or helper functions
  - limit nesting
- Ensure all “unexpected” values are handled:
  - final `else` in `if/else if` chains
  - `default` in switches

### Common “smell” indicators
- `if` blocks nested 3+ levels → refactor
- `switch` without `default` → add default
- loops with raw numeric bounds → replace with named constants or derived bounds
- assignments inside `if/while` → separate assignment and test

---

## Automation & Enforcement (Practical Gates for Chapter 8)

### Recommended “cheap” checks (heuristics)
- Assignment inside `if` condition:
  - search: `if\s*\(.*=[^=]`
- Missing `default` (requires parsing; best via static analysis)
- Magic numbers in loop bounds (requires review; partial detection via lint rules)
- Missing fall-through comments (best via code review or a linter rule)

### Static analysis targets (high value)
- unreachable code / missing returns
- missing `default` / unhandled enum values
- suspicious assignments in conditions
- overly complex functions (cyclomatic complexity thresholds)

---

## Review Checklist (Copy/Paste)

- [ ] No comma operator in declarations; one declaration per line
- [ ] `if/else if` chains: no assignments in conditions; final `else` present
- [ ] Nesting depth ≤ 2 levels (refactor deeper nesting)
- [ ] `switch`: `default` always present; `break` aligned with `case`; fall-through commented
- [ ] Loops: no magic numbers in bounds; no assignments in controlling expressions (except `for` init/increment)
- [ ] Infinite loops use `for (;;)`; empty loops use braces + explanatory comment
- [ ] No `abort/exit/setjmp/longjmp`; `goto` avoided or restricted to forward cleanup pattern
- [ ] Constant on left in equality comparisons to constants (`NULL == p`, `0u == x`)
