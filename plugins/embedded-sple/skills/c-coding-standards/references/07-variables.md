# 07 — Variable Rules (BARR‑C:2018, Chapter 7)

**Purpose:** Reduce defects caused by unclear naming, unintended coupling, uninitialized data, and pointer misuse—especially around globals, concurrency, and memory‑mapped I/O.
**Use this document when:** reviewing variable naming and scope, auditing initialization, handling pointers/handles, or dealing with ISR/thread‑shared state.

---

## 7.1 Variable Naming Conventions

### What to check
- **No reserved/keyword names:** Variables must not use names that collide with C/C++ keywords or common extensions.
- **No Standard Library collisions:** Do not reuse names like `errno`.
- **No leading underscore:** Variable names must not begin with `_`.
- **Length bounds:** Names are **≤ 31 characters** and **≥ 3 characters** (including loop counters).
- **Lowercase only:** No uppercase letters in variable names.
- **No embedded “magic numbers” in names:** Don’t bake numeric facts into names when they exist elsewhere (array size, bit width, etc.).
- **Underscores separate words.**
- **Names are descriptive of purpose** (avoid `tmp`, `val`, `foo` except in truly narrow scopes).

### Required prefixes (encode risk and usage)
Use these prefixes consistently:

- **Global variables** start with `g`
  Example: `g_zero_offset`
- **Pointer variables** start with `p`
  Example: `p_led_reg`
- **Pointer-to-pointer variables** start with `pp`
  Example: `pp_vector_table`
- **Integer variables containing Boolean information** start with `b` and read like a question
  Examples: `b_done_yet`, `b_is_buffer_full`
- **Non-pointer handles** start with `h`
  Example: `h_input_file`

If multiple prefixes apply, order is:
`[g][p/pp][b/h]` (then underscore, then rest of name)

### Why it matters
- Naming rules prevent collisions and ensure portability across toolchains with identifier limitations.
- Prefixing makes risk visible: globals and pointers need extra scrutiny; boolean-integers should be normalized and treated carefully.

### Common failure modes
- Loop counters named `i` (too short) or `I` (uppercase) in complex loops.
- Globals named without `g_`, hiding coupling and concurrency risks.
- Pointers named without `p_`, hiding nullability and aliasing risks.
- Boolean-ish values stored in ints without `b_`, causing “truthiness” misuse.

### Preferred fixes (patterns)

**Before (ambiguous intent):**
```c
uint16_t value;
uint8_t flag;
uint32_t counter;
uint8_t * buf;
```

**After (clear intent + risk encoded):**
```c
uint16_t sample_value;
uint8_t  b_is_valid;
uint32_t retry_count;
uint8_t * p_buf;
```

**Global + pointer + boolean order example:**
```c
static volatile uint8_t gpb_is_rx_ready = 0u; /* global + pointer + boolean pattern */
```

> **Tip:** Avoid piling prefixes unless it genuinely reduces confusion. If a variable name becomes awkward, consider refactoring the design (e.g., eliminate global, pass pointers explicitly, use accessor functions).

---

## 7.2 Initialization (Always Initialize Before Use)

### What to check
- **All variables are initialized before use** (locals, statics, globals).
- Preferred practice: **declare locals near first use** (C99 supports this) rather than at the top of the function.
- **File-scope variables** (project/global) are grouped together at the top of the `.c`.
- **Pointers without initial address are initialized to `NULL`.**

### Why it matters
- Uninitialized variables are a major embedded defect source; startup code does not always guarantee safe defaults for every context.
- Declaring near use reduces back‑and‑forth eye movement during reviews and lowers misunderstanding risk.

### Common failure modes
- Local variables declared but only conditionally initialized, then used on another path.
- Pointer variables used without guaranteed assignment.
- Assuming “globals start at zero” in all runtime environments.
- Mixing declarations and logic far apart, causing reviewers to miss initialization.

### Preferred fixes (patterns)

#### A) Initialize on declaration (most common)
```c
uint16_t checksum = 0u;
int      rc       = ERR_OK;
```

