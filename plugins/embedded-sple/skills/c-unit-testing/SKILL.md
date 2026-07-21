---
name: c-unit-testing
description: Write GTest/GMock unit tests for embedded C components using Arrange-Act-Assert and hammocking. Use when writing tests for a function or component, setting up mocks for dependencies, fixing failing tests, debugging mock expectation errors, adding test traceability to requirements, writing characterization tests for legacy code, improving test coverage, creating parameterized tests, or testing hardware register access. Covers test file structure, CREATE_MOCK pattern, RST traceability blocks, variant-aware testing, and refactoring safety nets.
---

# GTest Unit Testing for Embedded C

Write behavior-driven unit tests that enable safe refactoring and capture component dynamics using the Arrange-Act-Assert pattern with GTest/GMock and hammocking.

> **COMPANION SKILL**: For testing multiple components working together (subsystem integration, data flow, variant interactions), use the `c-integration-testing` skill.

## First Contact

When the user invokes this skill, gather the context needed to help effectively:

1. **Which component?** — Ask for the component path (e.g., `components/brightness_controller`)
2. **What's the goal?** — New tests from scratch, add tests for a specific function, fix a failing test, or refactoring safety net?
3. **Existing tests?** — Check if `test/` directory exists in the component. If yes, read existing test files to understand patterns already in use.
4. **Dependencies** — Run `analyze_dependencies.py` on the source file to identify what needs mocking.

> If the user already provided this context (e.g., "write tests for ComponentX_Init"), skip the questions and proceed directly.

## Core Philosophy

Unit tests should:

1. **Enable Safe Refactoring**: Capture existing behavior to allow confident restructuring
2. **Document Behavior**: Arrange-Act-Assert structure documents component interactions
3. **Specify Behavior**: Describe what the component does, not how
4. **Prevent Regressions**: Lock in behavior to prevent accidental changes

## Choosing the Test Level

Before writing a single line, decide whether you are actually writing a unit test:

| Scenario | Test level | Skill to use |
|---|---|---|
| Exactly ONE component in isolation, all dependencies mocked | **Unit test** | This skill |
| TWO or more real component implementations compiled and exercised together | **Integration test** | `c-integration-testing` skill |
| Mixed (isolated logic + inter-component paths) | **Both** | Unit tests here + integration tests there |

> **RULE**: If a test requires two real production modules compiled together and exercised against
> each other, it is an integration test — even when it uses GTest and GMock. Writing it here would
> produce a false sense of unit isolation. Use the `c-integration-testing` skill instead.

## Specification-First Test Design

> Test cases are derived from the **specification**, not only from the code paths.

**Before writing tests** — read the relevant design/requirement documents for the function under
test (component `doc/index.md`, software/unit specification, requirement-management IDs). Derive
test cases from required behavior, not just from what the code happens to do.

**When the code contradicts the specification** — do not silently make the test follow the code.
Stop and ask the user which behavior the test should pin down:

```text
DECISION REQUIRED - Spec/Implementation Conflict
Spec  <SPEC_ID>: "<verbatim requirement text>"
Code  : <what the current implementation does>

  A) Test verifies CURRENT IMPLEMENTATION -> test passes, potential defect remains hidden
  B) Test verifies SPECIFICATION          -> test FAILS, documents a potential defect
```

If the user chooses B, write the test to express the spec-correct behavior and mark it clearly as
intentionally failing (with a comment referencing the spec ID and the divergence).

**After writing tests** — add the new test IDs back into the traceability source (component
`doc/index.md` / spec test chapter) so the requirement-to-test mapping stays complete.

## Quick Start

### Build and Run Tests

**Variant names** must match the choices configured in `.vscode/cmake-variants.json`.
Some variants use a `Platform/SubVariant` format (e.g. `PlatformA/VariantX`) reflecting the nested folder
structure under `variants/`. The top-level platform folder alone (e.g. `PlatformA`) is **not** a valid variant —
always use the full path to the actual variant folder.

> **BUILD**: Invoke the `build-execution` skill to build and run unit tests.
> Provide: buildKit=test, buildType=Debug, variants=\<Variant\>, target=components\_\<name\>\_unittests

View reports via VS Code tasks: "Open component test report", "Open component coverage report".

### Test File Structure

