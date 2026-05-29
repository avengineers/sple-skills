# 04 — Module Rules (BARR‑C:2018, Chapter 4)

**Purpose:** Keep modules cohesive, APIs clean, and coupling low—so the compiler and reviewers can catch defects early and maintenance remains predictable.
**Use this document when:** creating new `.c/.h` pairs, reviewing includes and visibility, restructuring modules, or enforcing file layout and naming.

---

## 4.1 Module Naming Conventions

### What to check
- Module file names use **only lowercase letters, digits, and underscores**.
- No spaces in file names.
- Module names are **unique in their first 8 characters** (helps cross-platform and tooling constraints).
- Header/source use standard suffixes: `.h` and `.c`.
- No header file name collides with standard library headers (e.g., avoid `stdio.h`, `math.h`).
- Any module containing `main()` includes `"main"` in the source filename.

### Why it matters
- Avoids cross-platform case-sensitivity problems (Windows vs Unix).
- Prevents name collisions and confusion in large builds.

### Common failure modes
- Mixed-case filenames: `UartDriver.c` vs `uartdriver.c` causing build or include issues.
- A module named like a standard header (`time.h`) causing accidental include ambiguity.
- Multiple modules with same first 8 chars in environments with constraints (older tools, archives).

### Preferred fixes (patterns)
- Rename `UartDriver.c` → `uart_driver.c`
- Rename `math.c` → `math_utils.c` (or better, domain-specific)

---

## 4.2 Header Files (Public Interface Discipline)

### What to check
1. **One-to-one pairing**
   - Every `.c` has exactly one corresponding `.h` with the same root name.
   - Example: `adc.c` ↔ `adc.h`

2. **Include guard present and portable**
   - Use:
     ```c
     #ifndef ADC_H
     #define ADC_H
     ...
     #endif /* ADC_H */
     ```
   - Avoid non-portable `#pragma once` when portability matters.

3. **Header exposes only what other modules must know**
   - Public API prototypes
   - Public types (`typedef`)
   - Public constants/macros that are necessary
   - **Avoid leaking private details** (private structs, private macros, internal constants)

4. **Preferred: no `extern` variable declarations in headers**
   - Strong preference is to avoid exposing global variables across modules.
   - If unavoidable, declare `extern` in header and define storage in exactly one `.c`.

5. **Never allocate storage in a header**
   - No variable definitions in headers (prevents multiple definitions across translation units).

6. **No public header includes a private header**
   - “Public” headers should not depend on “internal/private” headers that aren’t meant for external consumers.

### Why it matters
- Reduces dangerous coupling: fewer modules depend on internal details.
- Avoids multiple-definition linker issues.
- Keeps APIs stable and reviewable; prevents accidental use of internal symbols.

### Common failure modes
- **Defining globals in headers**
  ```c
  /* bad: foo.h */
  uint32_t g_counter = 0u;  /* allocates storage in every .c that includes foo.h */
  ```
- **Headers that include half the project**
  - Long include chains slow builds and increase coupling.
- **Headers exposing private macros**
  - Encourages misuse and makes refactors harder.

### Preferred fixes (patterns)

#### A) Replace `extern` globals with accessors (preferred)
**Before:**
```c
/* adc.h */
extern uint16_t g_adc_last_sample;
```

**After:**
```c
/* adc.h */
uint16_t adc_get_last_sample (void);
```

```c
/* adc.c */
static uint16_t g_adc_last_sample = 0u;

uint16_t adc_get_last_sample (void)
{
    return g_adc_last_sample;
}
```

#### B) If `extern` is unavoidable, keep it correct
```c
/* foo.h */
extern uint32_t g_counter;

/* foo.c */
uint32_t g_counter = 0u;
```

#### C) Keep private details out of the public header
- Move private `typedef struct { ... } internal_t;` into `.c` or a private header.
- Expose only an opaque handle if needed.

Opaque handle pattern:
```c
/* public header */
typedef struct widget_s widget_t;
widget_t * widget_create (void);
void       widget_destroy (widget_t * p_widget);
```

---

## 4.3 Source Files (Cohesion, Layout, and Includes)

### What to check

#### A) One “entity” per source file
Each `.c` should implement one cohesive unit:
- peripheral driver (UART, SPI)
- protocol layer (CAN transport, CRC)
- active object/task (if RTOS)
- encapsulated type

