# Parameterized Tests (TEST_P)

Use `TEST_P()` when multiple tests share the same logic but differ only in their data. This eliminates copy-paste tests and makes it obvious that you're testing the same behavior across a range of inputs.

## When to Use Parameterized Tests

Use `TEST_P()` when you find yourself writing two or more tests where:

- The test structure (Arrange/Act/Assert) is identical
- Only the input values and/or expected outputs differ
- You're covering a range: boundaries, error codes, equivalence classes, multiple valid inputs

**Concrete recognition patterns — reach for `TEST_P()` when:**

| You want to test...                                 | Example scenario                                      |
|-----------------------------------------------------|-------------------------------------------------------|
| Same function with multiple input/output pairs      | `Calculate(input)` should return `expected` for N inputs |
| Boundary values (below / at / above threshold)      | Temperature sensor: 17°C, 18°C, 19°C produce different outputs |
| All relevant error codes handled the same way       | `E_PARAM`, `E_TIMEOUT`, `E_OVERFLOW` all trigger fault state |
| Multiple valid enum/state values produce same result| Any of 3 active states disables sleep mode            |
| Equivalence classes                                 | Low/medium/high load → low/medium/high fan speed      |

**Do NOT use `TEST_P()` when:**

- Tests require different mock expectations (different call sequences)
- The Arrange-Act-Assert structure differs between cases
- Only 2 cases exist and the test body is trivial — a plain `TEST()` is simpler

---

## Full Template

```cpp
#include <gtest/gtest.h>
using ::testing::Return;
using ::testing::Values;

extern "C" {
    #include "autoconf.h"
    #include "<component>.h"
}
#include "mockup_components_<component>.h"

// -----------------------------------------------------------------------------
// 1. Parameter struct: name each field to make test failures self-documenting
// -----------------------------------------------------------------------------
struct <TestName>Param {
    const char* description;     // shown in test output on failure
    <InputType>  input;
    <OutputType> expected;
};

// Enables gtest to print the parameter in failure messages
std::ostream& operator<<(std::ostream& os, const <TestName>Param& p) {
    return os << p.description;
}

// -----------------------------------------------------------------------------
// 2. Fixture: inherit from TestWithParam<T>
//    Add shared setup/teardown here if needed (optional)
// -----------------------------------------------------------------------------
class <TestName>Test : public ::testing::TestWithParam<<TestName>Param> {};

// -----------------------------------------------------------------------------
// 3. Test body: parameterized, AAA structure
// -----------------------------------------------------------------------------
/*!
 * @rst
 * .. test:: <TestSuite>/<TestName>Test.<TestBehavior>/*
 *    :id: TS_<COMP>-###
 *    :tests: SWDD_<COMP>-###
 *
 * <Brief description of what is being tested across all parameter sets.>
 * @endrst
 */
TEST_P(<TestName>Test, <TestBehavior>) {
    CREATE_MOCK(mymock);
    auto param = GetParam();

    // ARRANGE
    EXPECT_CALL(mymock, <Setup>(param.input)).WillOnce(Return(OK));

    // ACT
    <ReturnType> result = <Component>_<Function>(param.input);

    // ASSERT
    EXPECT_EQ(result, param.expected);
}

// -----------------------------------------------------------------------------
// 4. Instantiation: provide all test cases
// -----------------------------------------------------------------------------
INSTANTIATE_TEST_SUITE_P(
    <TestSuite>,
    <TestName>Test,
    Values(
        <TestName>Param{"<description1>", <input1>, <expected1>},
        <TestName>Param{"<description2>", <input2>, <expected2>},
        <TestName>Param{"<description3>", <input3>, <expected3>}
    )
);
```

---

## Common Patterns

### Pattern 1: Boundary Value Testing

Tests that a threshold is crossed at exactly the right value.

```cpp
struct OvervoltageParam {
    const char* description;
    uint16_t    voltage_mv;
    bool        expected_fault;
};

std::ostream& operator<<(std::ostream& os, const OvervoltageParam& p) {
    return os << p.description;
}

class OvervoltageTest : public ::testing::TestWithParam<OvervoltageParam> {};

/*!
 * @rst
 * .. test:: VoltageMonitor/OvervoltageTest.DetectsFault/*
 *    :id: TS_VOLT-010
 *    :tests: SWDD_VOLT-200
 *
 * Overvoltage fault triggered at and above 14500 mV, suppressed below.
 * @endrst
 */
TEST_P(OvervoltageTest, DetectsFault) {
    CREATE_MOCK(mymock);
    auto param = GetParam();

    // ARRANGE
    EXPECT_CALL(mymock, HAL_ADC_ReadVoltage()).WillOnce(Return(param.voltage_mv));

    // ACT
    VoltageMonitor_Process();

    // ASSERT
    EXPECT_EQ(VoltageMonitor_IsFaultActive(), param.expected_fault);
}

INSTANTIATE_TEST_SUITE_P(VoltageMonitor, OvervoltageTest, Values(
    OvervoltageParam{"BelowThreshold",  14499u, false},
    OvervoltageParam{"AtThreshold",     14500u, true },
    OvervoltageParam{"AboveThreshold",  14501u, true }
));
```

### Pattern 2: Error Code Handling

