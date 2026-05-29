
# 01 — General Rules (BARR‑C:2018, Chapter 1)

**Purpose:** Apply the highest‑leverage “general” rules from BARR‑C:2018 to prevent common embedded firmware defects and improve portability/readability.
**Use this document when:** writing/refactoring control flow, reviewing expressions/macros, enforcing formatting gates (80 columns, braces), or auditing for risky language features.

---

## 1.1 Which C? (C99 Baseline + Extensions Discipline)

### What to check

- **C99 target:** Code assumes C99 as the baseline (e.g., `//` comments, local declarations near use, `<stdint.h>`, `<stdbool.h>`).
- **C++ compiler restriction:** If a C++ compiler is used for C sources, confirm compiler options restrict language to the intended ISO C version.
- **Extensions are rare and localized:** Compiler extensions, pragmas, and inline assembly are minimized and confined to a small number of hardware-facing modules (typically low-level drivers or startup code).
- **No “language rewriting” with `#define`:** Preprocessor definitions must not rename or alter C keywords or core language constructs.

### Why it matters

- Embedded toolchains vary widely; sticking to a defined ISO C version reduces implementation-defined surprises.
- Extensions scattered across the codebase increase coupling to a single compiler/toolchain and complicate maintenance and portability.

### Common failure modes

- Renaming language constructs (e.g., `#define begin {`) makes code misleading and fragile.
- Using `#pragma` or attributes across many modules (instead of isolating them).
- Using inline assembly outside strict hardware-near contexts.

### Preferred fixes (patterns)

- **Localize non-portable code** into dedicated driver modules and wrap it with clear comments and/or deviation markers.
- **Abstract extensions** behind a small compatibility header (e.g., `compiler_port.h`) that defines macros like `ISR_ATTR`, `PACKED`, etc., used in a controlled way.

**Example: isolate ISR decoration**

```c
/* compiler_port.h */
#if defined(__IAR_SYSTEMS_ICC__)
# define ISR_ATTR __interrupt
#elif defined(__GNUC__)
# define ISR_ATTR __attribute__((interrupt))
#else
# define ISR_ATTR
#endif
```

---

## 1.2 Line Widths (≤ 80 Characters)

### What to check

- Any line exceeding **80 characters**, especially:
  - complex `if` conditions
  - long macro invocations
  - chained arithmetic and bitwise expressions
  - long function signatures

### Why it matters

- Prevents line wrapping in printed reviews and improves side-by-side diffs.

### Common failure modes

- Huge boolean expressions that are visually unreviewable.
- “One-liners” that hide multiple operations.

### Preferred fixes (patterns)

1. **Introduce named intermediate booleans** for readability.
2. **Wrap logical operands** on new lines with consistent indentation.
3. **Extract helper functions** when a condition represents a meaningful predicate.

**Example: wrap and name a predicate**

```c
bool b_in_range =
    ((0u < depth_cm) && (depth_cm < MAX_DEPTH_CM));

if (b_in_range)
{
    depth_ft = convert_depth_to_ft(depth_cm);
}
```

---

## 1.3 Braces (Always Use Braces for Control Blocks)

### What to check

- Braces must surround the blocks following:
  - `if`, `else`, `else if`
  - `switch`
  - `while`, `do … while`
  - `for`
- This includes:
  - **single statements**
  - **empty statements** (should be a braced empty block with an explanation comment if intentional)
- **Brace placement:** left brace on its own line under the control statement; right brace aligned and on its own line.

### Why it matters

- Eliminates a major class of defects caused by:
  - accidental “dangling else”
  - adding a second statement later without braces
  - mistakenly leaving a semicolon as an empty body

### Common failure modes

- “Looks right” but behaves wrong after edits:
```c
if (b_ready)
    start();
    log_event(); /* always executes by mistake */
```

### Preferred fixes (patterns)

**Before:**

```c
if (b_ready)
    start();
```

**After:**

```c
if (b_ready)
{
    start();
}
```

**Empty body that is intentional:**
```c
while (0u != (*p_status_reg & BUSY_MASK))
{
    /* NOTE: Intentional busy-wait until hardware clears BUSY. */
}
```

---

## 1.4 Parentheses (Clarity Over Precedence)

### What to check

- Do not rely on implicit operator precedence for non-trivial expressions.
- Each operand of `&&` and `||` should be parenthesized unless it is a single identifier or constant.
- Long expressions should be **split across lines** or **broken into named intermediates**.

### Why it matters

- C operator precedence is complex and error-prone; reviewers may misread intent.
- Parentheses reduce ambiguity and improve maintainability.

### Common failure modes

- Bitwise and comparison precedence confusion:
-
```c
if (flags & MASK == 0u)   /* ambiguous: is it (flags & (MASK==0)) ? */
{
    ...
}
```

### Preferred fixes (patterns)

- Make precedence explicit:
-
```c
if (0u == (flags & MASK))
{
    ...
}
```

- Parenthesize logical operands:
-
```c
if (((a > 0) && (a < LIMIT)) || (b_enabled))
{
    ...
}
```

