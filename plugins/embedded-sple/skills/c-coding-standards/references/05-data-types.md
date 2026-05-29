# 05 — Data Type Rules (BARR‑C:2018, Chapter 5)

**Purpose:** Prevent portability defects and subtle runtime bugs caused by implementation‑defined integer widths, signed/unsigned mixing, floating‑point pitfalls, and layout ambiguity in structs/unions—especially for hardware/bus/network interfaces.
**Use this document when:** you see `char/short/int/long`, bitwise operations, bitfields, protocol packing, memory‑mapped I/O (MMIO) register overlays, floating‑point math, or boolean handling.

---

## 5.1 Data Type Naming Conventions

### What to check
- New data types (struct/union/enum typedefs) are:
  - **lowercase_with_underscores**
  - end with **`_t`**
- New structs/unions/enums are named via a **`typedef`**.
- Public data types are prefixed with **`<module>_`**.

### Why it matters
- Clear and consistent type naming reduces confusion between “type” and “instance”.
- Module prefixes reduce name collisions and improve encapsulation.

### Common failure modes
- Using `struct foo` directly without a typedef, leading to inconsistent naming.
- Public types without module prefix colliding across libraries.

### Preferred fixes (patterns)

**Good:**
```c
typedef struct
{
    uint16_t count;
    uint16_t max_count;
} timer_reg_t;
```

**Public type with module prefix:**
```c
typedef struct
{
    uint16_t raw;
    int16_t  celsius;
} sensor_temp_t; /* if public, prefer: sensor_temp_t */
```

---

## 5.2 Fixed‑Width Integers (Use stdint Types When Width Matters)

### What to check
- Wherever integer width matters (registers, wire formats, CRCs, counters that must not overflow):
  - use **fixed‑width types**: `int8_t/uint8_t`, `int16_t/uint16_t`, `int32_t/uint32_t`, `int64_t/uint64_t`
- **Do not use** `short` or `long`.
- Restrict use of `char` to **strings** (text).

### Why it matters
- `int`, `long`, etc. have **implementation‑defined widths**, varying by compiler/architecture.
- Porting code breaks when assumptions about width/overflow silently change.

### Common failure modes
- Protocol structs using `int` that changes size across platforms.
- Loop counters declared as `int` while the array size is `uint32_t`, causing signed/unsigned mixing.
- Using `char` for raw bytes (ambiguous signedness across compilers).

### Preferred fixes (patterns)

**Replace ambiguous types**
```c
/* Before */
long counter;

/* After */
uint32_t counter;
```

**Avoid `char` for raw bytes**
```c
/* Before */
char buffer[16]; /* ambiguous: string or bytes? */

/* After */
uint8_t buffer[16u]; /* for raw bytes */
```

**Use `char` for strings only**
```c
char const * const p_name = "UART0";
```

### Review tip
- If the code uses `sizeof(int)` or relies on `int` overflow/limits, treat as **high risk** and normalize to fixed widths.

---

## 5.3 Signed and Unsigned Integers (Avoid Mixing and Signed Bitwise Ops)

### What to check
- **No bit‑fields** declared within **signed** integer types.
- **No bitwise operators** (`& | ~ ^ << >>`) used on **signed** integer data.
- **Do not mix signed and unsigned** in:
  - comparisons
  - arithmetic expressions
  - ternary expressions
- Unsigned decimal constants meant to be unsigned include a `u` suffix (e.g., `6u`).

### Why it matters
- Signed bitwise shifts and mixed signed/unsigned conversions can be implementation‑defined or surprising due to integer promotions.
- Mixed essential types lead to bugs that are hard to spot in review and may vary by compiler.

### Common failure modes
- `if (len < 0u)` comparisons that are always false.
- `int16_t s; uint16_t u; if (s < u)` produces unexpected results after promotions.
- Right shift of negative signed values expecting arithmetic shift everywhere.

### Preferred fixes (patterns)

#### A) Normalize types before operations
```c
int16_t  s = -9;
int16_t  t = 6;

if ((int16_t)(s + t) < 4)
{
    ...
}
```

Better: choose a common signed type for the whole computation (often `int32_t`):
```c
int32_t sum = (int32_t)s + (int32_t)t;

if (sum < 4)
{
    ...
}
```

#### B) Use unsigned only when truly non‑negative
- Counters, sizes, bit masks: unsigned fixed‑width types.
- Values that can go negative: signed fixed‑width types.

#### C) Keep bitwise ops on unsigned types
```c
uint32_t flags = read_flags();

if (0u != (flags & READY_MASK))
{
    ...
}
```

#### D) Use explicit suffix for unsigned constants
```c
uint16_t timeout_ms = 1000u;
```

---

## 5.4 Floating Point (Avoid When Possible; If Used, Use Carefully)

### What to check
- Floating point is avoided unless necessary (consider fixed‑point math).
- If floating point is used:
  - Use the appropriate float type naming scheme used by the project (BARR‑C recommends C99 float type names when available).
  - Append `f` to single‑precision constants (e.g., `3.14f`).
  - Ensure the compiler/toolchain truly supports the required precision (especially `double`).
  - **Never compare floats for equality/inequality** directly.
  - Validate results are finite (e.g., `isfinite()`), especially after divisions or transforms.

### Why it matters
- Many MCUs lack hardware FP; emulation can be slow and code-size heavy.
- Float equality comparisons are unreliable due to rounding and representation.

