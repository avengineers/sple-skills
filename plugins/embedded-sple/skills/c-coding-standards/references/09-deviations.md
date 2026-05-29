# 09 — Deviations (BARR‑C:2018 Deviation Procedure)

**Purpose:** Provide a consistent, auditable way to handle the rare cases where strict compliance with BARR‑C must be relaxed due to hardware, compiler, RTOS, certification, or legacy constraints—without letting “exceptions” become the norm.
**Use this document when:** a rule cannot be followed as written, porting legacy code, using compiler-required ISR attributes/pragmas, mapping MMIO registers, dealing with toolchain quirks, or integrating third‑party libraries.

---

## Deviation Principles (Non‑Negotiables)

1. **All release code shall conform** to the standard *except* approved, documented deviations.
2. **Deviations must be specific, localized, and justified**:
   - Prefer a deviation for a single line/function over a broad module‑wide exemption.
3. **Document deviations as close as possible to the code** (nearest meaningful location).
4. **Approval is required**:
   - Record the approver’s name/role and reasoning.
5. **Mitigate risk**:
   - Whenever a rule is violated, document the risk introduced and what mitigations apply.
6. **Avoid “silent drift”**:
   - Any deviation should be discoverable during review and by automated searches (where possible).

---

## When Deviations Are Acceptable (Common Scenarios)

Deviations are typically acceptable only when compliance would cause a larger risk or is technically impossible:

### A) Hardware / MMIO constraints
- Struct overlays that require precise layout or compiler attributes.
- Required volatile patterns for peripheral registers.
- Bitfield usage only when a fixed compiler/target is guaranteed and verified.

### B) Compiler / toolchain requirements
- ISR attributes/pragmas required by a specific compiler.
- Necessary `#pragma` use that cannot be avoided.
- Toolchain bugs or missing features requiring workarounds.

### C) RTOS or platform ABI constraints
- Task function signatures mandated by the RTOS.
- ISR installation mechanisms requiring symbol visibility.

### D) Legacy or third‑party code
- Certified/validated legacy modules that cannot be reformatted or refactored without re‑qualification.
- Vendor HAL libraries that don’t comply and are imported “as-is”.

### E) Performance and memory constraints (rare)
- A rule-compliant alternative creates unacceptable latency/code size.
- Must be documented with measurement evidence where possible.

---

## Deviation Types (How Big Is the Exception?)

### 1) Micro deviation (preferred)
- Single line or small block.
- Document inline at the exact location.

### 2) Function-level deviation
- Applies to one function (e.g., necessary multiple returns for clarity or time constraints).
- Document at the function header.

### 3) Module-level deviation (last resort)
- Applies to many places in a file (e.g., third‑party driver module).
- Document in the file header block with a clear scope.

> **Rule of thumb:** the broader the deviation scope, the stronger the justification and review rigor required.

---

## Required Deviation Metadata (What to Write)

Each deviation must include, at minimum:

- **Which rule(s):** `BARR‑C X.Y` (and sub-rule letter if applicable)
- **Reason:** why compliance is impractical/unsafe/impossible
- **Risk:** what new risk is introduced by deviating
- **Mitigation:** how the risk is reduced (tests, assertions, reviews, static analysis, hardware checks)
- **Approval:** name/role (or placeholder) and date
- **Scope:** line/function/module and any constraints (compiler version, MCU family, etc.)
- **Removal plan (optional but recommended):** conditions under which deviation can be removed

---

## Standard Deviation Comment Templates (Copy/Paste)

### A) Inline deviation (single line / small block)
```c
/* DEVIATION (BARR-C X.Y):
 * Reason:
 * Risk:
 * Mitigation:
 * Approved-by:
 * Date:
 */
```

### B) Function-level deviation (place above function definition)
```c
/* DEVIATION (BARR-C X.Y):
 * Scope: This function only.
 * Reason:
 * Risk:
 * Mitigation:
 * Approved-by:
 * Date:
 */
```