- Extract predicates:
-
```c
bool b_depth_ok = ((0u < depth_cm) && (depth_cm < MAX_DEPTH_CM));
bool b_speed_ok =
    ((speed_mps >= MIN_SPEED_MPS) && (speed_mps <= MAX_SPEED_MPS));

if (b_depth_ok && b_speed_ok)
{
    ...
}
```

---

## 1.5 Abbreviations and Acronyms (Keep Names Decodable)

### What to check

- Avoid unclear abbreviations and acronyms unless widely understood and consistently used.
- Maintain a project-specific list of allowed abbreviations in version control.

### Why it matters

- Reduces maintenance defects caused by misunderstanding variable and function intent.

### Preferred fixes

- Prefer descriptive names over cryptic abbreviations.
- If abbreviations are required, document them in a shared glossary.

---

## 1.6 Casts (Casting Is Dangerous—Document Range Safety)

### What to check

- Each cast must have an associated comment explaining:
  - why the cast is safe
  - what assumptions it relies on (e.g., `int` width, range limits)
  - how the code ensures correctness for all possible values

### Why it matters

- Casts can silently truncate, overflow, or change signedness, producing subtle bugs.

### Common failure modes

- Casting unsigned wider-range values into signed narrower types without bounds proof.
- Assuming `int` is 32-bit everywhere.

### Preferred fixes (patterns)

- Replace casts with safe conversion code + checks.
- Use fixed-width types to avoid implicit assumptions.
- If you must cast, **document the range and assumptions**:

```c
uint16_t sample_u16 = adc_read(ADC_CHANNEL_1);

/* WARNING: Cast assumes sample_u16 <= 4095 (12-bit ADC), and int32_t is available. */
int32_t sample_i32 = (int32_t)sample_u16;
```

---

## 1.7 Keywords to Avoid (auto/register; Prefer Avoid goto/continue)

### What to check

- **Forbidden:** `auto`, `register`
- **Discouraged:** `goto`, `continue` (use only when it clearly improves clarity and remains structured)

### Why it matters

- `register` presumes the programmer knows better than the compiler.
- `goto`/`continue` often lead to spaghetti flow and review difficulty.

### Common failure modes

- `continue` used to “skip ahead” in loops, creating hidden control paths.
- `goto` used for general flow rather than rare cleanup/exception handling.

### Preferred fixes (patterns)

- Replace `continue` with explicit `if` blocks:
-
```c
for (int idx = 0; idx < n_items; idx++)
{
    if (!item_is_valid(items[idx]))
    {
        /* NOTE: Skip invalid entries. */
    }
    else
    {
        process_item(items[idx]);
    }
}
```

- If `goto` is used for cleanup, keep it forward-only and local, with a clear label:
-
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

## 1.8 Keywords to Use Frequently (static / const / volatile)

### What to check

- **`static`**
  - Functions and file-scope variables that do not need external visibility should be `static`.
- **`const`**
  - Use for read-only variables, constants, and read-only pointer parameters.
  - Prefer `const` over `#define` for typed numeric constants when feasible.
- **`volatile`**
  - Use for:
    - variables shared with ISRs
    - variables shared across threads/tasks
    - memory-mapped I/O registers (MMIO) pointers
    - delay loop counters

### Why it matters

- `static` reduces coupling and name collisions across modules.
- `const` prevents unintended writes at compile time.
- `volatile` prevents “optimization bugs” where reads/writes are removed or reordered incorrectly.

### Common failure modes

- Missing `volatile` for ISR/shared flags leading to “glitches” only at higher optimization levels.
- Using `#define` for typed constants, losing type safety.
- Exporting internal helper functions (forgetting `static`), increasing coupling.

### Preferred fixes (patterns)

#### Encapsulation with static

```c
static void update_state (void)
{
    ...
}
```

#### const correctness

```c
int sensor_read (uint8_t const * const p_buf, uint16_t n_bytes);
```

#### MMIO pointer pattern

```c
typedef struct
{
    uint16_t count;
    uint16_t max_count;
    uint16_t const _unused; /* read-only register */
    uint16_t control;
} timer_reg_t;

static timer_reg_t volatile * const p_timer =
    (timer_reg_t volatile * const)HW_TIMER_ADDR;
```

---

## Quick enforcement hooks (for this chapter)

### Grep-style checks (cheap)

- Tabs: search for literal `\t`
- Forbidden keywords: `\b(auto|register)\b`
- Braces missing after control keywords (heuristic):
  - find lines like `if (` not followed by `{` on next non-blank line
- Assignment in conditionals (heuristic):
  - `if\s*\(.*=[^=]`

### Review-time “must ask”

If the code uses `volatile`, ISRs, or threads:

- What concurrency model exists (bare metal vs RTOS)?
- Are shared variables accessed atomically for the target width?
- Are critical sections required around shared state?

---

## Minimal “General Rules” review checklist (copy/paste)

- [ ] C99 baseline adhered to; extensions localized and documented
- [ ] Lines ≤ 80 characters (or wrapped cleanly)
- [ ] Braces used for every control structure; brace placement consistent
- [ ] Parentheses clarify precedence; `&&`/`||` operands parenthesized
- [ ] Casts are rare and include range/assumption comments
- [ ] `auto`/`register` absent; `goto`/`continue` avoided or justified
- [ ] `static` used for private symbols; `const` and `volatile` applied correctly
