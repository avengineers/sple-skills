# 13 — Safety & Portability Checklist (BARR‑C:2018 Focus)

**Purpose:** A deeper checklist focused on the most defect-prone areas for embedded firmware—especially **portability traps**, **concurrency/ISR hazards**, and **hardware interface correctness**—while staying aligned with BARR‑C intent.
**Use this document when:** code touches interrupts, RTOS tasks, MMIO registers, protocol/packet formats, fixed-width arithmetic, casts, or anything that will be reused/ported across targets.

> This checklist is *not* a safety standard. Use it to reduce bug risk; apply your project’s safety/security process as required.

---

## How to use (recommended workflow)

1. **Identify the “portability boundary”**
   - Which compilers/versions? Which MCU families? Any 8/16/32-bit variants?
2. **Identify the “concurrency boundary”**
   - Bare metal vs RTOS; ISR nesting; preemption; shared objects.
3. **Identify the “hardware boundary”**
   - MMIO overlays, register semantics (W1C, R2C), timing loops, DMA, cache.
4. Apply relevant sections only (don’t treat this as a blanket requirement for every PR).

---

## A) Portability — Type System & Integer Semantics (highest ROI)

### A1 — Fixed-width types used where width matters (High)

- [ ] Register fields, protocol fields, storage formats, CRCs, counters that must not overflow use `uint*_t/int*_t`.
- [ ] `short` and `long` are not used.
- [ ] `char` is used only for strings; raw bytes use `uint8_t`.

**Common fixes**

- Replace ambiguous `int`/`long` with `int32_t` or `uint32_t` based on semantics.
- Replace `char` buffers carrying bytes with `uint8_t`.

---

### A2 — Signed/unsigned mixing is eliminated (Blocker → High)

- [ ] No comparisons between signed and unsigned without normalization.
- [ ] No arithmetic mixing signed/unsigned without explicit promotion to a common type.
- [ ] Unsigned decimal constants have `u` suffix where appropriate.

**Common fixes**

- Promote both operands once at the boundary:

```c
int32_t sum = (int32_t)a + (int32_t)b;
```

---

### A3 — Bitwise operations only on unsigned types (High)

- [ ] No `& | ^ ~ << >>` on signed integers.
- [ ] Right shifts of signed values are not relied upon for sign extension.

**Common fixes**

- Convert to unsigned before masking/shifting:

```c
uint32_t u = (uint32_t)signed_val;
u = (u >> SHIFT) & MASK;
```

---

### A4 — Casting is documented and bounded (High)

- [ ] Every cast has a comment explaining range safety and assumptions.
- [ ] Narrowing conversions are either prevented or guarded.

**Common fixes**

- Use range check + cast:

```c
if (val > UINT16_MAX)
{
    return ERR_RANGE;
}
/* Safe: val <= UINT16_MAX */
u16 = (uint16_t)val;
```

---

## B) Floating Point — If Present, Treat as High Risk

### B1 — No float equality/inequality tests (High)

- [ ] No `==` or `!=` comparisons on floats.
- [ ] Use epsilon range checks instead.

### B2 — Constant precision is explicit (High)

- [ ] Single-precision literals use `f` suffix.
- [ ] Double precision dependency is documented if required.

### B3 — Finite checks for unstable math (High)

- [ ] `isfinite()` (or project equivalent) used after division/sqrt/log, etc., where NaN/Inf can occur.

---

## C) Structs/Unions/Bitfields — Layout and ABI Portability

### C1 — Protocol and storage layouts are explicit (Blocker → High)

- [ ] Do not rely on implicit struct padding for wire/storage formats.
- [ ] If struct overlays are used for buses/protocols, layout is verified.

**Common fixes**

- Prefer manual packing/unpacking with masks and shifts for portable formats.
- Add compile-time size checks for overlays.

### C2 — Bitfields treated as non-portable by default (High)

- [ ] Bitfield ordering assumptions are not used for cross-compiler portability.
- [ ] If bitfields are used (fixed toolchain only), document the constraint and verify layout.

### C3 — MMIO overlays are correctly qualified (Blocker)

- [ ] MMIO access uses `volatile` correctly.
- [ ] Base register pointers are `* const` to prevent reassignment.
- [ ] Read-only registers represented as `const` fields where appropriate.

**Common pattern**

```c
static reg_t volatile * const p_reg = (reg_t volatile * const)BASE_ADDR;
```

