# Workflow and Debugging Guide

## Table of Contents

| Section | Line | When to read |
|---------|------|--------------|
| [Development Workflow](#development-workflow) | ~18 | Step-by-step test creation |
| [Debugging Test Failures](#debugging-test-failures) | ~100 | Fixing failing tests |
| [Testing for Refactoring](#testing-for-refactoring) | ~296 | Capturing behavior before restructuring |
| [Test Maintenance](#test-maintenance) | ~359 | Updating tests after code changes |
| [Performance Considerations](#performance-considerations) | ~441 | Keeping test suite fast |

## Development Workflow

### 1. Analyze Component for Testing

```powershell
# Check component structure
ls components\<name>\

# Read design doc for requirements
cat components\<name>\doc\index.md

# Examine source for behavior
cat components\<name>\src\<name>.c

# Check dependencies for mocking
cat components\<name>\CMakeLists.txt | Select-String "spl_add_required_interface"
```

### 2. Create Test File

Location: `components/<name>/test/test_<name>.cc`

Template:

```cpp
#include <gtest/gtest.h>

extern "C"
{
#include "autoconf.h"  // KConfig flags
#include "<component_name>.h"
}

#include "mockup_components_<component_name>.h"  // Auto-generated mocks

// Test fixture (if needed)
class <ComponentName>Test : public Test
{
protected:
    void SetUp() override
    {
        // Initialize component
    }
};

// Tests go here with RST traceability
```

### 3. Write Tests

For each requirement or behavior:

1. Identify the scenario (what condition/input)
2. Structure as Arrange-Act-Assert
3. Add RST traceability
4. Use descriptive test name

### 4. Register Test in CMake

In `components/<name>/CMakeLists.txt`:

```cmake
# Add test source
spl_add_test_source(test/test_<name>.cc)
```

### 5. Build and Run

```powershell
.\build.ps1 -build -buildKit test -buildType Debug -variants <Variant> -target components_<name>_unittests
```

### 6. Review Results

Open test report using VS Code task: "Open component test report"

Check:
- Test pass/fail status
- Traceability coverage (which requirements tested)
- Code coverage percentage
- Missing test cases

## Debugging Test Failures

### Common Failures

#### 1. Uninteresting Mock Function Call

**Error**:
```
GMOCK WARNING: Uninteresting mock function call
```

**Cause**: Component calls a mocked function without `EXPECT_CALL`

**Fix**: Add expectation or verify the call should happen

**Example**:
```cpp
// Problem: Missing expectation
TEST(LED, ShouldWork)
{
    CREATE_MOCK(mymock);
    LED_TurnOn();  // Calls HAL_GPIO_Write but no expectation set!
}

// Solution: Add expectation
TEST(LED, ShouldWork)
{
    CREATE_MOCK(mymock);
    EXPECT_CALL(mymock, HAL_GPIO_Write(LED_PIN, HIGH))
        .Times(1);
    LED_TurnOn();
}
```

#### 2. Function Call Count Mismatch

**Error**:
```
Expected: to be called once
  Actual: called 0 times
```

**Cause**: Component doesn't call expected function

**Debugging Steps**:
1. Check if logic path is reachable
2. Verify test setup (preconditions)
3. Check KConfig guards (`#ifdef CONFIG_*`)
4. Review component state machine

**Example**:
```cpp
// Problem: Feature disabled in variant
TEST(Power, AutoShutoffWorks)
{
    CREATE_MOCK(mymock);
    EXPECT_CALL(mymock, ShutdownSystem()).Times(1);  // Fails if CONFIG_AUTO_OFF disabled
    Power_Tick(5000);
}

// Solution: Guard test with feature flag
#ifdef CONFIG_AUTO_OFF
TEST(Power, AutoShutoffWorks)
{
    CREATE_MOCK(mymock);
    EXPECT_CALL(mymock, ShutdownSystem()).Times(1);
    Power_Tick(5000);
}
#endif
```

#### 3. Wrong Call Order

**Error**:
```
Expected: call sequence violated
```

**Cause**: Calls occur in different order than `InSequence` expects

**Fix**: Use `InSequence` only when order matters, or adjust expectations

**Example**:
```cpp
// Problem: Too strict ordering
TEST(Startup, InitializesCorrectly)
{
    CREATE_MOCK(mymock);
    InSequence seq;  // Forces strict order
    
    EXPECT_CALL(mymock, InitClock()).Times(1);
    EXPECT_CALL(mymock, InitGPIO()).Times(1);  // Fails if GPIO initialized first
    
    Startup_Run();
}

// Solution 1: Remove InSequence if order doesn't matter
TEST(Startup, InitializesCorrectly)
{
    CREATE_MOCK(mymock);
    // No InSequence - order flexible
    
    EXPECT_CALL(mymock, InitClock()).Times(1);
    EXPECT_CALL(mymock, InitGPIO()).Times(1);
    
    Startup_Run();
}

// Solution 2: Verify order is actually correct
TEST(Startup, InitializesInOrder)
{
    CREATE_MOCK(mymock);
    InSequence seq;
    
    // Verify actual call order from code
    EXPECT_CALL(mymock, InitGPIO()).Times(1);   // Check source: GPIO first
    EXPECT_CALL(mymock, InitClock()).Times(1);  // Then clock
    
    Startup_Run();
}
```

#### 4. Missing Mock Header

**Error**:
```
undefined reference to MockFunction
```

**Cause**: Dependency not in `spl_add_required_interface()` or missing include

**Fix**: Add dependency to CMakeLists.txt, include mock header

**Example**:
```cmake
# In components/my_component/CMakeLists.txt

# Problem: Missing dependency declaration
# (no spl_add_required_interface for hal_gpio)

# Solution: Add required interface
spl_add_required_interface(components/hal_gpio)
```

Then rebuild to regenerate mocks:
```powershell
.\build.ps1 -build -buildKit test -buildType Debug -variants Disco -target components_my_component_unittests
```

### Advanced Debugging Techniques

#### Print Mock Call History

```cpp
TEST(Component, DebugCalls)
{
    CREATE_MOCK(mymock);
    
    // Enable verbose output
    testing::FLAGS_gtest_print_time = 1;
    
    // Calls will be printed
    Component_Function();
    
    // Manually print what was called (if needed)
    // Use EXPECT_CALL with _ wildcard to see all calls
    EXPECT_CALL(mymock, AnyFunction(_))
        .Times(AnyNumber());
}
```

#### Isolate Problem Test

```powershell
# Run single test
.\build.ps1 -build -buildKit test -buildType Debug -variants Disco -target components_my_component_unittests
cd build\Disco\test\Debug\
.\components_my_component_unittests.exe --gtest_filter="MyComponent.SpecificTest"
```

#### Check Coverage

Use coverage report to identify untested code paths:

```powershell
# Generate coverage report
.\build.ps1 -build -buildKit test -variants Disco -target reports

# Open coverage (VS Code task: "Open component coverage report")
```

Uncovered lines may reveal:
- Missing test cases
- Dead code
- Unreachable branches

## Testing for Refactoring

### Capturing Existing Behavior

When preparing to refactor legacy code:

1. **Write characterization tests**: Capture current behavior even if not formally specified
2. **Test at API boundaries**: Focus on public functions, not internal implementation
3. **Cover all code paths**: Use coverage report to identify untested branches
4. **Lock down edge cases**: Test boundary values, error conditions, state transitions

### Characterization Test Example

```cpp
/*!
 * @rst
 * .. test:: LegacyModule.CurrentBehavior_StoresLastValue
 *    :id: TS_LEG-001
 *    :tests: SWDD_LEG-100
 * 
 * Characterization test: Module stores last written value internally.
 * This test locks down current behavior before refactoring.
 * @endrst
 */
TEST(LegacyModule, CurrentBehavior_StoresLastValue)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    Legacy_Init();

    // ACT
    Legacy_SetValue(42);

    // ASSERT
    EXPECT_EQ(Legacy_GetValue(), 42);
}
```

### Refactoring Workflow

1. **Write comprehensive tests** capturing existing behavior
2. **Verify tests pass** with current implementation
3. **Refactor code** (restructure, rename, extract functions)
4. **Run tests** - they should still pass
5. **Update tests** only if intentionally changing behavior

### Coverage-Driven Test Development

Use coverage reports to guide test creation:

```powershell
# Initial test run
.\build.ps1 -build -buildKit test -buildType Debug -variants Disco -target components_my_component_unittests

# Generate coverage report
.\build.ps1 -build -buildKit test -buildType Debug -variants Disco -target reports

# Review coverage - identify untested branches
# Write tests for uncovered code
# Repeat until target coverage reached (75%+ minimum)
```

## Test Maintenance

### Updating Tests After Code Changes

**Scenario**: Refactored function signature

```cpp
// Old signature
void LED_SetBrightness(uint8_t percent);

// New signature (added validation)
status_t LED_SetBrightness(uint8_t percent);
```

Update tests:
```cpp
// Old test
TEST(LED, SetsBrightness)
{
    CREATE_MOCK(mymock);
    LED_SetBrightness(50);  // void return
}

// Updated test
TEST(LED, SetsBrightness)
{
    CREATE_MOCK(mymock);
    status_t result = LED_SetBrightness(50);  // Check return value
    EXPECT_EQ(result, STATUS_OK);
}

// Add new test for error case
TEST(LED, RejectsInvalidBrightness)
{
    CREATE_MOCK(mymock);
    status_t result = LED_SetBrightness(255);  // Invalid
    EXPECT_EQ(result, STATUS_INVALID_PARAMETER);
}
```

### Handling Breaking Changes

When component behavior intentionally changes:

1. **Update test expectations** to match new behavior
2. **Add traceability** to new requirements
3. **Keep old test** if legacy behavior still needed (with feature flag)
4. **Document change** in test description

Example:
```cpp
#ifdef CONFIG_NEW_BEHAVIOR
/*!
 * @rst
 * .. test:: Button.NewDebounceLogic_100ms
 *    :id: TS_BTN-010
 *    :tests: SWDD_BTN-300
 * 
 * Updated debounce logic: 100ms threshold (was 50ms in legacy).
 * @endrst
 */
TEST(Button, NewDebounceLogic_100ms)
{
    // Test new 100ms behavior
}
#else
/*!
 * @rst
 * .. test:: Button.LegacyDebounceLogic_50ms
 *    :id: TS_BTN-003
 *    :tests: SWDD_BTN-200
 * 
 * Legacy debounce logic: 50ms threshold (deprecated).
 * @endrst
 */
TEST(Button, LegacyDebounceLogic_50ms)
{
    // Test old 50ms behavior
}
#endif
```

## Performance Considerations

### Test Execution Speed

GTest unit tests should run fast (< 1 second per test suite):

- **Avoid delays**: Don't use real timers, simulate ticks instead
- **Minimize setup**: Only initialize what's needed
- **Parallel execution**: Tests run independently, enabling parallel execution

### Coverage vs. Speed Trade-off

Balance comprehensive coverage with test suite speed:

- **Critical paths**: 100% coverage
- **Error handling**: Test all error branches
- **Edge cases**: Cover boundary values
- **Nice-to-have**: Optional features can have lower coverage

Target: 75%+ overall coverage, < 5 minute full test suite execution.