Organize tests into multiple focused `test_*.cc` files — one file per function or logical group of related behaviors. Nobody benefits from a test file with thousands of lines.

**Rules:**

- **One file per function** for complex functions (many branches, states, error paths): `test_ComponentName_FunctionName.cc`
- **One file per feature area** for simpler functions that naturally belong together: `test_ComponentName_FeatureArea.cc`
- **Size limit**: When a test file grows beyond ~200–300 lines, treat it as a signal to split — even if all tests cover the same function
- **When modifying**: Check the file size after your changes. If it has grown too large, split it before committing

**Example layout for a component with several functions:**

```
components/<subsystem>/<component>/test/
    test_<Component>_Init.cc          # initialization and reset behavior
    test_<Component>_ProcessInput.cc  # main processing logic
    test_<Component>_ErrorHandling.cc # fault injection and error paths
    test_<Component>_StateTransitions.cc  # state machine transitions
```

> Each file gets its own `#include` block and mock setup. Tests in different files are fully independent — a crash or failure in one file does not affect the others.

### Test Template

```cpp
#include <gtest/gtest.h>
extern "C" { 
    #include "autoconf.h"
    #include "<component>.h"
}
#include "mockup_components_<component>.h"

/*!
 * @rst
 * .. test:: <Component>.DescriptiveTestName
 *    :id: TS_<COMP>-001
 *    :tests: SWDD_<COMP>-100
 * 
 * Brief: What behavior this test verifies.
 * @endrst
 */
TEST(TempMonitor, RaisesAlarm_When_ThresholdExceeded) {
    CREATE_MOCK(mymock);

    // ARRANGE
    EXPECT_CALL(mymock, ReadTemperature()).WillOnce(Return(85));
    EXPECT_CALL(mymock, TriggerAlarm()).Times(1);  // verified by GMock at teardown

    // ACT
    AlarmState_t result = TempMonitor_Check();

    // ASSERT
    EXPECT_EQ(result, ALARM_ACTIVE);
}
```

## Arrange-Act-Assert Pattern

Every test follows this structure:

- **ARRANGE**: Set up initial state and all mock expectations — inputs *and* expected outputs alike
- **ACT**: Call the function under test — one call per test
- **ASSERT**: Explicit assertions with `EXPECT_EQ` / `ASSERT_*` on return values or observable state

> **Key rule for GMock**: `EXPECT_CALL` registers expectations for *future* calls.
> All `EXPECT_CALL` statements — regardless of whether they supply inputs or verify outputs — must
> be placed **before** the ACT. GMock verifies call counts and arguments automatically at test teardown.
>
> ASSERT is optional when GMock verifies all outputs via `EXPECT_CALL`. If the function returns a
> value or modifies observable state, add an explicit `EXPECT_EQ` / `ASSERT_*` in the ASSERT block.

### Common Test Patterns

```cpp
// Pattern 1: Simple state transition
TEST(LED, TurnsOn_When_ButtonPressed) {
    CREATE_MOCK(mymock);

    // ARRANGE
    EXPECT_CALL(mymock, HAL_GPIO_Read(BUTTON_PIN)).WillOnce(Return(HIGH));
    EXPECT_CALL(mymock, HAL_GPIO_Write(LED_PIN, HIGH)).Times(1);

    // ACT
    LED_ProcessButtonInput();
}

// Pattern 2: Temporal behavior (debouncing, timing)
TEST(Button, GeneratesPressEvent_After50msStable) {
    CREATE_MOCK(mymock);

    // ARRANGE
    EXPECT_CALL(mymock, ReadButtonState()).Times(50).WillRepeatedly(Return(PRESSED));
    EXPECT_CALL(mymock, SendPressEvent()).Times(1);

    // ACT: Advance time 50ms
    for (int tick = 0; tick < 50; tick++) {
        Button_Tick1ms();
    }
}

```

**See**: [references/test-patterns.md](references/test-patterns.md) for advanced patterns

## Hammocking (Mocking Dependencies)

**Hammocking** isolates the component under test by mocking all external dependencies.

### Auto-Generated Mocks

The build system auto-generates mocks from component dependencies:

```cmake
# In components/<name>/CMakeLists.txt
spl_add_required_interface(components/hal_gpio)
spl_add_required_interface(components/rte)
```