Tests that multiple error codes all trigger the same defensive behavior.

```cpp
struct CommErrorParam {
    const char* description;
    status_t    error_code;
};

std::ostream& operator<<(std::ostream& os, const CommErrorParam& p) {
    return os << p.description;
}

class CommErrorTest : public ::testing::TestWithParam<CommErrorParam> {};

/*!
 * @rst
 * .. test:: Communication/CommErrorTest.EntersFaultState/*
 *    :id: TS_COMM-020
 *    :tests: SWDD_COMM-300
 *
 * Any bus error causes the component to enter fault state.
 * @endrst
 */
TEST_P(CommErrorTest, EntersFaultState) {
    CREATE_MOCK(mymock);
    auto param = GetParam();

    // ARRANGE
    EXPECT_CALL(mymock, Bus_Receive(_)).WillOnce(Return(param.error_code));

    // ACT
    Communication_Process();

    // ASSERT
    EXPECT_EQ(Communication_GetState(), STATE_FAULT);
}

INSTANTIATE_TEST_SUITE_P(Communication, CommErrorTest, Values(
    CommErrorParam{"ParamError",   E_PARAM  },
    CommErrorParam{"TimeoutError", E_TIMEOUT},
    CommErrorParam{"BusError",     E_BUS    },
    CommErrorParam{"OverflowError",E_OVERFLOW}
));
```

### Pattern 3: Input/Output Mapping (Lookup / Calculation)

Tests that a function maps inputs to expected outputs correctly.

```cpp
struct FanSpeedParam {
    const char* description;
    uint8_t     temperature_c;
    uint8_t     expected_duty_percent;
};

std::ostream& operator<<(std::ostream& os, const FanSpeedParam& p) {
    return os << p.description;
}

class FanControlTest : public ::testing::TestWithParam<FanSpeedParam> {};

/*!
 * @rst
 * .. test:: FanControl/FanControlTest.SetsCorrectSpeed/*
 *    :id: TS_FAN-005
 *    :tests: SWDD_FAN-100
 *
 * Fan duty cycle calculated correctly from temperature across operating range.
 * @endrst
 */
TEST_P(FanControlTest, SetsCorrectSpeed) {
    CREATE_MOCK(mymock);
    auto param = GetParam();

    // ARRANGE
    EXPECT_CALL(mymock, ReadTemperature()).WillOnce(Return(param.temperature_c));
    EXPECT_CALL(mymock, SetFanDuty(param.expected_duty_percent)).Times(1);

    // ACT
    FanControl_Process();
}

INSTANTIATE_TEST_SUITE_P(FanControl, FanControlTest, Values(
    FanSpeedParam{"Cold",    20u,  0u  },
    FanSpeedParam{"Warm",    60u,  25u },
    FanSpeedParam{"Hot",     80u,  60u },
    FanSpeedParam{"Critical",95u,  100u}
));
```

### Pattern 4: Fixture with shared setUp (TestFixture)

When all parameter variants need the same initialization beyond a simple mock:

```cpp
class DiagnosticParamTest : public ::testing::TestWithParam<DiagnosticParam> {
protected:
    void SetUp() override {
        CREATE_MOCK(mymock);
        Diagnostic_Init();
    }
};
```

### Pattern 5: Feature-Guarded Cases Inside `Values(...)`

When a feature flag adds extra branches to the function under test, keep the extra cases in the
**same** `INSTANTIATE_TEST_SUITE_P` but wrap them in `#if`. Put the `,` separator **before** the
`#if` block so the always-present case stays comma-free and the `Values(...)` list is valid whether
the flag is 0 or 1:

```cpp
INSTANTIATE_TEST_SUITE_P(Suite, Fixture, Values(
    Param{"always present case", ...}    // no trailing comma

#ifdef CONFIG_AUTO_OFF
    ,
    Param{"feature-specific case", ...}
#endif
));
```

> **Cross-variant compile rule**: Every `INSTANTIATE_TEST_SUITE_P` and every conditionally compiled
> `TEST_P`/`TEST_F` must compile and behave correctly on **all** supported variants — not only the
> currently active one. Before committing, mentally compile with the flag both set and cleared:
> "Does this still compile and pass when `CONFIG_AUTO_OFF` is not defined?"

### Separate Fixtures for Orthogonal Code Paths

When a function has two logically distinct paths that need different setup (e.g. the main data path
vs. a cleanup/reset path), use **two separate fixtures and two `INSTANTIATE_TEST_SUITE_P` blocks**
rather than one large suite with `if (param.special_case)` branches inside the test body. Each test
body stays flat, and the parameter sets document the two behaviors independently. A branch on the
parameter inside the body is a signal the cases do not actually share one structure — split them.

---

## Traceability Notes

- The RST test name **must** include the wildcard suffix `/*` to match all generated instances:
  ```
  .. test:: <TestSuite>/<FixtureName>.<TestName>/*
  ```
- Use a **single `:id:`** for the whole `TEST_P()`. GTest generates instance names like
  `VoltageMonitor/OvervoltageTest.DetectsFault/0` automatically.
- If individual cases need separate requirement links, split into plain `TEST()` instead.

**See**: [test-patterns.md](test-patterns.md) for non-parameterized patterns
