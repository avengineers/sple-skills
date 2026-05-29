# 06 — Procedure Rules (BARR‑C:2018, Chapter 6)

**Purpose:** Make functions and callable interfaces easy to review, hard to misuse, and less defect‑prone by enforcing consistent naming, limiting complexity, avoiding dangerous macros, and handling concurrency entry points (threads/ISRs) with clear conventions.
**Use this document when:** adding/refactoring functions, reviewing API naming, introducing macros, implementing RTOS tasks/threads, or writing interrupt service routines.

---

## 6.1 Procedure Naming Conventions

### What to check
- **No reserved/keyword names:** Procedure names must not match keywords from C or C++ (or common extensions).
- **No C Standard Library collisions:** Avoid naming overlaps with library functions (e.g., `memset`, `strlen`, `atoi`).
- **No leading underscore:** Procedure names must not begin with `_`.
- **Length limit:** Procedure names should be **≤ 31 characters**.
- **Lowercase only:** Function names contain **no uppercase letters**.
- **Macro names contain no lowercase letters.**
- **Word separation:** Use underscores to separate words.
- **Verb-first semantics:** Names should describe actions (verbs) or questions they answer.
- **Public API prefix:** Public functions should be prefixed with `<module>_`.

### Why it matters
- Prevents collisions with toolchain/library identifiers and avoids undefined behavior around reserved namespaces.
- Improves readability and makes public APIs discoverable.
- Short, consistent names reduce maintenance mistakes (some toolchains historically distinguish only prefix portions).

### Common failure modes
- Naming a function `printf()` or `memcpy()` by accident or by convenience.
- Mixed casing (`Uart_Init`) causing inconsistent calling patterns and search misses.
- “Utility” functions with vague names (`do_it`, `process`) that hide intent.

### Preferred fixes (patterns)

**Good public API naming**
```c
/* uart.h */
int uart_init (void);
int uart_tx   (uint8_t const * const p_buf, uint16_t n_bytes);
```

**Good “question” predicate naming**
```c
bool uart_is_tx_ready (void);
```

**Macro naming**
```c
#define UART_TX_MAX_BYTES  (256u)
```

---

## 6.2 Functions (Size, Structure, Prototypes, and `static`)

### What to check

#### A) Function length and reviewability
- Keep functions roughly **≤ 100 lines** where practical.
- Prefer “one printed page” per function for review.

#### B) Function boundaries and exits
- Preferred practice: **single exit point** with `return` at the bottom.
- Multiple returns are acceptable when they **clearly improve readability** (e.g., quick argument validation), but do not overuse.

#### C) Prototypes and visibility
- Every **public function** has a prototype in the corresponding header.
- Every **private function** is declared `static` in the `.c`.
- Parameters are explicitly declared and meaningfully named.

### Why it matters
- Smaller functions are easier to test and review; reviewers catch defects at function granularity.
- Prototypes in headers + including the module header in its `.c` ensures compiler checks match prototype and definition.
- `static` limits visibility and reduces coupling between modules.

### Common failure modes
- Large “god functions” that contain multiple responsibilities and deep nesting.
- Private helpers accidentally exported (missing `static`) and later used externally.
- Parameter names like `a`, `b`, `x1` that hide semantics and cause misuse.
- Public function defined but not declared (or mismatched signature vs header).

### Preferred fixes (patterns)

#### A) Reduce length by extracting `static` helpers
```c
static int validate_config (cfg_t const * const p_cfg);
static void apply_config   (cfg_t const * const p_cfg);

int module_configure (cfg_t const * const p_cfg)
{
    int rc = ERR_OK;

    rc = validate_config(p_cfg);
    if (ERR_OK == rc)
    {
        apply_config(p_cfg);
    }

    return rc;
}
```

#### B) Controlled early returns (argument validation)
```c
int uart_tx (uint8_t const * const p_buf, uint16_t n_bytes)
{
    if ((NULL == p_buf) || (0u == n_bytes))
    {
        return ERR_INVALID_ARG;
    }

    /* ... normal processing ... */

    return ERR_OK;
}
```

#### C) Prototype hygiene
- In `.h`:
```c
int uart_tx (uint8_t const * const p_buf, uint16_t n_bytes);
```
- In `.c`:
```c
#include "uart.h"   /* ensures prototype match */
```

---

## 6.3 Function‑Like Macros (Avoid; If Unavoidable, Make Them Safe)

### What to check
- **Do not use parameterized macros** if a function (or `inline` function) can accomplish the same behavior.
- If parameterized macros are used, enforce:
  1. Entire macro body surrounded by parentheses.
  2. Every parameter use surrounded by parentheses.
  3. Each parameter used **no more than once** (avoid side effects).
  4. Never include control transfer (e.g., `return`, `break`, `goto`).

### Why it matters
- Macros can evaluate arguments multiple times, causing side effects like double increments.
- Macros are invisible at runtime (hard to step into/debug).
- Macros bypass type checking and can silently introduce signed/unsigned or float comparison issues.

### Common failure modes
- Double evaluation:
```c
#define MAX(A, B)  ((A) > (B) ? (A) : (B))
x = MAX(i++, j++); /* increments twice in some paths */
```

- Missing parentheses leading to precedence bugs:
```c
#define SCALE(x)  x * 10u
y = SCALE(a + b); /* expands to a + b * 10u */
```

### Preferred fixes (patterns)

#### A) Use `static inline` instead of macros
```c
static inline uint32_t max_u32 (uint32_t a, uint32_t b)
{
    return (a > b) ? a : b;
}
```

#### B) If a macro is unavoidable (rare), guard it heavily
```c
#define CLAMP_U16(V, LO, HI) \
    (((V) < (LO)) ? (LO) : (((V) > (HI)) ? (HI) : (V)))
```