Generated files:

- `mockup_components_<component>.h`
- `mockup_components_<component>.cc`

### Mock Usage Pattern

Always use `CREATE_MOCK(mymock);` inside each test:

```cpp
TEST(Component, TestName) {
    CREATE_MOCK(mymock);  // Project-specific macro
    
    // Set expectations
    EXPECT_CALL(mymock, Function(arg)).Times(1).WillOnce(Return(value));
    
    // Execute test
    Component_Function();
}
```

### Mock Expectations

```cpp
// Single call with specific argument
EXPECT_CALL(mymock, SetValue(42)).Times(1);

// Multiple calls with return value
EXPECT_CALL(mymock, ReadSensor()).Times(3).WillRepeatedly(Return(100));

// Wildcard argument matching
EXPECT_CALL(mymock, WriteData(_)).WillOnce(Return(OK));

```

**See**: [references/hammocking-guide.md](references/hammocking-guide.md) for custom matchers and detailed mock strategies

## Parameterized Tests (DRY Principle)

### When to Use TEST_P()

Use `TEST_P()` when **two or more tests share identical Arrange-Act-Assert structure and differ only in data**:

- Multiple input/output pairs for the same function (boundary values, equivalence classes)
- Several error codes that all trigger the same fault behavior
- A range of valid enum/state values producing the same outcome
- Threshold testing: below / at / above a limit value

### When NOT to Use TEST_P()

**Do not force `TEST_P()` when the structure differs between cases.** Use plain `TEST()` when:

- Mock expectations differ between cases (different call counts, different functions called)
- The Arrange-Act-Assert flow varies (e.g., state machine tests where each state requires different setup)
- A `if (param.special_case)` branch would be needed inside the test body — that's a sign the cases don't actually share the same structure

> Forcing dissimilar tests into `TEST_P()` makes the test body harder to read than two plain `TEST()` calls would be. DRY is a good goal; contorting test logic to achieve it is not.

**See**: [references/parameterized-tests.md](references/parameterized-tests.md) for full templates, boundary testing, error code patterns, and traceability rules

## RTE Platform Aliasing

When a component runs on multiple platforms (ECU generations, project lines) that use different
RTE symbol naming conventions, define **test-local alias macros** once at the top of the test
file. The test body stays platform-agnostic.

```cpp
// After all #includes — one block, never scattered through the test body
// Platform switch comes from KConfig via autoconf.h (CONFIG_* define)
#ifdef CONFIG_PLATFORM_A
    #define COMP_TEST_RTE_Signal   (Rte_CompA_PComp_Signal)
    #define COMP_TEST_RTE_IrvValue (Rte_Irv_CompA_IrvValue)
    #undef  Rte_Call_CComp_Service
    #define Rte_Call_CComp_Service(a, b) PlatformA_Service(a, b)
#else
    #define COMP_TEST_RTE_Signal   (Rte_COMP_A_PComp_Signal)
    #define COMP_TEST_RTE_IrvValue (Rte_Irv_COMP_A_IrvValue)
    #undef  Rte_Call_CComp_Service
    #define Rte_Call_CComp_Service(a, b) PlatformB_Service(a, b)
#endif
```

**Rules:**
- Prefix with `<COMPONENT>_TEST_` — unambiguously test-only
- Always `#undef` before redefining a function-like macro
- Add `#error "Unknown platform"` as fallback when using `#elif` chains
- Only alias symbols actually used in test setup/assertions

**See**: [references/rte-platform-aliasing.md](references/rte-platform-aliasing.md) for full templates, the 3-platform `#elif` pattern, and a complete worked example

## HW Register Testing

When production code writes directly to memory-mapped registers (`*(volatile uint32*)ADDR = val`) or reads hardware status registers, you cannot mock these accesses through hammocking. Instead, use the **`SPLE_UNIT_TESTING` substitution pattern**.

### How it works

Three approaches exist — choose based on how production code accesses the register:

| Production code does | Approach |
|---|---|
| Named BSP symbol: `<PERIPH>_STATUS.B.BUSY` | **C – Header Replacement**: swap the whole BSP header — cleanest, zero guards in prod code |
| `*(volatile uint32*)ADDR = val` or component-owned macro | **A – Macro Substitution**: redefine the macro in the component's interface header |
| Internal helper function calls the register write | **B – Function Spy**: guard the real function body, provide spy implementation |
| External HAL/dependency function | **Standard hammocking** — no `SPLE_UNIT_TESTING` guard needed |