### C) Module-level deviation (place in top-of-file comment block)
```c
/* DEVIATION SUMMARY:
 * - BARR-C X.Y: <short label>
 *   Scope: Entire module (vendor HAL import).
 *   Reason:
 *   Risk:
 *   Mitigation:
 *   Approved-by:
 *   Date:
 */
```

---

## Examples of Well‑Formed Deviations

### Example 1 — Compiler-required ISR attribute/pragma
```c
/* DEVIATION (BARR-C 1.1 / 6.5):
 * Reason: Toolchain requires ISR pragma/attribute for correct prologue/epilogue.
 * Risk: Reduced portability across compilers.
 * Mitigation: Centralized through compiler_port.h; unit tested on supported toolchains.
 * Approved-by: <NAME/ROLE>
 * Date: <YYYY-MM-DD>
 */
ISR_ATTR static void timer_isr (void)
{
    ...
}
```

### Example 2 — Necessary `goto` cleanup (restricted use)
```c
int init_system (void)
{
    int rc = ERR_OK;

    p_buf = alloc_buf();
    if (NULL == p_buf)
    {
        rc = ERR_NO_MEM;
        goto cleanup;
    }

    p_dev = open_dev();
    if (NULL == p_dev)
    {
        rc = ERR_OPEN_FAIL;
        goto cleanup;
    }

    /* ... */

cleanup:
    /* DEVIATION (BARR-C 1.7.c):
     * Reason: Single cleanup block reduces duplication and error risk.
     * Risk: Misuse of goto could degrade readability if expanded.
     * Mitigation: Forward-only jump; label at function end; reviewed.
     * Approved-by: <NAME/ROLE>
     * Date: <YYYY-MM-DD>
     */
    close_dev(p_dev);
    free_buf(p_buf);
    return rc;
}
```

### Example 3 — MMIO struct layout verification
```c
typedef struct
{
    uint32_t ctrl;
    uint32_t status;
    uint32_t data;
} uart_reg_t;

static uart_reg_t volatile * const p_uart =
    (uart_reg_t volatile * const)UART0_BASE;

#if (12u != sizeof(uart_reg_t))
# error "DEVIATION (BARR-C 5.5): uart_reg_t layout must match HW register map."
#endif
```

---

## Deviation Review Process (Recommended Workflow)

1. **Attempt compliant solution first**
   - Document why it fails (technical reason, measurable constraint).
2. **Choose narrowest deviation scope**
   - Line > function > module.
3. **Write deviation comment**
   - Use the template; include risk + mitigation.
4. **Get approval**
   - Project manager / lead / safety owner as appropriate.
5. **Add enforcement hooks**
   - Add a grep token like `DEVIATION (` for easy scanning.
6. **Add tests or static checks**
   - Make the mitigation real: assertions, compile-time checks, unit tests.
7. **Track deviations**
   - Maintain a lightweight list (e.g., `doc/deviations.md`) with pointers to file/line and justification.

---

## Automation Hooks for Deviations

### Grep discovery tokens
- Standardize on:
  - `DEVIATION (BARR-C`
  - `DEVIATION SUMMARY`

This enables:
- CI checks for newly introduced deviations
- periodic reporting of deviation count and locations

### Policy suggestion
- Fail CI if:
  - a new deviation is added without `Approved-by` and `Date`
  - deviation scope is module-wide without explicit justification

---

## Review Checklist (Copy/Paste)

- [ ] Deviation is truly necessary; compliant alternative considered
- [ ] Scope is minimal (line/function preferred over module)
- [ ] Comment includes rule reference, reason, risk, mitigation, approval, date
- [ ] Mitigation is concrete (tests/assertions/static checks)
- [ ] Deviation is discoverable (standard token) and traceable (file/line)
- [ ] No “blanket exemptions” without strong justification
- [ ] Plan exists to remove deviation if constraints change (optional but recommended)
