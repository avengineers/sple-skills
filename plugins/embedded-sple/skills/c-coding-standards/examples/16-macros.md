# 16 — Macro Patterns (Do/Don’t + Safe Alternatives) (BARR‑C:2018‑Aligned)

**Purpose:** Provide practical patterns for replacing risky macros with safer C99 constructs (functions, `static inline`, typed constants) and for writing the rare “acceptable” macro safely when necessary.
**Use this document when:** you see parameterized macros, complex `#define` logic, macro-based “functions,” type-unsafe constants, or debugging code sprinkled via macros.

> **Rule of thumb:** If you can write a function, **write a function**. Use macros mainly for **compile-time constants**, conditional compilation, and very small portability shims.

---

## 0) Macro Risk Summary (Why reviewers should care)

Macros are risky because they:

- do not perform type checking
- may evaluate arguments multiple times (side effects)
- may have precedence bugs if not aggressively parenthesized
- are invisible at runtime (hard to debug/step into)
- can encourage signed/unsigned mixing and float comparisons accidentally

Use these patterns to reduce risk.

---

## 1) Prefer Typed `const` Over `#define` for Numeric Constants

### When to use

- You need a constant with type checking, scope control, and debugger visibility.

### Don’t

```c
#define TIMEOUT_MS 1000
```

### Do (typed constant)

```c
static uint16_t const TIMEOUT_MS = 1000u;
```

### Notes

- Prefer `u` suffix for unsigned literals where appropriate.
- Use module scope (`static`) to avoid external coupling.

---

## 2) Avoid Function‑Like Macros; Use `static inline` Instead

### 2.1 Classic example: MAX

#### Don’t

```c
#define MAX(A, B)  ((A) > (B) ? (A) : (B))
```

#### Why not

- Double evaluation:
```c
x = MAX(i++, j++); /* increments twice in one path */
```

#### Do (safe alternative)

```c
static inline int32_t max_i32 (int32_t a, int32_t b)
{
    return (a > b) ? a : b;
}
```

### 2.2 “Mathy” macros with precedence bugs

#### Don’t

```c
#define SCALE(x)  x * 10u
y = SCALE(a + b); /* expands to a + b * 10u */
```

#### Do

```c
static inline uint32_t scale_u32 (uint32_t x)
{
    return x * 10u;
}
```

---

## 3) If a Parameterized Macro Is Truly Necessary, Make It “Macro-Safe”

### Allowed only if:

- A function can’t be used (e.g., requires compile-time expression in `#if`, array size, `_Static_assert`, or special token tricks).
- Performance constraints are real and measured (and inline cannot satisfy).
- The macro’s argument usage is side-effect-free by contract.

### BARR‑C macro safety requirements

When you *must* use a parameterized macro:
1. Parenthesize the entire macro body
2. Parenthesize each parameter use
3. Use each parameter **no more than once**
4. Never transfer control (`return`, `goto`, etc.)

### Example: CLAMP (still risky; review hard)

```c
#define CLAMP_U16(V, LO, HI) \
    (((V) < (LO)) ? (LO) : (((V) > (HI)) ? (HI) : (V)))
```

**Usage rule:** never pass side effects:

```c
val = CLAMP_U16(val, lo, hi);    /* OK */
val = CLAMP_U16(val++, lo, hi);  /* DO NOT */
```

**NOTE:** This macro uses `V` more than once (common CLAMP does), which violates the “use each parameter once” ideal. Prefer a function unless you require compile-time evaluation. A safer approach is a function or an inline function for runtime clamping.

---

## 4) Multi‑Statement Macros (Use `do { ... } while (0)`)

### When to use

- Rarely, for debugging hooks or tiny repeated patterns—prefer functions.

### Don’t

```c
#define SET_ERROR(x) g_err = (x); log_err(x);
```

### Do

```c
#define SET_ERROR(X)           \
    do                         \
    {                          \
        g_err = (X);           \
        log_err((X));          \
    } while (0)
```

### Notes

- `do { } while (0)` ensures it behaves like a statement in `if/else`.
- Still beware double evaluation; `X` is used twice here—prefer function unless `X` is side-effect-free.

---

## 5) Macro “Traps” to Flag in Reviews

### 5.1 Side effects in macro arguments (High)

Look for calls like:

```c
MAX(i++, j++)
LOG(read_reg(), "msg")
```

### 5.2 Missing parentheses (High)

```c
#define BIT(n)  1u << n
mask = BIT(a + 1u); /* expands incorrectly */
```

Fix:

```c
#define BIT(N)  (1u << (N))
```

### 5.3 Signed/unsigned surprises (High)

```c
#define IS_NEG(x) ((x) < 0) /* if x is unsigned, always false */
```

Fix:

- Use typed functions and normalize types before comparisons.

### 5.4 Hidden control flow (Blocker)

Macros that `return`, `break`, `continue`, `goto` are high risk and should be rejected unless a very strong reason exists and is documented.

---

## 6) Macro Alternatives Cookbook (Recommended Replacements)

### Replace macro constants → typed `const`

- `#define BUF_SIZE 64` → `static uint16_t const BUF_SIZE = 64u;`

### Replace parameterized macros → `static inline` functions

- `MAX`, `MIN`, `ABS`, scaling, unit conversion, bounds checks

### Replace “debug logging macros” → `#ifndef NDEBUG` blocks

Instead of:

```c
#define DBG_PRINT(...) printf(__VA_ARGS__)
```

Prefer:

```c
#ifndef NDEBUG
debug_print("x=%u\n", x);
#endif
```

---

## 7) “Inline” vs Macro (Performance Notes)

### Guidance

- Prefer `static inline` for:
  - type safety
  - debug visibility (often still stepable depending on toolchain)
  - single-evaluation semantics

### Review trigger

If a contributor claims “macro needed for performance,” request:
- measured evidence (cycles / size) **or**
- confirmation that `inline` cannot satisfy due to toolchain constraints

---

## 8) Minimal Deviation Template (If Macro Use Must Break Rules)

```c
/* DEVIATION (BARR-C 6.3):
 * Reason:
 * Risk:
 * Mitigation:
 * Approved-by:
 * Date:
 */
```

---

## 9) Review Checklist (Macros)

- [ ] Parameterized macros avoided; functions/`static inline` used instead
- [ ] If macros exist:
  - [ ] body fully parenthesized
  - [ ] each parameter parenthesized
  - [ ] no side effects from multi-evaluation (ideally each parameter used once)
  - [ ] no hidden control flow (`return/goto/break/continue`)
  - [ ] no signed/unsigned traps
- [ ] Prefer typed constants (`static const`) over `#define` for numeric values
- [ ] Debug-only code uses `#ifndef NDEBUG` blocks rather than always-on macros
- [ ] Any unavoidable macro deviation is documented and approved