> **Write sequences** (multiple writes to the same register in order): Approach C only captures the final value. Use **A or B** when the test must verify each write in sequence.

**Approach A** — the hardware interface header splits into two worlds using `#ifndef SPLE_UNIT_TESTING`:

```c
/* <Component>HwInterfaces.h */

#define <COMP>_CMD_ADDR  ((uint32) 0xABCD0000u)   /* always visible */

#ifndef SPLE_UNIT_TESTING
    #include "IfxPeripheral_reg.h"                 /* real BSP header */
    #define <COMP>_WRITE_CMD(val)  (*(volatile uint32*)(<COMP>_CMD_ADDR) = (val))
    #define <COMP>_READ_STATUS()   (PERIPHERAL_STATUS.U)
#else
    /* Test variables */
    extern uint32 <comp>_test_cmd_log[];
    extern uint32 <comp>_test_status_seq[];
    extern void   <comp>_test_reset_cmd_log(void);
    extern uint32 <comp>_test_read_status(void);

    /* Redirect register access to test helpers */
    #define <COMP>_WRITE_CMD(val)  (<comp>_test_log_cmd_write(val))
    #define <COMP>_READ_STATUS()   (<comp>_test_read_status())

    /* BSP type stubs — only what the component actually uses */
    typedef union { uint32 U; sint32 I; } PERIPHERAL_STATUS_t;
#endif
```

The companion `<Component>HwInterfaces.c` is **fully wrapped** in `#ifdef SPLE_UNIT_TESTING` and implements the write log and sequential read simulation.

**See**: [references/hw-register-testing.md](references/hw-register-testing.md) for test patterns (write-log, status polling), Approach C (BSP header replacement), type stub patterns, and a worked example (`components/examples/`)

## Test Traceability

Every test must link to requirements using RST documentation blocks (format shown in the Test Template above).

### Rules

- **Test name**: Must match actual `TEST()`, `TEST_F()`, or `TEST_P()` name
- **Test ID**: `TS_<COMP>-###` (sequential, zero-padded to 3 digits)
- **Requirements**: Comma-separated list of SWDD IDs (find in `components/<name>/doc/index.md`)
- **Only use IDs that exist**: Never invent requirement or test IDs — an invented ID silently breaks traceability tooling. Grep the spec files/`doc/index.md` for the exact ID before writing it.
- **Quote requirements verbatim**: When copying requirement text into a traceability comment, copy it exactly from the source — never paraphrase (a paraphrase drifts from the requirement and misleads reviewers).
- **Parameterized tests**: Use wildcard `.. test:: SuiteName/FixtureName.TestName/*` **only when all parameter instances test the same requirement(s)**. If different cases trace to different requirements, use plain `TEST()` with individual RST blocks instead.

**See**: [references/traceability.md](references/traceability.md) for complete traceability guide

## Best Practices

### Test Design

- **Test behavior, not implementation**: Focus on what, not how
- **One behavior per test**: Each test validates one scenario
- **Use descriptive names**: `TurnsOn_When_ButtonPressed` explains the scenario
- **Cover edge cases**: Boundaries, errors, state transitions, timing
- **Always use Arrange-Act-Assert**: Makes tests self-documenting

### Refactoring Support

- **Write tests before refactoring**: Capture existing behavior first
- **Test at API boundaries**: Don't test internal functions
- **Lock down behavior**: Tests prevent accidental changes
- **Update tests intentionally**: Only when behavior should change

### Code Quality

- **Prefer parameterized tests**: Use `TEST_P()` over duplicated tests
- **Use custom matchers**: Cleaner than field-by-field checks
- **Keep tests simple**: Tests should be easier to understand than production code
- **Fast execution**: Simulate time with ticks, don't use real delays

### No Magic Numbers — In Code and In Comments

Never write a raw numeric literal that stands for a domain value — not in code, and not in
comments, RST blocks, or ARRANGE/ACT/ASSERT annotations. This includes embedding the *current*
value of a `#define`/`enum` as a parenthetical such as `(= 193)` or `(90..238)`: when the constant
changes, the annotation goes silently wrong and misleads the next reader.