### Common failure modes
- `if (x == 0.1)` style comparisons.
- Using `3.141592` without `f` causes double constants and unintended promotions.
- NaN/Inf propagation not detected; leads to downstream faults.

### Preferred fixes (patterns)

#### A) Use epsilon comparisons for “near equality”
```c
static float const EPS = 1.0e-5f;

if ((x > -EPS) && (x < EPS))
{
    ...
}
```

#### B) Guard against NaN/Inf
```c
if (!isfinite(x))
{
    return ERR_RANGE;
}
```

#### C) Consider fixed‑point
- If sensor scaling is stable (e.g., 0.01 units), represent as integer “centi-units”.

---

## 5.5 Structures and Unions (Layout, Padding, and Bitfields)

### What to check
- For structs/unions used to communicate with:
  - peripherals (MMIO register overlays)
  - buses
  - networks
  - storage formats
  ensure the compiler does not insert padding that breaks layout assumptions.
- For bitfields:
  - acknowledge **bit ordering** is not portable across compilers/targets
  - avoid bitfields in protocol/wire formats unless toolchain/target is fixed and verified
- Use compile‑time verification of struct size/layout where practical.

### Why it matters
- Struct padding and bitfield ordering are highly compiler/ABI dependent.
- A layout mismatch can corrupt hardware configuration or protocol messages.

### Common failure modes
- Assuming `sizeof(struct)` equals sum of members.
- Using bitfields in “wire format” structs and later porting to a different compiler.
- Overlaying MMIO with non‑volatile or incorrectly qualified pointers.

### Preferred fixes (patterns)

#### A) Prefer masks/shifts over bitfields for portable wire formats
```c
uint8_t flags = 0u;
flags |= (b_enabled ? ENABLE_MASK : 0u);
flags |= ((mode << MODE_SHIFT) & MODE_MASK);
```

#### B) If you must use register overlays, qualify correctly
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

#### C) Add compile-time size checks (choose a project convention)
- If C11 `_Static_assert` is available, use it; otherwise, use preprocessor checks.

```c
#if (8u != sizeof(timer_reg_t))
# error "timer_reg_t size incorrect (expected 8 bytes)"
#endif
```

#### D) Document endianness assumptions
```c
/* NOTE: Wire format is little-endian per protocol spec ABC-123, section 4.2. */
```

---

## 5.6 Booleans (Use `bool`; Convert via Relational Operators)

### What to check
- Boolean variables are declared as **`bool`** (from `<stdbool.h>`).
- Conversions to boolean are done via relational operators (`!=`, `<`, `>`, etc.), not casts.

### Why it matters
- Casting to `bool` can hide intent and may mask non‑zero “truthy” values that should be normalized.
- A relational expression communicates intent and improves readability.

### Common failure modes
- Using `uint8_t b_flag` without clear boolean semantics.
- Casting arbitrary integers to bool:
```c
bool b_ready = (bool)status;
```

### Preferred fixes (patterns)
```c
#include <stdbool.h>

bool b_in_motion = (0 != speed_mph);
bool b_valid     = (NULL != p_object);
```

If you must keep an integer type for ABI/HW reasons, enforce naming and normalization:
```c
uint8_t b_done_yet = (0u != raw_flag) ? 1u : 0u;
```

---

## Cross‑Cutting Guidance: Constants, Promotions, and “Type Hygiene”

### What to check
- Constants used with fixed-width unsigned types have a `u` suffix.
- Bit masks are the same type/width as the value they mask.
- Beware integer promotions in expressions involving `uint8_t`/`uint16_t`.
- Avoid implicit narrowing conversions in assignments.

### Preferred fixes
- Cast once, at the boundary, with a **range-safety comment** if needed.
- Use intermediate `uint32_t` or `int32_t` for arithmetic to avoid overflow surprises.

Example:
```c
uint16_t a = 60000u;
uint16_t b = 10000u;

/* WARNING: Promote to uint32_t to avoid overflow in 16-bit arithmetic. */
uint32_t sum = (uint32_t)a + (uint32_t)b;
```

---

## Automation & Enforcement (Practical Gates for Chapter 5)

### Recommended “cheap” checks
- Flag `short` and `long`:
  - `\b(short|long)\b`
- Flag non-string `char` usage (heuristic; requires review):
  - `\bchar\b` in non-string contexts
- Flag mixed signed/unsigned comparisons (best via static analysis):
  - compiler warnings + static analysis rule packs

### Static analysis targets (high value)
- Signed/unsigned mixing
- Narrowing conversions
- Bitwise ops on signed integers
- Uninitialized padding bytes in structs used for I/O (can cause nondeterministic behavior)
- Float equality comparisons

---

## Review Checklist (Copy/Paste)

- [ ] New types: lowercase_with_underscores, end in `_t`, typedef’d; public types module-prefixed
- [ ] Fixed-width integer types used where width matters; no `short`/`long`
- [ ] `char` reserved for strings; raw bytes use `uint8_t`
- [ ] No bitwise ops on signed ints; no signed bitfields
- [ ] No signed/unsigned mixing in expressions or comparisons; unsigned constants use `u`
- [ ] Floating point avoided where possible; if used: `f` suffix, no equality tests, finite checks where needed
- [ ] Struct/union layouts for MMIO/wire formats are verified; bitfield portability risks addressed
- [ ] Boolean variables use `bool`; integer→bool via relational operator, not casts
