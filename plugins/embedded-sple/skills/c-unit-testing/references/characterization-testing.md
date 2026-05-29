# Characterization Testing for Legacy Code

Characterization tests (Golden Master tests) capture the **current behavior** of legacy code before refactoring. They act as a safety net to detect unintended changes.

## When to Use

- Testing untested legacy code
- Before refactoring complex functions
- Documenting poorly understood code
- Preserving behavior during modernization

## Key Difference from Specification Tests

| Aspect        | Specification Tests     | Characterization Tests   |
|---------------|-------------------------|--------------------------|
| Purpose       | Verify correct behavior | Capture current behavior |
| Assertions    | Based on requirements   | Based on actual output   |
| Failures mean | Code is wrong           | Behavior changed         |
| Documentation | Requirements            | Current implementation   |

## Workflow

### Step 1: Analyze Dependencies

Use the analysis script to identify what needs mocking:

```powershell
python scripts/analyze_dependencies.py components/examples/adc/src/adc.c
```

Output shows:

- External functions (need mocking)
- Global variables (need reset in SetUp)
- Static functions (test through public API)
- Hardware accesses (need fake implementations)

### Step 2: Create Test with Unknown Assertions

```cpp
TEST(LegacyComponent, CapturesCurrentBehavior) {
    CREATE_MOCK(mymock);

    // ARRANGE
    int input = 42;

    // ACT
    int result = legacy_function(input);

    // ASSERT: What does it actually return?
    EXPECT_EQ(0, result);  // Intentionally wrong - run to discover actual value
}
```

### Step 3: Run Test and Capture Actual Output

```text
Expected: 0
  Actual: 73
```

Now you know: `legacy_function(42)` returns `73`.

### Step 4: Update Test with Captured Behavior

```cpp
/*!
 * @rst
 * .. test:: LegacyComponent.CapturesCurrentBehavior_Input42
 *    :id: TS_LEG-001
 *    :tests: SWDD_LEG-100
 * 
 * Captures current behavior for input 42.
 * TODO: Verify if 73 is correct per specification.
 * @endrst
 */
TEST(LegacyComponent, CapturesCurrentBehavior_Input42) {
    CREATE_MOCK(mymock);

    // ARRANGE
    int input = 42;

    // ACT
    int result = legacy_function(input);

    // ASSERT: Current behavior (golden master)
    EXPECT_EQ(73, result);
}
```

### Step 5: Document Suspicious Behavior

```cpp
/*!
 * @rst
 * .. test:: LegacyComponent.SuspiciousBehavior_NegativeInput
 *    :id: TS_LEG-002
 *    :tests: SWDD_LEG-100
 * 
 * SUSPICIOUS: Negative input not validated.
 * TODO: Should this return error or be rejected?
 * @endrst
 */
TEST(LegacyComponent, SuspiciousBehavior_NegativeInput) {
    CREATE_MOCK(mymock);

    // ARRANGE
    int input = -10;

    // ACT
    int result = legacy_function(input);

    // ASSERT: Current behavior (possibly incorrect)
    EXPECT_EQ(-73, result);  // No input validation!
}
```

## Capturing Side Effects

Don't just test return values - capture all side effects:

```cpp
TEST(MotorControl, CapturesCurrentBehavior_StartSequence) {
    CREATE_MOCK(mymock);

    // ARRANGE: Capture expected call sequence
    InSequence seq;
    EXPECT_CALL(mymock, HAL_GPIO_Write(ENABLE_PIN, HIGH)).Times(1);
    EXPECT_CALL(mymock, HAL_PWM_SetDuty(50)).Times(1);
    EXPECT_CALL(mymock, HAL_GPIO_Write(STATUS_LED, HIGH)).Times(1);

    // ACT
    Motor_Start();

    // TODO: Verify startup sequence against hardware spec
}
```

## Dealing with Globals

Reset global state in test fixture:

```cpp
class LegacyMotorTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Reset legacy globals before each test
        extern int g_motor_error_count;
        extern bool g_motor_running;
        g_motor_error_count = 0;
        g_motor_running = false;
    }
};

TEST_F(LegacyMotorTest, CapturesErrorCountBehavior) {
    CREATE_MOCK(mymock);

    // ACT
    for (int i = 0; i < 5; i++) {
        Motor_HandleError();
    }

    // ASSERT
    extern int g_motor_error_count;
    EXPECT_EQ(5, g_motor_error_count);
}
```

## Testing Static Functions

**Preferred**: Test through public API (black-box testing):

```cpp
// Static helper is tested indirectly through public function
TEST(Calculator, PublicFunction_TestsStaticHelperIndirectly) {
    CREATE_MOCK(mymock);

    // ACT
    int result = Calculator_Compute(10, 20);

    // ASSERT: Verifies internal static helper works correctly
    EXPECT_EQ(30, result);
}
```

**Alternative**: Use existing `UNIT_TEST` preprocessor seam if absolutely necessary (already present in some legacy codebases).

## Golden Master Pattern for Complex Output

For complex structures or multi-value output:

```cpp
TEST(ReportGenerator, CapturesCurrentReportFormat) {
    CREATE_MOCK(mymock);

    // ACT
    ReportData report = GenerateReport();

    // ASSERT: Capture all fields (golden master)
    EXPECT_EQ(42, report.item_count);
    EXPECT_EQ(1000, report.total_value);
    EXPECT_STREQ("2026-02-05", report.date);
    EXPECT_EQ(STATUS_OK, report.status);

    // TODO: Verify report format matches business requirements
}
```

## After Characterization: The Refactoring Cycle

1. **Tests pass** → Baseline established
2. **Refactor code** → Improve structure
3. **Tests still pass** → Behavior preserved
4. **If tests fail** → Unintended change detected, revert or fix

Then add specification tests for **correct** behavior alongside characterization tests.

## Best Practices

✅ Always add RST traceability blocks (see [traceability.md](traceability.md))
✅ Mark suspicious behavior with `TODO` comments
✅ Capture side effects, not just return values
✅ Use `CREATE_MOCK(mymock)` pattern (project standard)
✅ Reset global state in `SetUp()`
✅ Document what behavior is captured, not what is "correct"

## Anti-Patterns

❌ Assuming captured behavior is correct (it's just current behavior)
❌ Skipping edge cases and error paths
❌ Not documenting suspicious behavior
❌ Changing production code while characterizing (characterize first!)
❌ Creating tests without traceability

## References

- Michael Feathers: "Working Effectively with Legacy Code", Chapter 13
- Use `analyze_dependencies.py` script to identify testing needs
