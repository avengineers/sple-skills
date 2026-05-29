# 15 — MMIO Register Map Patterns (BARR‑C:2018‑Aligned)

**Purpose:** Provide safe, portable-ish patterns for interacting with memory‑mapped I/O (MMIO) registers while honoring BARR‑C goals: minimize defects, keep intent clear, and isolate compiler/toolchain dependencies.
**Use this document when:** writing peripheral drivers, mapping register blocks, handling read-only/write-only registers, dealing with padding/packing, or reviewing `volatile` usage.

> **Core rule:** MMIO is a shared “singleton” object (hardware state). Treat it like concurrency: use correct `volatile`, avoid undefined behavior, and document assumptions.

---

## 0) Golden Rules (Quick Review Triggers)

1. **Use `volatile` for MMIO accesses**
   - Prevents the compiler from removing or reordering reads/writes that the hardware depends on.

2. **Use `* const` for fixed base pointers**
   - The pointer value should not change at runtime.

3. **Prefer explicit masks/shifts over bitfields**
   - Bitfield ordering and layout are compiler/ABI dependent.

4. **Verify layout when a struct overlay is used**
   - Add compile-time size checks (and offset checks if your toolchain supports them).

5. **Document register semantics**
   - Common hazards:
     - W1C (write-1-to-clear)
     - R2C (read-to-clear)
     - “dummy read required” errata
     - reserved bits must be preserved
     - write-only registers (reading has side effects or returns garbage)

---

## 1) The Canonical Pointer Pattern (`volatile * const`)

### Use when

- You have a fixed peripheral base address for a register block.

### Pattern

```c
typedef struct
{
    uint32_t ctrl;
    uint32_t status;
    uint32_t data;
} uart_reg_t;

static uart_reg_t volatile * const p_uart =
    (uart_reg_t volatile * const)UART0_BASE;
```

### Why

- `volatile *` → accesses always happen as written
- `* const` → base pointer is fixed (prevents accidental reassignment)

---

## 2) Read-only and Write-only Registers (Make Semantics Explicit)

### Use when

- The hardware defines a register as read-only or write-only.

### Pattern: read-only field (use `const`)

```c
typedef struct
{
    uint32_t ctrl;
    uint32_t const status; /* read-only */
    uint32_t data;
} periph_reg_t;

static periph_reg_t volatile * const p_periph =
    (periph_reg_t volatile * const)PERIPH_BASE;
```

### Pattern: write-only register (do NOT mark as const)

C cannot enforce “write-only” directly, but you can document and avoid reads.

```c
typedef struct
{
    uint32_t ctrl;
    uint32_t status;
    uint32_t cmd; /* write-only: do not read */
} periph_reg_t;
```

**Guideline:**

- Add `/* write-only */` comment and never read it in code.
- In reviews, treat any read of such fields as **High risk**.

---

## 3) Reserved Bits: Preserve Them Safely (Avoid RMW Hazards)

### Use when

- The datasheet says “reserved bits must be kept at reset value” or “write as read”.

### Pattern: read-mask-write (foreground only, protected if concurrent)

```c
#define CTRL_ENABLE_MASK   (1u << 0)
#define CTRL_MODE_MASK     (3u << 4)
#define CTRL_MODE_SHIFT    (4u)

static void ctrl_set_mode (uint32_t mode)
{
    uint32_t reg;

    /* NOTE: Preserves reserved bits by masking and merging. */
    reg  = p_periph->ctrl;
    reg &= ~CTRL_MODE_MASK;
    reg |= ((mode << CTRL_MODE_SHIFT) & CTRL_MODE_MASK);

    p_periph->ctrl = reg;
}
```

### Concurrency warning

If an ISR can write the same register, the RMW sequence may race.
**Mitigation options:**

- protect with a critical section
- write only the documented writable bits if the peripheral supports that
- centralize all writes in one context (recommended)

---

## 4) W1C (Write-1-to-Clear) and R2C (Read-to-Clear)

### Use when

- Status bits clear by writing `1` to that bit, or clear when read.

### Pattern: W1C clear

```c
#define STATUS_ERR_MASK  (1u << 3)

static void clear_error (void)
{
    /* NOTE: W1C register: write 1 to clear error bit(s). */
    p_periph->status = STATUS_ERR_MASK;
}
```

### Pattern: R2C read-to-clear

```c
static uint32_t read_status_r2c (void)
{
    /* NOTE: R2C register: reading clears latched status bits. */
    return p_periph->status;
}
```

**Review note:**

- Any “status read” may change hardware state. Demand a `NOTE:` comment for R2C.

---

## 5) Avoid Bitfields in MMIO Overlays (Prefer Masks/Shifts)

### Why avoid bitfields

