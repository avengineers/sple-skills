# 03 — White Space Rules (BARR‑C:2018, Chapter 3)

**Purpose:** Enforce consistent whitespace and layout so code is easier to read, review, diff, and maintain—while also making certain defect patterns more visible.
**Use this document when:** formatting new modules, reviewing style drift, preparing a whitespace-only cleanup commit, or adding automated formatting gates.

> **Important workflow rule:** If you must reformat legacy code, keep whitespace-only changes in a **separate commit** from functional changes to preserve clean diffs during review.

---

## 3.1 Spaces (Operator and Token Spacing)

### What to check
- **Control keywords** followed by one space when additional text follows:
  `if`, `while`, `for`, `switch`, `return`
- **Assignment operators** have spaces on both sides:
  `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `|=`, `^=`, `~=`, `!=`
- **Binary operators** have spaces on both sides:
  `+ - * / % < <= > >= == != << >> & | ^ && ||`
- **Unary operators** have no space between operator and operand:
  `+ - ++ -- ! ~`
- **Pointer operators in declarations** use spaces around `*` and `&`; in expressions, no space on operand side:
  - Declaration: `uint8_t * p_buf;`
  - Expression: `*p_buf = value;`
- **Ternary `?:`** has spaces around `?` and `:`
- **Member access** has no spaces: `p->field`, `s.field`
- **Array subscript** has no spaces: `arr[idx]`
- **Parentheses** have no internal padding: `if (x)` not `if ( x )`
- **Function calls** have no space before `(`: `f(x)`
- **Function declarations** include one space between function name and `(` so the name is easier to locate: `int foo (int x);`
- **Commas** followed by exactly one space (unless end-of-line)
- **for(;;)** semicolons followed by one space: `for (i = 0; i < n; i++)`
- **Semicolons** have no leading space: `x = 1;`

### Why it matters
- Consistent spacing reduces eyestrain and makes review patterns predictable.
- Proper spacing highlights suspicious constructs (e.g., `if (x=1)` vs `if (x == 1)`).

### Common failure modes
- Missing spaces around operators:
```c
count+=1;
if(a&&b){...}
```

- Incorrect spacing around pointer declaration or dereference:
```c
uint8_t* p;     /* hard to scan */
* p = 7u;       /* visually confusing */
```

- Extra spaces inside parentheses:
```c
if ( a < b )
{
    ...
}
```

### Preferred fixes (patterns)
**Before:**
```c
if(a&&b){x+=1;}
```

**After:**
```c
if ((a) && (b))
{
    x += 1;
}
```

**Pointer declaration vs dereference:**
```c
uint8_t * p_buf = NULL;
*p_buf = value;
```

---

## 3.2 Alignment (Visual Grouping and Scanability)

### What to check
- In consecutive declarations, align the **variable names** (first character aligned).
- In structs/unions, align the **member names**.
- In adjacent assignment statements, align the **assignment operators** where it improves readability.
- Preprocessor `#` appears at the start of a line (column 0).
  Directives may be indented *within* a `#if/#ifdef` block, but the `#` itself stays at column 0.

### Why it matters
- Alignment makes it obvious which lines are “the same kind of thing,” improving scan speed and reducing review mistakes.

### Common failure modes
- Mixed indentation and misaligned declaration blocks:
```c
uint8_t a;
uint16_t  longer_name;
uint32_t x;
```

- Preprocessor directives indented with spaces before `#`:
```c
  #define FOO 1
```

### Preferred fixes (patterns)

**Aligned declarations:**
```c
uint8_t  mode;
uint16_t timeout_ms;
uint32_t retry_count;
```

**Aligned struct members:**
```c
typedef struct
{
    uint16_t count;
    uint16_t max_count;
    uint16_t control;
} timer_reg_t;
```

**Aligned assignments (when adjacent and related):**
```c
rx_count   = 0u;
tx_count   = 0u;
err_count  = 0u;
last_error = ERR_NONE;
```

**Preprocessor at column 0:**
```c
#ifdef USE_SMALL_BUFFER
# define BUFFER_BYTES 64u
#else
# define BUFFER_BYTES 128u
#endif
```

---

## 3.3 Blank Lines (One Statement Per Line + Natural Blocks)

### What to check
- **One statement per line** (no `x++; y++;`).
- Blank line **before and after** each “natural block” such as:
  - loops
  - `if/else` blocks
  - `switch` blocks
  - consecutive declarations
  - consecutive related assignments
- Each source file ends with:
  - an explicit end-of-file comment, followed by
  - a final blank line

### Why it matters
- One statement per line reduces “hidden logic” and makes diffs cleaner.
- Blank lines create visual separation so reviewers see structure immediately.
- End-of-file markers reduce confusion in printed reviews and ensure a trailing newline exists.

### Common failure modes
- Multiple statements on one line:
```c
x++; y++; z++;
```

- No separation between unrelated blocks:
```c
init();
for (...) { ... }
shutdown();
```

- Missing end-of-file marker and/or trailing newline.

### Preferred fixes (patterns)

**One statement per line:**
```c
x++;
y++;
z++;
```

**Natural block separation:**
```c
init();

for (int idx = 0; idx < n_items; idx++)
{
    process(items[idx]);
}

shutdown();
```

**End-of-file marker:**
```c
/*** end of file ***/
```

---

## 3.4 Indentation (4-Space Multiples + Switch Formatting)

### What to check
- Indentation levels align at **multiples of 4 spaces**.
- Inside a `switch`:
  - `case` labels are aligned
  - contents of each case are indented one level
- For wrapped lines (when exceeding 80 columns), indent continuation lines to maximize readability and maintain logical grouping.

### Why it matters
- Consistent indentation prevents logic misreads (especially in nested control flows).
- Proper `switch` formatting makes missing `break` statements easier to spot.

### Common failure modes
- Mixed 2/3/4/8 space indents.
- `case` blocks with inconsistent indentation.
- Wrapped lines that align poorly, obscuring conditions.

### Preferred fixes (patterns)

**Switch formatting:**
```c
switch (err)
{
    case ERR_A:
        handle_a();
        break;

    case ERR_B:
        handle_b();
        break;

    default:
        handle_default();
        break;
}
```

**Readable wrapping of complex conditions:**
```c
if (((first_condition) && (second_condition)) ||
    ((third_condition) && (fourth_condition)))
{
    ...
}
```

---

## 3.5 Tabs (Forbidden)

### What to check
- The literal tab character (ASCII `0x09`) must never appear in any source code file.

### Why it matters
- Tab width varies by editor/settings, causing inconsistent alignment during review and maintenance.

### Common failure modes
- Tabs mixed into indentation or alignment:
  - looks aligned in one editor, misaligned in another
- Copy/paste from external sources introducing tabs

### Preferred fixes (patterns)
- Configure editor to insert spaces when Tab is pressed.
- Add pre-commit/CI checks to reject tabs.
- When embedding a tab in a *string literal*, use `\t`:
```c
#define MSG "Value:\t"
```

---

## 3.6 Non‑Printing Characters (Line Endings and Allowed Control Chars)

### What to check
- Prefer lines end with **LF** only (`0x0A`) rather than CRLF.
- The only other allowed non-printing character is **FF** (`0x0C`) when intentionally used (e.g., page breaks for printed reviews).

### Why it matters
- Mixed line endings can break some build tools and complicate diffs.
- CRLF can cause issues with certain multi-line macro patterns on Unix-like toolchains.

### Preferred fixes (patterns)
- Normalize line endings via repository settings (e.g., `.gitattributes`) and editor configuration.
- If using FF for page breaks (rare), keep it intentional and documented.

---

## Automation & Enforcement (Practical Gates for Chapter 3)

### Recommended “cheap” checks
- **Reject tabs:** search for `\t`
- **Line width:** flag lines > 80 chars (allow exceptions only via documented deviation)
- **Trailing whitespace:** flag trailing spaces
- **Missing final newline:** ensure file ends with newline
- **CRLF normalization:** enforce LF where your toolchain permits

### Whitespace-only change discipline
- If doing bulk formatting on legacy code:
  1. Make a **whitespace-only commit** (no logic changes).
  2. Then make functional changes in a separate commit.

---

## Review Checklist (Copy/Paste)

- [ ] Operator/keyword spacing follows consistent rules (readable and predictable)
- [ ] Declarations/struct members/assignments aligned where adjacent and related
- [ ] One statement per line; blank lines around natural blocks
- [ ] Indentation uses 4-space multiples; switch/case formatting consistent
- [ ] No tabs in source files
- [ ] LF line endings (where feasible); only FF permitted as special control char
- [ ] End-of-file marker present and file ends with a trailing blank line