Avoid “god modules” that implement unrelated features.

#### B) File section order is consistent and readable
Recommended order:
1. File header comment block
2. `#include` statements
3. Type/constant/macro definitions
4. `static` data declarations
5. Private function prototypes
6. Public function bodies
7. Private function bodies

#### C) Include your own header in the `.c`
- `file.c` must `#include "file.h"` so the compiler can verify prototypes match definitions.

**Preferred include order inside `.c`:**
1. matching module header `"module.h"`
2. C standard headers `<stdint.h>`, `<stdbool.h>`, etc.
3. other project headers

This tends to expose missing includes and type dependencies earlier.

#### D) No absolute paths in includes
- Avoid `#include "/home/user/project/inc/foo.h"`
- Use project include paths configured in build system.

#### E) No unused includes
- Every included header should be required by that translation unit.

#### F) Never include another `.c` file
- `#include "other.c"` is forbidden.

### Why it matters
- Consistent structure reduces review time and helps engineers find what they need quickly.
- Including the matching header catches mismatched prototypes at compile-time.
- Avoiding `.c` inclusion prevents ODR-like duplication and build fragility.

### Common failure modes
- Public functions implemented without prototypes in header.
- Private helper functions not marked `static`.
- `.c` includes ordered such that missing includes are hidden.
- Many unused includes causing coupling and long rebuild times.

### Preferred fixes (patterns)

#### A) Enforce header inclusion and prototype checking
```c
#include "uart.h"     /* first: match prototypes */
#include <stdint.h>
#include <stdbool.h>
```

#### B) Remove unused includes
If `foo.c` includes `bar.h` but uses none of its declarations, remove it.

#### C) Mark private helpers `static`
```c
static uint16_t compute_crc (uint8_t const * const p_buf, uint16_t n_bytes);
```

#### D) Keep public functions above private ones
- Makes API discovery easier.
- Keeps the “what this module offers” visible early.

---

## 4.4 File Templates (Consistency for New Modules)

### What to check
- New `.h` and `.c` files are created from project templates that include:
  - Doxygen file headers
  - Copyright notices
  - Include guards in headers
  - End-of-file marker

### Why it matters
- Templates enforce consistent structure and avoid missing boilerplate (guards, includes, end markers).

### Preferred template skeletons

#### Header template
```c
/**
 * @file module.h
 * @brief Describe the module’s purpose.
 *
 * @par
 * COPYRIGHT NOTICE: (c) <YEAR> <COMPANY>. All rights reserved.
 */
#ifndef MODULE_H
#define MODULE_H

/* Public types, macros, and function prototypes go here. */

#endif /* MODULE_H */
/*** end of file ***/
```

#### Source template
```c
/**
 * @file module.c
 * @brief Describe the module’s purpose.
 *
 * @par
 * COPYRIGHT NOTICE: (c) <YEAR> <COMPANY>. All rights reserved.
 */
#include "module.h"
#include <stdint.h>
#include <stdbool.h>

/* Types/macros */

/* static data */

/* private prototypes */

/* public functions */

/* private functions */

/*** end of file ***/
```

---

## Automation & Enforcement (Practical Gates for Chapter 4)

### Recommended checks
- **Module naming check:** lowercase/underscore-only; `.c/.h` pairs exist.
- **Header guard check:** each `.h` contains a valid guard pattern.
- **Forbidden include check:** reject `#include` of `.c` files.
- **Unused include scan:** enable via static analysis or compiler warnings (where supported).
- **Visibility check:** warn when non-`static` functions are not declared in headers (project policy).

### Grep-style checks (cheap)
- Find `.c` includes:
  - search for: `#include ".*\.c"`
- Find missing `static` on private helpers (heuristic):
  - search for function definitions without `static` that are not in headers (requires tool support)

---

## Review Checklist (Copy/Paste)

- [ ] Filenames are lowercase_with_underscores; no stdlib header collisions
- [ ] One `.h` per `.c` with matching root name
- [ ] Header guard present; no storage allocated in headers
- [ ] Header exposes only necessary API; avoids `extern` globals (preferred)
- [ ] `.c` includes its own header (preferably first)
- [ ] No absolute include paths; no unused includes; never include `.c` files
- [ ] Module structure follows consistent section ordering
- [ ] Private functions are `static`; public functions are declared in the header
- [ ] New files start from templates and include end-of-file marker
