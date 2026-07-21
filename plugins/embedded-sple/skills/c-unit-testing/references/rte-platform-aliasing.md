# RTE Platform Aliasing in Tests

## Problem

Embedded C components access the RTE (Runtime Environment) through generated symbols. When a
component is deployed on multiple platforms (e.g., different ECU generations or project lines),
the RTE generator produces symbols with **different naming conventions** for the same logical
signal — even though the underlying mock buffer holds the same value.

**Example — same signal, two naming conventions:**

| Platform A                  | Platform B                  |
|-----------------------------|-----------------------------|
| `Rte_CompA_PComp_Signal`    | `Rte_COMP_A_PComp_Signal`   |
| `Rte_Irv_CompA_IrvValue`    | `Rte_Irv_COMP_A_IrvValue`   |
| `PlatformA_Service_Op(...)` | `PlatformB_Service_Op(...)` |

Tests that directly read RTE symbol values for setup or assertion would need to know which
platform is active. Without abstraction, either:

- The test file is duplicated per platform, or
- `#if` guards are scattered throughout the test body (unreadable)

## Solution: Test-Local Alias Macros

Define **neutral test-local aliases** once at the top of the test file, inside a single
`#if`/`#else` block keyed on the active platform. The test body uses only the aliases.

---

## Platform Guard: KConfig Variant (preferred)

In the SPLE build system, the active variant is configured via KConfig. The resulting
`autoconf.h` (included in every test via `extern "C" { #include "autoconf.h" }`) provides
`CONFIG_*` defines. Use these as the platform guard:

```cpp
// ============================================================
// Platform-specific RTE symbol aliases
// Place directly after the #include block, before test code.
// autoconf.h is already included via extern "C" above.
// ============================================================
#ifdef CONFIG_PLATFORM_A  /* Platform A RTE naming, set in variants/<VariantA>/config */
    #define COMP_TEST_RTE_OutputSignal       (Rte_CompA_PComp_OutputSignal)
    #define COMP_TEST_RTE_IrvValue           (Rte_Irv_CompA_IrvValue)
    #define COMP_TEST_RTE_StatusFlag         (Rte_CompA_PComp_StatusFlag)
    #undef  Rte_Call_CComp_Service_Operation
    #define Rte_Call_CComp_Service_Operation(arg1, arg2) \
        PlatformA_CompService_Operation(arg1, arg2)
#else  /* Platform B RTE naming */
    #define COMP_TEST_RTE_OutputSignal       (Rte_COMP_A_PComp_OutputSignal)
    #define COMP_TEST_RTE_IrvValue           (Rte_Irv_COMP_A_IrvValue)
    #define COMP_TEST_RTE_StatusFlag         (Rte_COMP_A_PComp_StatusFlag)
    #undef  Rte_Call_CComp_Service_Operation
    #define Rte_Call_CComp_Service_Operation(arg1, arg2) \
        PlatformB_CompService_Operation(arg1, arg2)
#endif /* CONFIG_PLATFORM_A */
```

The `CONFIG_PLATFORM_A` name comes from a KConfig entry in the variant configuration, e.g.:

```
# variants/PlatformA/config
CONFIG_PLATFORM_A=y
```

For three or more platforms, use `#elif`:

```cpp
#ifdef  CONFIG_PLATFORM_A
    #define COMP_TEST_RTE_Signal (Rte_CompA_PComp_Signal)
#elif defined CONFIG_PLATFORM_B
    #define COMP_TEST_RTE_Signal (Rte_CompB_PComp_Signal)
#elif defined CONFIG_PLATFORM_C
    #define COMP_TEST_RTE_Signal (Rte_CompC_PComp_Signal)
#else
    #error "Unknown platform — add alias mapping for this platform"
#endif
```

The `#error` fallback turns a missing mapping into a clear compile error instead of a
silent wrong-symbol access.

---

## Platform Guard: Legacy Project Switch (existing code only)

Older components use a handcrafted project switch instead of KConfig, e.g.
`#if (1 == PRJ_PLATFORM_XYZ)`. This is **legacy** — do not use this style for new tests.
Existing code using this pattern does not need to be migrated until the component itself
is migrated to the SPLE variant system.

```cpp
/* Legacy style — only in existing code, not for new tests */
#if ( 1 == MY_PRJ_PLATFORM_A )
    #define COMP_TEST_RTE_Signal (Rte_CompA_PComp_Signal)
#else
    #define COMP_TEST_RTE_Signal (Rte_COMP_A_PComp_Signal)
#endif
```