#### B) Declare near first use
```c
if (b_need_crc)
{
    uint16_t crc = crc_compute(p_buf, n_bytes);
    send_crc(crc);
}
```

#### C) Null-init pointers when “no address yet”
```c
uint8_t * p_buf = NULL;

p_buf = alloc();
if (NULL == p_buf)
{
    return ERR_NO_MEM;
}
```

#### D) Group file-scope variables together (top of `.c`)
```c
/* static data */
static volatile uint8_t  g_uart_rx_ready = 0u;
static uint16_t          g_uart_last_rx  = 0u;
static uint8_t           g_rx_buf[RX_BUF_BYTES];
```

---

## Additional Guidance: Scope, Lifetime, and Encapsulation

### What to check
- Prefer the **smallest scope** that works:
  - local variables over globals
  - `static` file-scope over exported globals
- Avoid exposing variables across modules; prefer accessor functions and encapsulated state.

### Why it matters
- Reduces coupling and prevents unintended writes from other modules.
- Makes concurrency/race analysis manageable.

### Preferred fixes (patterns)
- Convert exported globals to `static` + accessor:
```c
/* before: exported global */
uint16_t g_last_sample;

/* after: private + accessor */
static uint16_t g_last_sample = 0u;

uint16_t adc_get_last_sample (void)
{
    return g_last_sample;
}
```

---

## Boolean-in-Integer Variables: Normalize and Guard

### What to check
- If a boolean is stored in an integer type (ABI/HW/packing reasons), ensure:
  - name begins with `b_`
  - values are normalized to `0` or `1` (or clearly documented allowed set)
  - comparisons are explicit (`0u != b_flag`) rather than “truthy” use

### Preferred pattern
```c
uint8_t b_is_ready = (0u != raw_flag) ? 1u : 0u;

if (0u != b_is_ready)
{
    ...
}
```

---

## Pointer Variables: Safety and Readability

### What to check
- Pointer names begin with `p_` (or `pp_`).
- Pointers are initialized (`NULL` if not yet assigned).
- Null checks use constant-on-left style when comparing to constants:
  - `NULL == p_buf` rather than `p_buf == NULL`
- `const` correctness applied:
  - `uint8_t const *` for read-only buffers
  - `type volatile * const` for MMIO pointers

### Common failure modes
- Returning pointers to stack locals.
- Using pointers before null checks.
- Confusing pointer constness (const pointer vs pointer-to-const).

### Preferred patterns

**Read-only buffer parameter:**
```c
int parse_msg (uint8_t const * const p_buf, uint16_t n_bytes);
```

**MMIO pointer (example):**
```c
static reg_block_t volatile * const p_regs =
    (reg_block_t volatile * const)REG_BASE;
```

---

## Automation & Enforcement (Practical Gates for Chapter 7)

### Recommended “cheap” checks
- Flag uppercase in variable names (heuristic; review needed).
- Flag very short identifiers (length < 3) outside tightly-scoped loops:
  - consider a linter rule or review gate.
- Flag leading underscore identifiers:
  - `\b_[A-Za-z0-9_]+\b`

### Static analysis targets (high value)
- Use-before-initialization
- Null dereference paths
- Escaped address of stack variable
- Unused variables and shadowing (project policy dependent)
- Volatile access patterns (read-modify-write hazards)

---

## Review Checklist (Copy/Paste)

- [ ] Names: lowercase_with_underscores; 3–31 chars; no leading underscore; no keyword/stdlib collisions
- [ ] Globals start with `g_`; pointers with `p_`; pointer-to-pointer with `pp_`; handles with `h_`
- [ ] Boolean-in-integer starts with `b_` and is normalized to 0/1 (or documented allowed values)
- [ ] No embedded magic numbers in names (sizes/widths expressed elsewhere)
- [ ] All variables initialized before use; pointers NULL-initialized when unassigned
- [ ] Locals declared near first use; file-scope variables grouped at top of `.c`
- [ ] Prefer minimal scope; avoid exported globals; use accessors/encapsulation
- [ ] Pointer const/volatile usage correct; null checks are explicit and readable