**And** avoid passing expressions with side effects:
```c
val = CLAMP_U16(val, lo, hi); /* ok */
```

---

## 6.4 Threads of Execution (Tasks/Processes Naming)

### What to check
- Entry functions that encapsulate threads/tasks/processes end with:
  - `_thread` or `_task` or `_process`

### Why it matters
- Makes concurrency entry points easy to identify during review and debugging.
- Helps maintainers understand which functions run “forever” and are asynchronous.

### Common failure modes
- Task functions named like ordinary helpers, hiding that they run in infinite loops.
- RTOS entry functions doing heavy initialization with unclear lifecycle.

### Preferred fixes (patterns)

**Task entry function skeleton**
```c
void alarm_thread (void * p_data)
{
    (void)p_data;

    for (;;)
    {
        /* Wait for signal/message */
        /* Process event */
    }
}
```

**Notes**
- Prefer `for (;;)` for infinite loops.
- Keep per‑iteration work bounded; avoid unbounded blocking without design rationale.

---

## 6.5 Interrupt Service Routines (ISRs)

### What to check

#### A) ISR declaration is platform‑correct
- The compiler must be informed a function is an ISR (pragma/attribute/keyword per toolchain).
- ISR name ends with `_isr`.

#### B) Prevent accidental calls
- ISR should be declared `static` and/or positioned/linked such that it cannot be called like a normal function (subject to platform needs).

#### C) Stub/default handlers exist
- Unused/unexpected interrupt vectors should point to a safe default handler that:
  - disables/reports the interrupt if possible
  - asserts/logs
  - prevents silent undefined behavior

#### D) ISR body stays minimal and deterministic
- Do not block in an ISR.
- Do not call APIs that can block or depend on scheduler timing unless explicitly ISR‑safe.
- Acknowledge/clear the interrupt source appropriately.
- Shared data rules:
  - Use `volatile` for shared variables touched in ISR and foreground.
  - Ensure atomicity (critical sections in foreground when required).

### Why it matters
- ISRs are asynchronous extensions of hardware; incorrect handling corrupts state, causes races, and can wedge the system.
- Accidental direct calls to ISR functions can corrupt stack/CPU context depending on ABI.

### Common failure modes
- Doing “too much” work in ISR (complex parsing, memory allocation, logging).
- Missing `volatile` on ISR‑shared flags leading to optimization bugs.
- Failing to clear interrupt flags, causing interrupt storms.
- Foreground reads multi‑byte values that ISR updates, leading to torn reads.

### Preferred fixes (patterns)

#### A) Minimal ISR + deferred processing
```c
static volatile uint8_t g_rx_ready = 0u;

ISR_ATTR static void uart_rx_isr (void)
{
    /* Read/clear HW source first (platform specific) */
    g_rx_ready = 1u;

    /* Acknowledge interrupt at hardware */
}
```

Foreground processing:
```c
void uart_poll (void)
{
    if (0u != g_rx_ready)
    {
        enter_critical();
        g_rx_ready = 0u;
        exit_critical();

        process_rx();
    }
}
```

#### B) Default handler stub
```c
ISR_ATTR static void default_isr (void)
{
    /* WARNING: Unexpected interrupt. Investigate vector table configuration. */
    assert(false);
    for (;;)
    {
        /* Halt */
    }
}
```

#### C) Document critical assumptions
```c
/* NOTE: This ISR assumes the UART status register is write-1-to-clear. */
*p_uart_status = UART_INT_CLR_MASK;
```

---

## Cross‑Cutting Guidance: Error Handling and Cleanup Patterns

### What to check
- Avoid `goto` generally, but if used for cleanup, ensure it:
  - jumps forward only
  - is local to function scope
  - improves clarity (single cleanup block)
- Avoid complex multi‑exit paths unless they simplify the function.

### Preferred cleanup pattern (when needed)
```c
int rc = ERR_OK;

p_buf = alloc();
if (NULL == p_buf)
{
    rc = ERR_NO_MEM;
    goto cleanup;
}

/* ... work ... */

cleanup:
free(p_buf);
return rc;
```

---

## Automation & Enforcement (Practical Gates for Chapter 6)

### Recommended “cheap” checks
- Flag uppercase letters in function names (heuristic): review + naming conventions
- Flag parameterized macros: search for `#define\s+\w+\s*\(`
- Flag missing `static` on private functions (requires tooling/context)
- Flag functions longer than 100 lines (simple script / linter)
- Flag ISR naming violations: search for `_isr` and verify attributes/placement

### Static analysis targets (high value)
- Inconsistent prototypes between header and source
- Non‑static functions not declared in headers
- Macro side effects and double evaluations
- ISR‑unsafe calls inside interrupt context (rule sets vary by platform)

---

## Review Checklist (Copy/Paste)

- [ ] Function names: lowercase_with_underscores, ≤31 chars, no leading underscore
- [ ] No collisions with C/C++ keywords or standard library function names
- [ ] Public functions prefixed with module name; prototypes in the module header
- [ ] Private helpers are `static` and not exposed
- [ ] Functions are small/reviewable (≈≤100 lines) and not deeply nested
- [ ] Exit strategy is consistent; early returns used only to improve clarity
- [ ] Parameterized macros avoided; use `static inline` functions instead
- [ ] Task entry points end with `_thread/_task/_process` and use `for (;;)`
- [ ] ISRs: platform-marked, named `_isr`, minimal, acknowledge/clear HW, safe default handlers exist
- [ ] ISR/shared data uses `volatile` and foreground protects multi‑byte or non‑atomic accesses
