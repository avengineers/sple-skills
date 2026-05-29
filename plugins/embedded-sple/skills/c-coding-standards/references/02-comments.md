# 02 — Comment Rules (BARR‑C:2018, Chapter 2)

**Purpose:** Ensure comments *prevent defects* by documenting intent, assumptions, and hazards—without creating new risks (e.g., nested comment confusion) or drifting away from the code.
**Use this document when:** reviewing comment quality, preparing Doxygen documentation, removing commented-out code, or adding notes for safety/security/portability constraints.

---

## 2.1 Acceptable Formats (and What Is Forbidden)

### What to check
- **Allowed styles:** Both `/* ... */` and `// ...` are acceptable for comments.
- **Forbidden tokens inside comments:** Comments must not contain the preprocessor/comment tokens `/*`, `//`, or `\` *as literal sequences inside the comment text*, because they can confuse parsers or reviewers.
- **No commented-out code — ever:** Code should not be commented out, even temporarily.

### Why it matters
- Comment syntax pitfalls can hide compiled code or unintentionally comment out code.
- Commented-out code rots and becomes misleading, increasing maintenance defects.

### Common failure modes
- Nested comment disaster:
```c
/* This looks fine...
   /* but actually terminates badly */
   do_work();
*/
```

- Large commented-out blocks that reviewers must mentally “compile” to understand what’s active:
```c
// if (b_feature_enabled) {
//     do_feature();
// }
```

### Preferred fixes (patterns)

#### A) Temporarily disable code using conditional compilation
Use `#if 0` with a clear reason. Keep this rare and short-lived:
```c
#if 0  /* TEMP: disable until HW rev B arrives; see JIRA-1234 */
do_feature();
#endif
```

#### B) Debug-only code guarded with `#ifndef NDEBUG`
Surround debug output / extra checks with:
```c
#ifndef NDEBUG
log_debug_state();
#endif
```

#### C) Remove dead code
If it’s obsolete, delete it. Version control preserves history.

---

## 2.2 Locations and Content (Write Comments That Stay Useful)

### What to check
- Comments are written in **clear, complete sentences** with reasonable grammar and punctuation.
- Comments **precede** the code block they describe (especially algorithm steps).
- A **blank line follows** each commented “step block” to visually separate steps.
- Avoid explaining the obvious (assume the reader knows C).
- Comment volume is proportional to complexity: more complexity → more commentary; simple code → minimal commentary.
- External references (specs, datasheets, patents, standards) are cited sufficiently for someone to locate them.
- Diagrams/flowcharts that are necessary are version-controlled and referenced by filename/title.
- **Assumptions are explicitly stated.**
- Modules and functions have Doxygen-friendly comments for automated documentation.

### Why it matters
- Most embedded defects in maintenance come from misunderstanding intent, constraints, timing, hardware quirks, or assumptions.
- When comments capture “why” and constraints, they reduce the chance of unsafe “optimizations” later.

### Common failure modes
- Redundant “obvious” comments:
```c
x <<= 2;  // Shift x left by 2 bits.
```

- Misleading comments that drift from code behavior:
```c
// Read temperature in Celsius.
temp_f = adc_to_temp_f(raw); /* actually Fahrenheit */
```

- Comments that describe *how* but never *why*:
```c
// Set bit 3.
reg |= (1u << 3); /* Why bit 3? What does it mean? */
```

### Preferred comment placement pattern (algorithm steps)
Use “Step” comments for multi-step logic. Keep them aligned with the block:
```c
/* Step 1: Validate the input buffer and length. */
if ((NULL == p_buf) || (0u == n_bytes))
{
    return ERR_INVALID_ARG;
}

/* Step 2: Compute the checksum over the buffer. */
checksum = checksum_compute(p_buf, n_bytes);

```

---

## Doxygen-Ready Module and Function Comments

### What to check
- Each public module (`.h` and often `.c`) has a Doxygen file header.
- Each public function has:
  - `@brief`
  - parameter direction (`[in]`, `[out]`, `[in,out]`)
  - return description
  - assumptions/preconditions if important

### Preferred templates

#### Module header (file-level)
```c
/**
 * @file uart.h
 * @brief UART driver public API.
 *
 * @par
 * COPYRIGHT NOTICE: (c) <YEAR> <COMPANY>. All rights reserved.
 */
```

#### Public API function
```c
/**
 * @brief Transmit a buffer over UART.
 *
 * @param[in]  p_buf    Pointer to the data to transmit.
 * @param[in]  n_bytes  Number of bytes to transmit.
 *
 * @return 0 on success; negative error code on failure.
 *
 * @note This function is non-blocking when UART_TX_DMA is enabled.
 */
int uart_tx (uint8_t const * const p_buf, uint16_t n_bytes);
```

---

## Comment Markers: WARNING / NOTE / TODO

### What to check
Use these exact markers to highlight important maintenance signals:

- **WARNING:** There is risk in changing this code; changing it may break timing, safety, or portability.
- **NOTE:** Explains *why* something is done (especially deviations from datasheets/specs).
- **TODO:** Work remains; include what remains and optionally initials.

### Preferred examples

#### WARNING for empirically tuned timing
```c
/* WARNING: Delay loop count is empirically tuned for 48 MHz at -O2.
 * Re-evaluate if clock or optimization level changes.
 */
for (volatile uint32_t i = 0u; i < DELAY_COUNT; i++)
{
    /* Intentional delay. */
}
```

#### NOTE for datasheet errata
```c
/* NOTE: Datasheet rev C errata E-17 requires a dummy read after reset. */
(void)*p_status_reg;
```

#### TODO with ownership
```c
/* TODO(MD): Add CRC-32 option when bootloader protocol is finalized. */
```

---

## Assumptions: Make Them Explicit (and Keep Them Close)

### What to check
If correctness depends on assumptions, the assumptions must be written down near the code:
- type widths / overflow expectations
- endianness assumptions
- register semantics (write-1-to-clear, read-to-clear)
- timing or ISR rate assumptions
- concurrency assumptions (single writer / multiple readers, atomicity)

### Preferred pattern
```c
/* NOTE: Assumes 16-bit register access is atomic on this MCU family.
 * If ported to an 8-bit MCU, protect reads with a critical section.
 */
value = g_shared_u16;
```

---

## Avoid “Comment Rot”: Techniques to Keep Comments Accurate

### What to check
- Comments describe *intent* rather than duplicating code structure.
- Comments are updated when code behavior changes.
- If reviewers ask “what does this do?”, add a clarifying comment nearby.

### Preferred fixes
- Replace brittle comments with assertions or design-by-contract checks where feasible:
```c
/* NOTE: n_bytes must be <= UART_TX_MAX_BYTES. */
ASSERT(n_bytes <= UART_TX_MAX_BYTES);
```

---

## Review Checklist (Copy/Paste)

- [ ] No commented-out code; temporary disabling uses `#if 0` with reason
- [ ] Debug-only blocks use `#ifndef NDEBUG`
- [ ] Comments are complete sentences; minimal “obvious” commentary
- [ ] Algorithm steps are commented above the blocks; blank line separates steps
- [ ] Assumptions (timing, widths, concurrency, HW semantics) are spelled out
- [ ] External references are identifiable (doc ID + section if possible)
- [ ] Doxygen file/function comments exist for public APIs
- [ ] WARNING/NOTE/TODO markers used appropriately