- Bit ordering and packing are not portable across compilers/targets.
- Some toolchains lay out bitfields differently; this can silently write the wrong bits.

### Prefer this (mask/shift)

```c
#define CTRL_ENABLE_MASK  (1u << 0)
#define CTRL_MODE_MASK    (3u << 4)
#define CTRL_MODE_SHIFT   (4u)

static void periph_enable (bool b_enable)
{
    if (b_enable)
    {
        p_periph->ctrl |= CTRL_ENABLE_MASK;
    }
    else
    {
        p_periph->ctrl &= ~CTRL_ENABLE_MASK;
    }
}
```

### If you must use bitfields (rare)
- Constrain it to a fixed compiler + target and document a deviation.
- Add compile-time layout verification.
- Prefer `uint32_t` unsigned base types for bitfields.

```c
/* DEVIATION (BARR-C 5.5):
 * Reason: Toolchain-fixed project; vendor header defines bitfields.
 * Risk: Non-portable across compilers/targets.
 * Mitigation: Locked compiler version; verified via integration tests.
 * Approved-by:
 * Date:
 */
```

---

## 6) Struct Layout Verification (Size and Offsets)

### Use when

- You rely on a struct overlay matching the datasheet register map.

### Minimal check: size

```c
#if (12u != sizeof(uart_reg_t))
# error "uart_reg_t size mismatch (expected 12 bytes)"
#endif
```

### Stronger check: offsets (if available)

If your environment supports `offsetof` reliably:

```c
#include <stddef.h>

#if (0u != offsetof(uart_reg_t, ctrl))
# error "uart_reg_t.ctrl offset mismatch"
#endif

#if (4u != offsetof(uart_reg_t, status))
# error "uart_reg_t.status offset mismatch"
#endif
```

**Note:**

- Offsets are especially important if the register map includes gaps/reserved words.

---

## 7) Alignment and Access Width (16-bit/8-bit Targets)

### Problem

- Some MCUs require aligned accesses or only allow certain widths (8/16/32-bit).
- Misaligned struct members can cause bus faults or unexpected behavior.

### Guidance

- Match register widths exactly with fixed-width types.
- Ensure the struct is naturally aligned per your ABI.
- If the device requires 16-bit accesses, use `uint16_t` fields and verify layout.

Example:

```c
typedef struct
{
    uint16_t ctrl;
    uint16_t status;
    uint16_t data;
    uint16_t _reserved;
} periph16_reg_t;
```

---

## 8) Endianness Notes (When It Matters)

### Use when

- Register fields represent byte arrays or multi-register values.
- Peripheral presents data in a specific order.

### Pattern

```c
/* NOTE: Multi-register 32-bit value is little-endian: LOW then HIGH register. */
low  = p_adc->value_low;
high = p_adc->value_high;
value = ((uint32_t)high << 16) | (uint32_t)low;
```

---

## 9) “Safe Wrapper” Functions (Encapsulation Best Practice)

### Why

- Keeps register semantics in one place.
- Reduces repeated RMW patterns and the risk of missing reserved-bit handling.

### Pattern

```c
uint32_t periph_get_status (void)
{
    return p_periph->status;
}

void periph_clear_error (void)
{
    p_periph->status = STATUS_ERR_MASK; /* W1C */
}
```

**Review tip:**
If you see direct register writes scattered across the codebase, recommend consolidating into a driver module API.

---

## 10) Common Reviewer Findings (What to flag)

### Blockers

- Missing `volatile` on MMIO pointers or shared registers
- Reading from write-only registers
- Writing to R2C registers without comment/understanding
- Struct overlay without size/layout checks where layout is assumed

### High

- Bitfields used for MMIO without deviation + verification
- RMW on control register without reserved-bit preservation rules
- RMW sequences not protected when multiple contexts write the same register

### Medium

- No `NOTE:` for non-obvious register semantics (W1C/R2C/dummy reads)
- MMIO pointers not `* const` (allowing reassignment)

---

## 11) Review Checklist (MMIO register maps)

- [ ] MMIO pointers are `type volatile * const` and correctly typed
- [ ] Read-only registers represented with `const` fields (where appropriate)
- [ ] Write-only registers are never read and are documented
- [ ] W1C / R2C / dummy-read semantics documented with `NOTE:`
- [ ] Reserved bits preserved correctly (mask/merge strategy)
- [ ] Bitfields avoided; if used, deviation + verification exists
- [ ] Layout checks exist (size and offsets if necessary)
- [ ] Access widths and alignment constraints respected
- [ ] Register access consolidated into driver APIs (preferred)

---

## 12) Minimal deviation template (if required)

```c
/* DEVIATION (BARR-C X.Y):
 * Reason:
 * Risk:
 * Mitigation:
 * Approved-by:
 * Date:
 */
```