```cpp
// BAD — raw literal in code and in the comment; meaning unclear, breaks silently if the enum changes
RteSetPowerState(1);                 // what does 1 mean?
/* toggles because the previous state was 0 */

// GOOD — symbolic constant everywhere, including prose
RteSetPowerState(POWER_STATE_ON);
/* toggles because the previous state was POWER_STATE_OFF */
```

**Accepted exceptions** (state the reason in a comment): a constant defined only in a
hardware/generated header that cannot be included in the test translation unit, or a typical
analog signal value for which the code defines only threshold constants. The exception covers the
code literal only — the symbolic name must still appear in the surrounding prose. Application-level
headers are always reachable in a test build; include them rather than hard-coding their values.

### Keep Comments Robust Against Config Changes

- **No hard-coded feature-switch values or variant names in comments.** Feature-switch values
  (`= 0` / `= 1`) and variant/project names change over time; naming them in comments creates
  documentation that is wrong the moment the configuration changes. List feature switches by name
  and effect only, and label `#else` branches by their *convention* (e.g. "default RTE prefix"),
  not by a specific variant.
- **Verify enum/constant values against the real source header**, not against spec or doc files —
  specs can lag behind the code by one or more refactoring cycles. Grep the defining header before
  using a value; if the doc disagrees, fix the doc first (separate change), then test against the
  source of truth.

### File Encoding — Pure ASCII in Test Files

Keep test files pure ASCII. Special Unicode characters (em/en dash `–`, right arrow `→`,
ellipsis `…`, multiplication `×`, smart quotes) turn into mojibake when files round-trip through
tools with mismatched encodings.

- Use `-` not `–`, `->` not `→`, `...` not `…`, `x` not `×`, and straight quotes `"` `'`.
- Quick check: `python -c "print(sum(1 for c in open('FILE',encoding='utf-8-sig').read() if ord(c)>127))"` should print `0`.

## Reference Documents

- **[test-patterns.md](references/test-patterns.md)**: Advanced test patterns and examples
- **[parameterized-tests.md](references/parameterized-tests.md)**: Full templates for `TEST_P()` — boundary, error codes, I/O mapping
- **[hammocking-guide.md](references/hammocking-guide.md)**: Deep dive on mock setup strategies
- **[traceability.md](references/traceability.md)**: Complete traceability guide
- **[workflow-debugging.md](references/workflow-debugging.md)**: Development workflow and debugging
- **[rte-platform-aliasing.md](references/rte-platform-aliasing.md)**: Test-local alias macros for multi-platform RTE symbol naming
- **[variant-testing.md](references/variant-testing.md)**: Variant-based testing strategies
- **[characterization-testing.md](references/characterization-testing.md)**: Golden master tests for legacy code
- **[hw-register-testing.md](references/hw-register-testing.md)**: Testing memory-mapped hardware registers — write-log, status polling simulation, BSP type stubs

## Committing Tests

> **COMMIT REQUIREMENT**: When committing new tests, invoke the `conventional-commits` skill
> to ensure proper commit message formatting (use `test:` type for test-only changes).

> **PROJECT MEMORY**: When discovering important test patterns or solving tricky testing challenges,
> use the `project-memory` skill to document them:
> - **Testing bugs or workarounds** → `doc/project_notes/bugs.md`
> - **Test architecture decisions** → `doc/project_notes/decisions.md`

## Coverage Analysis

After building and running tests, always check coverage to identify untested code paths. This is especially important when:

- Writing tests for an untested function (verify you actually covered the branches you intended)
- Completing a batch of tests (check overall component coverage before committing)
- Debugging a test failure (coverage can reveal which paths were/weren't executed)

**READ**: [Coverage Analysis](../shared/test-reports/coverage-analysis.md) — Report locations, coverage.json extraction, junit.xml parsing, output format template, and variant mapping.

## Scripts

- **[analyze_dependencies.py](scripts/analyze_dependencies.py)**: Analyze C file dependencies for testing

```powershell
# Analyze legacy code dependencies
python plugins/embedded-sple/skills/c-unit-testing/scripts/analyze_dependencies.py components/examples/adc/src/adc.c
```