---

## Test Body (same regardless of platform guard style)

```cpp
TEST(MyComponent, OutputsCorrectSignal_WhenProcessed) {
    CREATE_MOCK(mymock);

    // ARRANGE
    COMP_TEST_RTE_IrvValue = INITIAL_VALUE;

    // ACT
    MyComponent_Process();

    // ASSERT: alias hides which platform is active
    EXPECT_EQ(COMP_TEST_RTE_OutputSignal, EXPECTED_OUTPUT);
    EXPECT_EQ(COMP_TEST_RTE_StatusFlag,   STATUS_ACTIVE);
}
```

---

## Rules

### Naming

- **Always prefix** aliases with `<COMPONENT>_TEST_` — makes it obvious this is test-only code
  and prevents accidental collisions with production symbol names.
- Use the **logical signal name** (not the platform name) in the alias:
  - ✅ `COMP_TEST_RTE_OutputSignal`
  - ❌ `COMP_TEST_RTE_Disco_OutputSignal`

### Placement

- The entire alias block goes **directly after all `#include` statements**, before any test
  code. One block per file — don't scatter aliases across the file.

### Function-like macros

- Always use `#undef` before redefining a function-like macro. Without it, compilers warn
  about redefining an existing macro.

### What to alias

Only alias symbols that appear in **test setup or assertions**. Do not alias every RTE symbol
in the generated mockup — only what you actually use.

---

## Full Example (KConfig variant guard)

Component `SeatHeater` deployed on variants `PlatformGen3` and `PlatformGen4`:

```
# variants/PlatformGen3/config
CONFIG_RTE_GEN3=y

# variants/PlatformGen4/config  
CONFIG_RTE_GEN4=y
```

```cpp
#include <gtest/gtest.h>
using namespace testing;

extern "C" {
    #include "autoconf.h"
    #include "SeatHeater.h"
}
#include "mockup_components_body_SeatHeater.h"

// ============================================================
// Platform RTE aliases — driven by KConfig variant config
// ============================================================
#ifdef CONFIG_RTE_GEN3
    #define SH_TEST_RTE_HeaterLevel     (Rte_SeatHtr_PSeatHtr_HeaterLevel)
    #define SH_TEST_RTE_SeatTemperature (Rte_Irv_SeatHtr_SeatTemperature)
    #undef  Rte_Call_CSeatHtr_DiagnosticSrv_ReportError
    #define Rte_Call_CSeatHtr_DiagnosticSrv_ReportError(id, val) \
        Gen3_DiagReport_SeatHeaterError(id, val)
#else  /* CONFIG_RTE_GEN4 */
    #define SH_TEST_RTE_HeaterLevel     (Rte_SEAT_HTR_PSeatHtr_HeaterLevel)
    #define SH_TEST_RTE_SeatTemperature (Rte_Irv_SEAT_HTR_SeatTemperature)
    #undef  Rte_Call_CSeatHtr_DiagnosticSrv_ReportError
    #define Rte_Call_CSeatHtr_DiagnosticSrv_ReportError(id, val) \
        Gen4_DiagReport_SeatHtrError(id, val)
#endif /* CONFIG_RTE_GEN3 */

// ============================================================
// Tests — platform-agnostic from here on
// ============================================================

/*!
 * @rst
 * .. test:: SeatHeater.ActivatesLevel2_WhenTemperatureBelowTarget
 *    :id: TS_SH-001
 *    :tests: SWDD_SH-100
 *
 * Heater activates at level 2 when seat temperature is below target.
 * @endrst
 */
TEST(SeatHeater, ActivatesLevel2_WhenTemperatureBelowTarget) {
    CREATE_MOCK(mymock);

    // ARRANGE
    SH_TEST_RTE_SeatTemperature = 15u;  /* °C, below 20°C target */

    // ACT
    SeatHeater_Process();

    // ASSERT
    EXPECT_EQ(SH_TEST_RTE_HeaterLevel, HEAT_LEVEL_2);
}
```

---

## When to Apply This Pattern

Apply RTE platform aliasing when **all** of the following are true:

1. The component under test uses RTE-generated symbols directly (read/write macros, `Rte_Irv*`, ports)
2. The component is compiled for **two or more platforms** that use different RTE naming conventions
3. Test setup or assertions **directly access RTE symbol values** (not just via mock expectations)

If tests only use `EXPECT_CALL()` and never read RTE symbol values directly, no aliasing is needed.

**See**: [variant-testing.md](variant-testing.md) for KConfig-based feature variants
