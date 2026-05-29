# HW Register Testing

Testing code that directly accesses hardware registers (memory-mapped I/O, peripheral status registers, write-only command registers) requires a substitution mechanism that redirects register access to controllable test variables.

Three approaches are available. Pick the one that fits how your production code accesses the register.

## Table of Contents

| Section | Line | When to read |
|---------|------|--------------|
| [Choosing the Right Approach](#choosing-the-right-approach) | ~15 | Always — decision matrix |
| [Common: File Structure](#common-file-structure) | ~40 | Always — directory layout |
| [Approach A: Macro Substitution](#approach-a-macro-substitution) | ~60 | Raw pointer casts, component-owned addresses |
| [Rules (both approaches)](#rules-both-approaches) | ~310 | After reading A or B |
| [Approach B: Function Spy](#approach-b-function-spy) | ~320 | Internal write helper functions |
| [Real-World Example (Approach A)](#real-world-example-approach-a) | ~475 | Need a concrete reference |
| [Approach C: Header Replacement](#approach-c-header-replacement) | ~485 | Named BSP register symbols |

---

## Choosing the Right Approach

**Look at how the production code accesses the register:**

```
Production code does:                            → Use:
──────────────────────────────────────────────────────────────────────────────
<PERIPH>_STATUS.U  (named BSP symbol, read)     → Approach C (Header Replacement) ← cleanest
<PERIPH>_STATUS.U  (named BSP symbol, write)    → Approach C if single write; A or B for sequences
*(volatile uint32*)ADDR = val (raw cast)         → Approach A (Macro Substitution)
Comp_WriteReg(ADDR, val)  ← own function         → Approach B (Function Spy)
HAL_WriteReg(ADDR, val)   ← external dep.        → standard hammocking, no guard needed
```

| | Approach A | Approach B | Approach C |
|---|---|---|---|
| **Production code change** | none | wrap function body | none |
| **Build system change** | none | none | add stub include path |
| **Test substitution level** | macro in header | function body | entire BSP header file |
| **Sequence write testing** | ✅ log array | ✅ log array | ⚠️ last value only |
| **Bitfield `.B.x` access** | needs type stubs in header | not needed | ✅ full union in stub header |
| **`#ifdef SPLE_UNIT_TESTING` in prod code** | header only | `.c` function body | nowhere |
| **Best for** | raw pointer casts, component-owned addresses | existing internal write helper | named BSP register symbols (`<Peripheral>_reg.h`) |

**Rule of thumb**: If the register symbol comes from a BSP/MCAL header (`<Peripheral>_reg.h`), use **Approach C**. If your component defines the address itself with a raw cast, use **Approach A**.

---

## Common: File Structure

```
components/<name>/src/
    <Component>.c               ← production code (no change for A and C; minimal for B)
    <Component>HwInterfaces.h   ← Approach A/B: register access header with guard
    <Component>HwInterfaces.c   ← Approach A/B: test helper implementation (entire file guarded)

test/
    hw_stubs/                   ← Approach C: stub headers, one per replaced BSP header
        <Peripheral>_reg.h      ← same filename as real BSP header
        <OtherPeriph>_reg.h
        hw_stubs.c              ← defines the global test variables
```

---

## Approach A: Macro Substitution

### When to use

Production code writes registers directly with pointer casts or BSP structs:

```c
*(volatile uint32*)(<COMP>_PROTECTION_ADDR) = value;
<PERIPH>_STATUS.U;   /* BSP register struct from <Peripheral>_reg.h */
```

### Header (`<Component>HwInterfaces.h`)

```c
#ifndef <COMPONENT>_HW_INTERFACES_H_
#define <COMPONENT>_HW_INTERFACES_H_

/* ---- register addresses and constants (always visible) ---- */
#define <COMP>_REG_CMD_ADDR       ((uint32) 0xABCD0000u)
#define <COMP>_REG_STATUS_ADDR    ((uint32) 0xABCD0004u)
#define <COMP>_STATUS_BUSY        ((uint32) 0x00000001u)
#define <COMP>_STATUS_READY       ((uint32) 0x00000000u)

#ifndef SPLE_UNIT_TESTING

/* ---- production: real BSP headers + raw register access ---- */
#include "<Peripheral>_reg.h"

#define <COMP>_WRITE_CMD_REG(val)      (*(volatile uint32*)(<COMP>_REG_CMD_ADDR) = (val))
#define <COMP>_READ_STATUS_REG()       (PERIPHERAL_STATUS.U)

#else /* SPLE_UNIT_TESTING */

/* ---- test: variable-backed register simulation ---- */

/* Maximum number of sequential reads to simulate (status polling) */
#define <COMP>_TEST_STATUS_SEQ_MAX  ((uint8) 10u)

/* Maximum number of writes to log (write-only registers) */
#define <COMP>_TEST_CMD_LOG_MAX     ((uint8) 16u)

/* Test variables — accessible from test file via extern */
extern uint32 <comp>_test_cmd_log[<COMP>_TEST_CMD_LOG_MAX];
extern uint8  <comp>_test_cmd_log_index;
extern uint32 <comp>_test_status_seq[<COMP>_TEST_STATUS_SEQ_MAX];

/* Test helper functions */
extern void   <comp>_test_reset_cmd_log(void);
extern void   <comp>_test_log_cmd_write(uint32 value);
extern uint32 <comp>_test_read_status(void);
extern void   <comp>_test_reset_status_seq(void);

/* Macro substitutions */
#define <COMP>_WRITE_CMD_REG(val)    (<comp>_test_log_cmd_write(val))
#define <COMP>_READ_STATUS_REG()     (<comp>_test_read_status())

/* --- Type stubs replacing BSP union/bitfield types --- */
typedef union {
    uint32 U;
    sint32 I;
} PERIPHERAL_STATUS_t;

/* Add further BSP type stubs here as needed */

#endif /* SPLE_UNIT_TESTING */

#endif /* <COMPONENT>_HW_INTERFACES_H_ */
```

---

### Implementation (`<Component>HwInterfaces.c`)

```c
#ifdef SPLE_UNIT_TESTING

#include "Std_Types.h"
#include "<Component>HwInterfaces.h"

/* ---- write-log for command/unlock registers ---- */

uint32 <comp>_test_cmd_log[<COMP>_TEST_CMD_LOG_MAX]  = {0u};
uint8  <comp>_test_cmd_log_index                     = 0u;

void <comp>_test_reset_cmd_log(void)
{
    uint8 i;
    for (i = 0u; i < <COMP>_TEST_CMD_LOG_MAX; i++)
    {
        <comp>_test_cmd_log[i] = 0u;
    }
    <comp>_test_cmd_log_index = 0u;
}

void <comp>_test_log_cmd_write(uint32 value)
{
    if (<comp>_test_cmd_log_index < <COMP>_TEST_CMD_LOG_MAX)
    {
        <comp>_test_cmd_log[<comp>_test_cmd_log_index] = value;
        <comp>_test_cmd_log_index++;
    }
}

/* ---- sequential read simulation for status/polling registers ---- */

uint32         <comp>_test_status_seq[<COMP>_TEST_STATUS_SEQ_MAX] = {0u};
static uint8   <comp>_test_status_seq_index                       = 0u;

uint32 <comp>_test_read_status(void)
{
    uint32 ret = 0u;
    if (<comp>_test_status_seq_index < <COMP>_TEST_STATUS_SEQ_MAX)
    {
        ret = <comp>_test_status_seq[<comp>_test_status_seq_index];
        <comp>_test_status_seq_index++;
    }
    return ret;
}

void <comp>_test_reset_status_seq(void)
{
    uint8 i;
    for (i = 0u; i < <COMP>_TEST_STATUS_SEQ_MAX; i++)
    {
        <comp>_test_status_seq[i] = 0u;
    }
    <comp>_test_status_seq_index = 0u;
}

#endif /* SPLE_UNIT_TESTING */
```

---

### Test File

```cpp
#include <gtest/gtest.h>
using namespace testing;

extern "C"
{
#include "<Component>.h"
#include "<Component>HwInterfaces.h"
}

#include "mockup_components_<path>_<Component>.h"

/*!
 * @rst
 * .. test:: <Component>Test.RegisterWriteSequence
 *    :id: TS_<COMP>-001
 *    :tests: SWDD_<COMP>-100
 *
 * Verifies that the command register is written in the correct order
 * and the status register is polled until ready.
 * @endrst
 */
TEST(<Component>Test, RegisterWriteSequence)
{
    /* Declare access to test variables (defined in HwInterfaces.c) */
    extern uint32 <comp>_test_cmd_log[];
    extern uint8  <comp>_test_cmd_log_index;
    extern uint32 <comp>_test_status_seq[];
    extern void   <comp>_test_reset_cmd_log(void);
    extern void   <comp>_test_reset_status_seq(void);

    CREATE_MOCK(mockups);

    /* GIVEN: Register log is clean */
    <comp>_test_reset_cmd_log();
    <comp>_test_reset_status_seq();

    /* GIVEN: Status register returns "busy" once, then "ready" */
    <comp>_test_status_seq[0] = <COMP>_STATUS_BUSY;
    <comp>_test_status_seq[1] = <COMP>_STATUS_READY;

    /* WHEN: Component function that touches HW registers is called */
    <Component>_ExecuteCommand(EXPECTED_CMD_VALUE);

    /* THEN: Correct number of writes logged */
    EXPECT_EQ(<comp>_test_cmd_log_index, EXPECTED_WRITE_COUNT)
        << "Unexpected number of register writes";

    /* THEN: First write was the command value */
    EXPECT_EQ(<comp>_test_cmd_log[0], EXPECTED_CMD_VALUE)
        << "Command register write mismatch";
}
```

---

### Patterns

### Write-Only Registers (e.g. unlock sequences, command registers)

Use the **log array** pattern: every write appends to `<comp>_test_cmd_log[]`. After calling the production function, assert:
- `_log_index` equals the expected write count
- each `_log[i]` equals the expected value in order

```cpp
EXPECT_EQ(<comp>_test_cmd_log_index, 3u) << "Expected exactly 3 writes";
EXPECT_EQ(<comp>_test_cmd_log[0], CMD_START);
EXPECT_EQ(<comp>_test_cmd_log[1], CMD_DATA);
EXPECT_EQ(<comp>_test_cmd_log[2], CMD_COMMIT);
```

### Status / Polling Registers (read until condition)

Pre-load the `_status_seq[]` array with the sequence the production code will read. The counter advances on every call to `<comp>_test_read_status()`.

```cpp
/* Simulate: first two reads return BUSY, third returns READY */
<comp>_test_status_seq[0] = <COMP>_STATUS_BUSY;
<comp>_test_status_seq[1] = <COMP>_STATUS_BUSY;
<comp>_test_status_seq[2] = <COMP>_STATUS_READY;
```

### Readable Registers with Bitfields

When production code uses `REG.B.SomeBit`, define the union type stub in the `SPLE_UNIT_TESTING` block of the header and expose a global test variable:

```c
/* In header under SPLE_UNIT_TESTING */
typedef struct { uint32 SomeBit : 1; } PERIPHERAL_CTRL_bits;
typedef union {
    uint32             U;
    PERIPHERAL_CTRL_bits B;
} PERIPHERAL_CTRL_t;

extern PERIPHERAL_CTRL_t PERIPHERAL_CTRL;
#define <COMP>_READ_CTRL_REG()   (PERIPHERAL_CTRL.U)
```

```c
/* In HwInterfaces.c under SPLE_UNIT_TESTING */
PERIPHERAL_CTRL_t PERIPHERAL_CTRL = {0u};
```

```cpp
/* In test: set individual bit fields */
PERIPHERAL_CTRL.B.SomeBit = 1u;
<Component>_CheckProtection();
EXPECT_EQ(result, EXPECTED);
```

---

## Rules (both approaches)

1. **`SPLE_UNIT_TESTING` is the only switch** — never add component-specific test switches.
2. **Constants and addresses go above the `#ifndef`** — always visible in both builds.
3. **No test code in production headers** — everything test-specific lives inside `#else`.
4. **`HwInterfaces.c` is fully guarded** — `#ifdef SPLE_UNIT_TESTING` wraps the entire file.
5. **Always reset before each test** — call all `_reset_*()` helpers in the Arrange section.
6. **BSP type stubs are minimal** — only define what the component actually uses (Approach A only).
7. **Log size must cover worst case** — set `_LOG_MAX` / `_SEQ_MAX` to the maximum expected call count plus margin.
8. **Approach B: guard the real function** — wrap the production function body in `#ifndef SPLE_UNIT_TESTING`; the spy in `HwInterfaces.c` provides the alternative under `#ifdef SPLE_UNIT_TESTING`.

---

## Approach B: Function Spy

### When to use

Production code writes registers via an internal helper function rather than inline pointer casts:

```c
/* Comp.c — existing production code */
static void writeProtectionReg(uint32 value)
{
    *(volatile uint32*)(COMP_PROTECTION_ADDR) = value;
}

void Comp_ExecuteUnlock(uint32 key)
{
    writeProtectionReg(key);   /* calls the internal helper */
    ...
}
```

The function is part of the same compilation unit — it cannot be hammocked. Replace its body with a spy under `SPLE_UNIT_TESTING`.

### Production source change (`<Component>.c`)

Wrap only the real function body. The function signature stays unchanged:

```c
/* <Component>.c */

static void <comp>_writeReg(uint32 value)
{
#ifndef SPLE_UNIT_TESTING
    *(volatile uint32*)(<COMP>_REG_ADDR) = value;
#else
    <comp>_test_log_write(value);   /* spy: log instead of writing hardware */
#endif
}
```

> **Keep the change minimal**: only the function body needs the guard. Signature, call sites, and all other code remain untouched.

### Header (`<Component>HwInterfaces.h`)

No macro substitution needed — the function handles everything. The header declares the test helpers exposed to the test file:

```c
#ifndef <COMPONENT>_HW_INTERFACES_H_
#define <COMPONENT>_HW_INTERFACES_H_

/* ---- register addresses and constants (always visible) ---- */
#define <COMP>_REG_ADDR           ((uint32) 0xABCD0000u)
#define <COMP>_STATUS_BUSY        ((uint32) 0x00000001u)
#define <COMP>_STATUS_READY       ((uint32) 0x00000000u)

#ifdef SPLE_UNIT_TESTING

/* Maximum number of writes to log */
#define <COMP>_TEST_WRITE_LOG_MAX  ((uint8) 16u)

/* Test variables — accessible from test file via extern */
extern uint32 <comp>_test_write_log[<COMP>_TEST_WRITE_LOG_MAX];
extern uint8  <comp>_test_write_log_index;

/* Test helper functions */
extern void   <comp>_test_reset_write_log(void);
extern void   <comp>_test_log_write(uint32 value);

#endif /* SPLE_UNIT_TESTING */

#endif /* <COMPONENT>_HW_INTERFACES_H_ */
```

### Implementation (`<Component>HwInterfaces.c`)

```c
#ifdef SPLE_UNIT_TESTING

#include "Std_Types.h"
#include "<Component>HwInterfaces.h"

uint32 <comp>_test_write_log[<COMP>_TEST_WRITE_LOG_MAX] = {0u};
uint8  <comp>_test_write_log_index                      = 0u;

void <comp>_test_reset_write_log(void)
{
    uint8 i;
    for (i = 0u; i < <COMP>_TEST_WRITE_LOG_MAX; i++)
    {
        <comp>_test_write_log[i] = 0u;
    }
    <comp>_test_write_log_index = 0u;
}

void <comp>_test_log_write(uint32 value)
{
    if (<comp>_test_write_log_index < <COMP>_TEST_WRITE_LOG_MAX)
    {
        <comp>_test_write_log[<comp>_test_write_log_index] = value;
        <comp>_test_write_log_index++;
    }
}

#endif /* SPLE_UNIT_TESTING */
```

### Test File

```cpp
#include <gtest/gtest.h>
using namespace testing;

extern "C"
{
#include "<Component>.h"
#include "<Component>HwInterfaces.h"
}

#include "mockup_components_<path>_<Component>.h"

/*!
 * @rst
 * .. test:: <Component>Test.RegisterWriteSequence
 *    :id: TS_<COMP>-001
 *    :tests: SWDD_<COMP>-100
 *
 * Verifies that the internal write helper logs register writes
 * in the correct order with the correct values.
 * @endrst
 */
TEST(<Component>Test, RegisterWriteSequence)
{
    extern uint32 <comp>_test_write_log[];
    extern uint8  <comp>_test_write_log_index;
    extern void   <comp>_test_reset_write_log(void);

    CREATE_MOCK(mockups);

    /* GIVEN: Write log is clean */
    <comp>_test_reset_write_log();

    /* WHEN: Production function that calls writeReg() internally */
    <Component>_ExecuteUnlock(EXPECTED_KEY);

    /* THEN: Correct number of writes */
    EXPECT_EQ(<comp>_test_write_log_index, EXPECTED_WRITE_COUNT)
        << "Unexpected number of register writes";

    /* THEN: Written values match expected sequence */
    EXPECT_EQ(<comp>_test_write_log[0], EXPECTED_KEY)
        << "First write mismatch";
}
```

---

## Real-World Example (Approach A)

See `components/examples/` for a complete reference implementation of Approach A:

- **Header**: `src/*HwInterfaces.h` — `SPLE_UNIT_TESTING` guard, log/seq variables, macro substitutions, BSP type stubs
- **Implementation**: `src/*HwInterfaces.c` — write log + sequential status register simulation
- **Test**: `test/test_*.cc` — verifies the register write sequence using the log array

---

## Approach C: Header Replacement

### When to use

Production code uses **named BSP register symbols** from MCAL headers like `<Peripheral>_reg.h`:

```c
/* Production code — no guards, no macros, completely clean */
while (<PERIPH>_STATUS.B.BUSY == 1u) { /* wait */ }
if (<PERIPH2>_STATE.B.LOCKED != 0u) { ... }
<PERIPH>_CTRL.U = EXPECTED_VALUE;
```

The idea: the build system for unit tests points to a **stub include directory** containing replacement headers with the same filenames. The production `.c` files include `"<Peripheral>_reg.h"` as usual — the compiler silently picks up the stub version because the stub directory comes first in the include path.

**No `#ifdef SPLE_UNIT_TESTING` anywhere in production code.**

### Limitation

This approach only captures the **final value** written to a register. For write sequences (multiple writes to the same address), use Approach A or B — they provide the log array to verify each write in order.

### File Structure

```
components/<name>/
    src/
        <Component>.c         ← unchanged — #include "<Peripheral>_reg.h" as always
    test/
        hw_stubs/
            <Peripheral>_reg.h      ← stub header (same filename as real BSP header)
            <OtherPeriph>_reg.h     ← stub header
        hw_stubs.c                  ← defines the global test variables
        test_<Component>.cc         ← test file
```

### CMakeLists.txt change

Add the stub directory **before** the real BSP include path in the test target:

```cmake
target_include_directories(<component>_unittests
    BEFORE PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/test/hw_stubs   # stub headers shadow real BSP headers
)
```

### Stub Header — Simple Variant (`<Peripheral>_reg.h`)

Use this when production code only accesses the register as a plain `uint32` (`.U` access only):

```c
/* test/hw_stubs/<Peripheral>_reg.h */
#ifndef <PERIPHERAL>_REG_H
#define <PERIPHERAL>_REG_H

#include "Std_Types.h"

/* ---- Simple uint32 variables replacing hardware registers ---- */
/* One extern variable per register used by the component under test */

typedef union { uint32 U; sint32 I; } <Vendor>_<PERIPH>_STATUS;
typedef union { uint32 U; sint32 I; } <Vendor>_<PERIPH>_CTRL;
typedef union { uint32 U; sint32 I; } <Vendor>_<PERIPH>_ERRSTAT;

extern <Vendor>_<PERIPH>_STATUS  <PERIPH>_STATUS;
extern <Vendor>_<PERIPH>_CTRL    <PERIPH>_CTRL;
extern <Vendor>_<PERIPH>_ERRSTAT <PERIPH>_ERRSTAT;

#endif /* <PERIPHERAL>_REG_H */
```

### Stub Header — Union Variant with Bitfields (`<Peripheral>_reg.h`)

Use this when production code accesses individual bits via `.B.BITNAME`. Define only the bitfields the component actually uses — keep the stub minimal:

```c
/* test/hw_stubs/<Peripheral>_reg.h */
#ifndef <PERIPHERAL>_REG_H
#define <PERIPHERAL>_REG_H

#include "Std_Types.h"

/* <PERIPH>_STATUS — only the bits the component accesses */
typedef struct
{
    uint32 BUSY     : 1;   /**< [0] Peripheral busy */
    uint32 SEC_BUSY : 1;   /**< [1] Secondary operation busy */
    uint32 reserved : 30;
} <Vendor>_<PERIPH>_STATUS_Bits;

typedef union
{
    uint32                    U;   /**< Raw uint32 access */
    sint32                    I;   /**< Signed access */
    <Vendor>_<PERIPH>_STATUS_Bits B; /**< Bitfield access */
} <Vendor>_<PERIPH>_STATUS;

/* <PERIPH>_CTRL — only the bits the component accesses */
typedef struct
{
    uint32 DISABLE_DEBUG : 1;   /**< [0] Disable debug interface */
    uint32 reserved      : 31;
} <Vendor>_<PERIPH>_CTRL_Bits;

typedef union
{
    uint32                  U;
    sint32                  I;
    <Vendor>_<PERIPH>_CTRL_Bits B;
} <Vendor>_<PERIPH>_CTRL;

/* Declare global test variables (defined in hw_stubs.c) */
extern <Vendor>_<PERIPH>_STATUS <PERIPH>_STATUS;
extern <Vendor>_<PERIPH>_CTRL   <PERIPH>_CTRL;

#endif /* <PERIPHERAL>_REG_H */
```

### Stub Header — Second Peripheral (`<OtherPeriph>_reg.h`)

```c
/* test/hw_stubs/<OtherPeriph>_reg.h */
#ifndef <OTHERPERIPH>_REG_H
#define <OTHERPERIPH>_REG_H

#include "Std_Types.h"

typedef struct
{
    uint32 LOCKED   : 1;   /**< [0] Interface locked */
    uint32 reserved : 31;
} <Vendor>_<PERIPH2>_STATE_Bits;

typedef union
{
    uint32                    U;
    sint32                    I;
    <Vendor>_<PERIPH2>_STATE_Bits B;
} <Vendor>_<PERIPH2>_STATE;

extern <Vendor>_<PERIPH2>_STATE <PERIPH2>_STATE;

#endif /* <OTHERPERIPH>_REG_H */
```

### Stub Variable Definitions (`hw_stubs.c`)

All global test variables are defined here — one file for all stub headers:

```c
/* test/hw_stubs.c — compiled into the unit test target only */
#include "Std_Types.h"
#include "<Peripheral>_reg.h"
#include "<OtherPeriph>_reg.h"

<Vendor>_<PERIPH>_STATUS  <PERIPH>_STATUS  = {0u};
<Vendor>_<PERIPH>_CTRL    <PERIPH>_CTRL    = {0u};
<Vendor>_<PERIPH2>_STATE  <PERIPH2>_STATE  = {0u};
```

### Test File

```cpp
#include <gtest/gtest.h>
using namespace testing;

extern "C"
{
#include "<Component>.h"
/* <Peripheral>_reg.h is pulled in transitively via the component header */
}
#include "mockup_components_<path>_<Component>.h"

/* Declare access to stub variables */
extern "C"
{
    extern <Vendor>_<PERIPH>_STATUS  <PERIPH>_STATUS;
    extern <Vendor>_<PERIPH>_CTRL    <PERIPH>_CTRL;
    extern <Vendor>_<PERIPH2>_STATE  <PERIPH2>_STATE;
}

/*!
 * @rst
 * .. test:: <Component>Test.ReadsStatusRegister_WhenReady
 *    :id: TS_<COMP>-001
 *    :tests: SWDD_<COMP>-100
 *
 * Verifies that the component reads the status register and
 * proceeds when the BUSY bit is clear.
 * @endrst
 */
TEST(<Component>Test, ReadsStatusRegister_WhenReady)
{
    CREATE_MOCK(mockups);

    /* GIVEN: Status register signals ready */
    /* Note: Approach C sets one value — for polling sequences use Approach A/B */
    <PERIPH>_STATUS.B.BUSY = 0u;

    /* WHEN: Component function that reads the status register */
    <Component>_WaitForReady();

    /* THEN: (assert on return value or side effects) */
    EXPECT_EQ(<comp>_result, EXPECTED_RESULT);
}

/*!
 * @rst
 * .. test:: <Component>Test.WritesControlRegister
 *    :id: TS_<COMP>-002
 *    :tests: SWDD_<COMP>-101
 *
 * Verifies that the control register is written with the expected value.
 * @endrst
 */
TEST(<Component>Test, WritesControlRegister)
{
    CREATE_MOCK(mockups);

    /* GIVEN: Control register is cleared */
    <PERIPH>_CTRL.U = 0u;

    /* WHEN: Component function that writes the control register */
    <Component>_Configure();

    /* THEN: Expected bit is set */
    EXPECT_EQ(<PERIPH>_CTRL.B.DISABLE_DEBUG, 1u)
        << "Control register bit not set as expected";
}
```
