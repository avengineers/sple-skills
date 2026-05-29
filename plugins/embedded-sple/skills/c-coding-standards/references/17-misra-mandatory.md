# 11 — MISRA C:2012 Mandatory-by-Design Guidance (Authoring + Review)

**Purpose:** Ensure the developer (and this agent) considers **Mandatory MISRA C:2012** requirements from the outset.

Mandatory guidelines **must always be complied with** (no deviations).
**Use when:** the project claims MISRA compliance, especially in safety/security/critical systems.

> MISRA expects a process that uses static analysis tools and a compliance approach early, not late.

---

## A) Mandatory means “no exceptions”

- Mandatory guidelines are non-negotiable; if code violates one, it is not MISRA compliant.
- If you hit a “mandatory conflict”, redesign rather than deviating.

---

## B) Mandatory “catches” to treat as design constraints

### 1) Rule 9.1 — no read of uninitialized automatic objects (Mandatory)

**Intent:** Never read an automatic variable before it is set.
**Authoring habits:**

- Initialize on declaration.
- Avoid conditional initialization with later unconditional use.
- Prefer “declare near first use” (C99 supports this) and set a safe default.

**Review triggers:**

- Variables assigned in one branch but used after the branch.
- Out-parameters not written on all paths.

---

### 2) Rule 12.5 — don’t use `sizeof` on array-typed parameters (Mandatory)

**Intent:** Function parameters declared as arrays are actually pointers; `sizeof(param)` is wrong.
**Authoring habits:**

- Pass array length explicitly (or use a struct wrapper with size).
- Use `sizeof` only on real arrays in the same scope, not on parameters.

---

### 3) Rule 13.6 — no side effects inside `sizeof` operand (Mandatory)

**Intent:** The operand of `sizeof` must not contain expressions with side effects.
**Authoring habits:**

- Never call functions inside `sizeof`.
- Never use `++/--` or assignments inside `sizeof`.
- Prefer `sizeof(type)` or `sizeof(obj)` with a plain identifier.

---

### 4) Rule 17.4 — all non-void functions return a value on every path (Mandatory)

**Intent:** Every exit path must explicitly return a value.
**Authoring habits:**

- Use a single return at the end with a “result” variable.
- If you use early returns, ensure every path returns (but also be aware of project style constraints).

---

### 5) Rule 17.6 (C99) — no `static` in array parameter declarators (Mandatory)

**Intent:** The `static` array parameter feature introduces risk; it’s forbidden.
**Authoring habits:**

- Never write `f(int a[static 10])`.
- If you need “min length” documentation, use comments + explicit length parameter.

---

## C) Process guidance MISRA expects (tooling + evidence)

- MISRA guidance emphasizes using static analysis tools and configuring them appropriately to match the compiler/implementation, and applying MISRA early in the lifecycle.
- Record tool versions and options used for compliance checking as part of the compliance story.

---

## D) How this agent should review under MISRA Mandatory

When MISRA is required:

1) Treat any Mandatory violation as **Blocker**.
2) Prefer “rewrite to safety” over local patches that preserve risky structure.
3) If a tool finding references a Mandatory guideline, do not suggest deviations; propose redesign.

---

## E) MISRA C:2012 Compliance

**Goal:** Zero suppressions. If a suppression is strictly necessary (e.g., hardware memory mapping), use inline suppression with a justification.

### Inline Suppression (Last Resort)

```c
// polyspace-begin MISRA2012:11.4 [Justified: Hardware register access requires pointer cast]
volatile uint32_t* const UART_REG = (volatile uint32_t*)0x40001000;
// polyspace-end MISRA2012:11.4
```

### Critical Rules (Zero Tolerance)

- **Rule 17.2:** No recursion.
- **Rule 9.1:** No uninitialized variables.
- **Rule 21.6:** No use of standard library input/output functions (printf, scanf) in production code (driver layer).
- **Rule 11.4:** Casts from integer to pointer only for memory-mapped registers (must justify).
- **Rule 10.x:** Implicit conversions (use explicit casts with appropriate types).

### Coding Practices for MISRA Compliance

1. **Use stdint types exclusively:** `uint8_t`, `int32_t`, etc. (never `int`, `long`, `unsigned`)
2. **Initialize all variables at declaration**
3. **Explicit type casts:** Never rely on implicit conversions
4. **No dynamic memory:** No `malloc`/`free`
5. **Function prototypes:** Declare all functions in headers
6. **Static functions:** Functions used only in one file should be `static`
7. **Const correctness:** Use `const` for read-only parameters

### Example: MISRA-Compliant Code

```c
#include <stdint.h>
#include <stdbool.h>

// Good: Explicit types, initialized variables, const parameter
static void processData(const uint8_t* data, uint16_t length)
{
    uint16_t sum = 0U;  // Explicit initialization and unsigned suffix

    for (uint16_t i = 0U; i < length; i++)
    {
        sum = (uint16_t)(sum + data[i]);  // Explicit cast for widening
    }
}

// Bad: Implicit types, no initialization, no const
void processData(char* data, int length)
{
    int sum;  // Uninitialized
    for (int i = 0; i < length; i++)
        sum += data[i];  // Implicit conversions
}
```

## Integration with SPLED

- **Variant-specific checks:** Each variant has `variants/<Name>/static_analysis.json` configuration
- **CI/CD integration:** Jenkinsfile runs Polyspace as part of STATIC_ANALYSIS stage
- **Quality gates:** PR validation automatically checks MISRA compliance
- **Compiler options:** See `variants/<Name>/sca_compiler_options_file.txt` for analysis settings

````

---

## F) Minimal review checklist (Mandatory focus)

- [ ] No read-before-set of automatic objects (Rule 9.1).
- [ ] No `sizeof(param)` where param is an “array parameter” (Rule 12.5).
- [ ] No side effects inside `sizeof` operands (Rule 13.6).
- [ ] All non-void functions return a value on all paths (Rule 17.4).
- [ ] No `static` keyword inside array parameter brackets (Rule 17.6 C99).