---

## D) Concurrency & ISR Safety (most likely to cause “glitches”)

### D1 — Shared data is identified and protected (Blocker)

- [ ] Any object accessed from ISR and foreground is treated as shared state.
- [ ] Any object accessed from multiple threads/tasks is treated as shared state.

### D2 — `volatile` is necessary but not sufficient (Blocker)

- [ ] `volatile` is present for shared flags/counters/registers where required.
- [ ] Atomicity is ensured:
  - [ ] Multi-byte data updated asynchronously is read/written atomically or protected.

**Common fixes**

- Use critical sections around shared multi-byte reads/writes.
- Use “copy then process” patterns: copy shared state under protection, process without locks.

### D3 — ISR minimalism and determinism (High → Blocker)

- [ ] ISR does not block.
- [ ] ISR does not call non-ISR-safe APIs.
- [ ] ISR clears/acknowledges the interrupt source correctly.
- [ ] ISR defers heavy work (e.g., to task/foreground).

### D4 — Default handlers / unexpected interrupts (High)

- [ ] Unhandled vectors have a default ISR that asserts/logs and prevents silent faults.
- [ ] Behavior is defined (halt, safe state, watchdog strategy) per project policy.

---

## E) Control Flow Robustness (avoid fragile constructs)

### E1 — Braces everywhere (Blocker)

- [ ] Every control statement has braces, including single/empty statements.

### E2 — Conditionals are explicit and complete (High)

- [ ] No assignments inside condition tests.
- [ ] `if` + `else if` chains end with a final `else`.

### E3 — Switch statements are safe (High)

- [ ] `default` always present.
- [ ] Fall-through is commented.
- [ ] Breaks are visually obvious.

### E4 — Loops are bound to real sizes (High)

- [ ] No magic numbers for loop bounds.
- [ ] `for (;;)` used for intentional infinite loops.
- [ ] Empty loops use braces + explanatory comment.

---

## F) Header/Module Portability (linkage and coupling hazards)

### F1 — Headers do not allocate storage (Blocker)

- [ ] No variable definitions in headers.
- [ ] Avoid `extern` globals; prefer accessors/encapsulation.

### F2 — Prototype consistency is compiler-checked (High)

- [ ] `.c` includes its matching header.
- [ ] Public prototypes are declared in headers; private helpers are `static`.

---

## G) Timing, Delays, and Hardware Semantics (portability hotspot)

### G1 — Delay loops are documented (High)

- [ ] Delay loop counters use `volatile` when needed to prevent optimization removal.
- [ ] Empirical loop constants include `WARNING:` and portability note (clock/opt changes).

### G2 — Register semantics are documented (High)

- [ ] Write-1-to-clear (W1C), read-to-clear (R2C), and “dummy read” errata behaviors are documented with `NOTE:` referencing datasheet/errata.

### G3 — DMA/cache interactions (project-dependent, High)

- [ ] Buffer alignment and cache coherency assumptions documented where relevant.

---

## H) Deviation Hygiene (when portability conflicts with reality)

### H1 — Deviations are explicit and complete (High)

- [ ] Deviation comment contains:
  - rule reference, reason, risk, mitigation
  - Approved-by, Date (or placeholders per policy)
- [ ] Scope is minimal (line/function > module).

**Deviation token suggestion**

```c
/* DEVIATION (BARR-C X.Y):
 * Reason:
 * Risk:
 * Mitigation:
 * Approved-by:
 * Date:
 */
```

---

## “Stop-the-line” findings (immediate Changes Requested)

If any item below is true, the PR should not merge without fixes:

- [ ] ISR/thread shared state without `volatile` *and* without protection where atomicity is required
- [ ] Signed/unsigned mixing in non-trivial expressions or comparisons
- [ ] Missing braces on control structures
- [ ] Missing `default` in a `switch` that controls state/error handling
- [ ] Struct/union overlay used for MMIO/wire format without layout verification/justification
- [ ] Casts that can truncate/overflow without range proof/comment

---

## Reviewer output template (for safety/portability)

- **Portability risks:** (list + file/line)
- **Concurrency/ISR risks:** (list + file/line)
- **Hardware interface risks:** (list + file/line)
- **Required fixes (Blockers):** (bullets)
- **Recommended fixes (High):** (bullets)
- **Suggested automation:** (which check would prevent recurrence)
