# Hammocking Guide: Isolating Components with Mocks

## Table of Contents

| Section | Line | When to read |
|---------|------|--------------|
| [What is Hammocking?](#what-is-hammocking) | ~15 | New to the concept |
| [Why Hammock?](#why-hammock) | ~20 | Motivation and benefits |
| [SPLED Auto-Mocker System](#spled-auto-mocker-system) | ~25 | How mocks are generated in this project |
| [Hammocking Tool Command Line Usage](#hammocking-tool-command-line-usage) | ~85 | Running the mock generator manually |
| [Mock Expectation Patterns](#mock-expectation-patterns) | ~222 | EXPECT_CALL, WillOnce, Times, matchers |
| [Hammocking Strategies](#hammocking-strategies) | ~494 | Full vs partial mocking, legacy code |
| [Common Hammocking Patterns](#common-hammocking-patterns) | ~570 | Callbacks, state machines, sequences |
| [Debugging Mock Issues](#debugging-mock-issues) | ~656 | Fixing unmatched calls, missing expectations |
| [Best Practices](#best-practices) | ~745 | Do's and don'ts |
| [Advanced Techniques](#advanced-techniques) | ~808 | Custom matchers, action sequences |
| [Summary](#summary) | ~856 | Quick reference |

## What is Hammocking?

**Hammocking** is the practice of isolating a component under test by replacing all its external dependencies with mocks. Like a hammock suspends a person in the air, hammocking suspends the component under test, with mocks providing controlled input/output without involving real hardware or other components.

```text
    [Mock A] ←→ [Component Under Test] ←→ [Mock B]
                        ↕
                    [Mock C]
```

## Why Hammock?

1. **Isolation**: Test one component at a time without dependencies
2. **Control**: Precisely control inputs and verify outputs
3. **Speed**: No hardware delays, tests run in milliseconds
4. **Determinism**: No non-deterministic hardware behavior
5. **Coverage**: Easy to test error paths and edge cases

## SPLED Auto-Mocker System

### How Mocks Are Generated

The SPLED build system automatically generates mocks based on component dependencies:

1. **CMakeLists.txt** declares dependencies:

   ```cmake
   spl_add_required_interface(components/hal_gpio)
   spl_add_required_interface(components/rte)
   ```

2. **Build system** analyzes missing symbols when partial linking component source

3. **Auto-generated files** created:
   - `mockup_components_<component_name>.h` - Mock class declaration
   - `mockup_components_<component_name>.cc` - Mock implementation

4. **Test includes** generated mock header:

   ```cpp
   #include "mockup_components_<component_name>.h"
   ```

### What Gets Mocked

Any function from a dependency declared in `spl_add_required_interface()`:

```c
// In hal_gpio.h (dependency)
void HAL_GPIO_Write(uint8_t pin, bool value);
bool HAL_GPIO_Read(uint8_t pin);

// Auto-generated in mockup_components_<component>.h
MOCK_METHOD(void, HAL_GPIO_Write, (uint8_t pin, bool value));
MOCK_METHOD(bool, HAL_GPIO_Read, (uint8_t pin));
```

### Project-Specific Mock Macro

Always use `CREATE_MOCK(mymock)` inside each test:

```cpp
TEST(Component, TestName)
{
    CREATE_MOCK(mymock);  // Project-specific initialization
    
    // Use mymock for expectations
    EXPECT_CALL(mymock, Function()).Times(1);
}
```

**Do NOT** manually instantiate mocks:

```cpp
// ✗ WRONG - Don't do this
StrictMock<MockClass> mock;
MockClass mock;

// ✓ CORRECT - Use project macro
CREATE_MOCK(mymock);
```

## Hammocking Tool Command Line Usage

The `hammocking` Python tool generates GoogleMock code from unresolved symbols. While SPLED automates this, understanding the tool helps debug build issues.

### Basic Command

```shell
python -m hammocking --sources <source_files> --outdir <output_dir> \
    (--symbols <symbol_list> | --plink <object_file>)
```

### Required Arguments

- **`--sources`**: Source files representing the component under test

  ```shell
  --sources src/component.c src/helper.c
  ```

- **`--outdir`**: Directory where mock files will be generated

  ```shell
  --outdir build/mocks/
  ```

- **Symbol specification** (choose one):
  - **`--symbols`**: Comma-separated list of symbols to mock

    ```shell
    --symbols HAL_GPIO_Read,HAL_GPIO_Write,Timer_GetTicks
    ```

  - **`--plink`**: Partial link object file containing unresolved symbols

    ```shell
    --plink build/component.o
    ```

### Optional Arguments

- **`--except`**: Exclude symbols from headers in these directories

  ```shell
  --except /usr/include /opt/toolchain/include
  ```
  
  Use this to exclude system library symbols that will be provided during linking.
  Defaults to `/usr/include` for system headers.

### Example: Single Compilation Unit

```makefile
# Compile component to object file
component.o: component.c
 gcc -c component.c -o component.o

# Partial link to identify unresolved symbols
component.plink.o: component.o
 ld -r component.o -o component.plink.o

# Generate mocks from unresolved symbols
mockup_component.cc: component.plink.o
 python -m hammocking \
  --sources component.c \
  --plink component.plink.o \
  --outdir .

# Compile test with mocks
test_component: test_component.cc mockup_component.cc component.o
 g++ test_component.cc mockup_component.cc component.o \
  -lgtest -lgmock -o test_component
```

### Example: Multiple Compilation Units

```makefile
# Compile all component sources
SOURCES = component.c helper.c utils.c
OBJECTS = $(SOURCES:.c=.o)

%.o: %.c
 gcc -c $< -o $@

# Partial link all objects
component.plink.o: $(OBJECTS)
 ld -r $(OBJECTS) -o component.plink.o

# Generate mocks from combined unresolved symbols
mockup_component.cc: component.plink.o
 python -m hammocking \
  --sources $(SOURCES) \
  --plink component.plink.o \
  --outdir . \
  --except /usr/include

# Build test
test_component: test_component.cc mockup_component.cc $(OBJECTS)
 g++ test_component.cc mockup_component.cc $(OBJECTS) \
  -lgtest -lgmock -pthread -o test_component
```

### How SPLED Uses Hammocking

In SPLED's CMake build system:

1. Component sources are compiled to `.o` files
2. Partial linking (`ld -r`) combines objects and identifies missing symbols
3. `hammocking` tool generates `mockup_components_<name>.cc` and `.h` files
4. Test build links component objects with generated mocks and GoogleTest

This happens automatically when building with `--buildKit test`.

### Debugging Hammocking Issues

**Problem**: Mock not generated for expected function

**Check**:

```shell
# View unresolved symbols in partial link
nm -u component.plink.o | grep <function_name>
```

**Problem**: Too many symbols mocked (including system functions)

**Solution**: Use `--except` to exclude system headers:

```shell
--except /usr/include /usr/local/include
```

**Problem**: Symbol from component itself is being mocked

**Cause**: Function declared but not defined in component sources

**Solution**: Either implement the function or add it to `--except` if provided externally

## Mock Expectation Patterns

### Basic Expectations

#### Single Call with Specific Argument

```cpp
// Function called exactly once with specific value
EXPECT_CALL(mymock, SetLED(true))
    .Times(1);

// Times(1) is default, can be omitted
EXPECT_CALL(mymock, SetLED(true));
```

#### Multiple Calls

```cpp
// Called exactly 5 times
EXPECT_CALL(mymock, ReadSensor())
    .Times(5)
    .WillRepeatedly(Return(100));

// Called at least once
EXPECT_CALL(mymock, LogMessage(_))
    .Times(AtLeast(1));

// Called between 3 and 5 times
EXPECT_CALL(mymock, Process())
    .Times(Between(3, 5));
```

#### Never Called

```cpp
// Verify function is NOT called
EXPECT_CALL(mymock, ErrorHandler())
    .Times(0);
```

### Return Values

#### Single Return Value

```cpp
// Return same value every call
EXPECT_CALL(mymock, GetTemperature())
    .WillRepeatedly(Return(25));
```

#### Sequence of Different Values

```cpp
// Return different values on successive calls
EXPECT_CALL(mymock, GetState())
    .WillOnce(Return(STATE_INIT))
    .WillOnce(Return(STATE_READY))
    .WillOnce(Return(STATE_ACTIVE))
    .WillRepeatedly(Return(STATE_DONE));  // All further calls
```

#### Computed Return Values

```cpp
// Return value based on input argument
EXPECT_CALL(mymock, Multiply(_, _))
    .WillRepeatedly([](int a, int b) { return a * b; });
```

### Argument Matching

#### Specific Values

```cpp
// Exact match required
EXPECT_CALL(mymock, Configure(9600, PARITY_EVEN));
```

#### Wildcard (Any Value)

```cpp
// Accept any value for argument
EXPECT_CALL(mymock, WriteData(_))
    .WillOnce(Return(OK));

// Multiple wildcards
EXPECT_CALL(mymock, SetPosition(_, _));
```

#### Conditional Matchers

```cpp
// Greater than
EXPECT_CALL(mymock, SetBrightness(Gt(50)))
    .Times(1);

// Less than
EXPECT_CALL(mymock, SetThreshold(Lt(100)))
    .Times(1);

// In range
EXPECT_CALL(mymock, SetValue(AllOf(Ge(0), Le(255))))
    .Times(1);

// One of several values
EXPECT_CALL(mymock, SetMode(AnyOf(MODE_A, MODE_B, MODE_C)))
    .Times(1);

// Not equal to
EXPECT_CALL(mymock, SetState(Ne(STATE_ERROR)))
    .Times(1);
```

#### Pointer Matchers

```cpp
// Null pointer
EXPECT_CALL(mymock, ProcessData(IsNull()))
    .WillOnce(Return(ERROR));

// Non-null pointer
EXPECT_CALL(mymock, ProcessData(NotNull()))
    .WillOnce(Return(OK));

// Specific pointer value
const uint8_t* expected_ptr = &data;
EXPECT_CALL(mymock, ProcessData(Eq(expected_ptr)))
    .Times(1);
```

### Custom Matchers for Complex Types

#### Struct Comparison

```cpp
// Define comparison function
bool areConfigsEqual(const Config* a, const Config* b)
{
    return a->baudrate == b->baudrate &&
           a->parity == b->parity &&
           a->stop_bits == b->stop_bits;
}

// Create custom matcher
MATCHER_P(ConfigEq, expected, "")
{
    return areConfigsEqual(&arg, &expected);
}

// Overload operator<< for readable errors
std::ostream& operator<<(std::ostream& os, const Config& cfg)
{
    os << "Config(baudrate=" << cfg.baudrate
       << ", parity=" << (int)cfg.parity
       << ", stop_bits=" << (int)cfg.stop_bits << ")";
    return os;
}

// Use in test
TEST(UART, ConfiguresCorrectly)
{
    CREATE_MOCK(mymock);
    Config expected = {
        .baudrate = 115200,
        .parity = PARITY_NONE,
        .stop_bits = 1
    };
    
    EXPECT_CALL(mymock, ApplyConfig(ConfigEq(expected)))
        .Times(1);
    
    UART_Initialize();
}
```

#### Array/Buffer Comparison

```cpp
// Matcher for byte array
MATCHER_P2(BufferEq, expected, size, "")
{
    return memcmp(arg, expected, size) == 0;
}

// Use in test
TEST(Communication, SendsCorrectData)
{
    CREATE_MOCK(mymock);
    const uint8_t expected_data[] = {0x01, 0x02, 0x03, 0x04};
    
    EXPECT_CALL(mymock, Transmit(
        BufferEq(expected_data, sizeof(expected_data)),
        sizeof(expected_data)))
        .Times(1);
    
    Communication_Send(expected_data, sizeof(expected_data));
}
```

### Call Ordering

#### Strict Ordering with InSequence

```cpp
TEST(StateMachine, TransitionsInOrder)
{
    CREATE_MOCK(mymock);
    InSequence seq;  // Enforce call order
    
    // These MUST occur in this exact order
    EXPECT_CALL(mymock, Initialize()).Times(1);
    EXPECT_CALL(mymock, Configure()).Times(1);
    EXPECT_CALL(mymock, Start()).Times(1);
    
    StateMachine_Execute();
}
```

#### Partial Ordering

```cpp
TEST(Component, SomeOrderedSomeNot)
{
    CREATE_MOCK(mymock);
    
    // These two must be ordered relative to each other
    {
        InSequence seq;
        EXPECT_CALL(mymock, StepA()).Times(1);
        EXPECT_CALL(mymock, StepB()).Times(1);
    }
    
    // This can happen anytime
    EXPECT_CALL(mymock, LogStatus())
        .Times(AnyNumber());
    
    Component_Execute();
}
```

### Side Effects

#### Modifying Output Parameters

```cpp
// Mock function that writes to pointer argument
EXPECT_CALL(mymock, ReadValue(_))
    .WillOnce(DoAll(
        SetArgPointee<0>(42),  // Set first argument (*arg) to 42
        Return(OK)
    ));

// Usage in code under test:
// uint8_t value;
// status_t result = ReadValue(&value);
// // value is now 42, result is OK
```

#### Multiple Side Effects

```cpp
EXPECT_CALL(mymock, ComplexOperation(_, _))
    .WillOnce(DoAll(
        SetArgPointee<0>(100),    // Set first arg to 100
        SetArgPointee<1>(200),    // Set second arg to 200
        InvokeWithoutArgs([]() {  // Custom action
            // Do something
        }),
        Return(OK)                // Return value
    ));
```

## Hammocking Strategies

### Strategy 1: Minimal Hammocking

Only mock what you must. Test as much real code as possible:

```cpp
// Component under test uses both HAL and utility functions
// Only mock HAL (external dependency), use real utility functions

TEST(Component, ProcessesCorrectly)
{
    CREATE_MOCK(mymock);

    // ARRANGE: Mock HAL calls; utility functions run for real (not mocked)
    EXPECT_CALL(mymock, HAL_GPIO_Read(_))
        .WillOnce(Return(true));
    EXPECT_CALL(mymock, HAL_GPIO_Write(_, _))
        .Times(1);

    // ACT
    Component_Process();
}
```

### Strategy 2: Full Isolation

Mock all dependencies for complete isolation:

```cpp
TEST(Component, IsolatedTest)
{
    CREATE_MOCK(mymock);
    
    // Mock every external interface
    EXPECT_CALL(mymock, HAL_GPIO_Read(_)).WillOnce(Return(true));
    EXPECT_CALL(mymock, RTE_GetSignal(_)).WillOnce(Return(42));
    EXPECT_CALL(mymock, Timer_GetTicks()).WillOnce(Return(1000));
    EXPECT_CALL(mymock, Logger_Log(_)).Times(AnyNumber());
    
    Component_Process();
}
```

### Strategy 3: Default Behaviors

Set up default mock behavior at test fixture level:

```cpp
class ComponentTest : public Test
{
protected:
    void SetUp() override
    {
        CREATE_MOCK(mymock);
        
        // Default behaviors for common calls
        ON_CALL(mymock, HAL_GPIO_Read(_))
            .WillByDefault(Return(false));
        ON_CALL(mymock, Timer_GetTicks())
            .WillByDefault(Return(0));
        
        Component_Init();
    }
};

TEST_F(ComponentTest, SpecificTest)
{
    // Override default for this test
    EXPECT_CALL(mymock, HAL_GPIO_Read(BUTTON_PIN))
        .WillOnce(Return(true));
    
    Component_Process();
}
```

## Common Hammocking Patterns

### Pattern: Simulating Hardware State

```cpp
TEST(Sensor, ReadsMultipleSensors)
{
    CREATE_MOCK(mymock);
    
    // Simulate different sensor readings
    EXPECT_CALL(mymock, ADC_Read(SENSOR_TEMP))
        .WillOnce(Return(2500));  // 25.0°C
    EXPECT_CALL(mymock, ADC_Read(SENSOR_HUMIDITY))
        .WillOnce(Return(6000));  // 60.0%
    EXPECT_CALL(mymock, ADC_Read(SENSOR_PRESSURE))
        .WillOnce(Return(10132)); // 1013.2 hPa
    
    Sensor_ReadAll();
}
```

### Pattern: Simulating Timing

```cpp
TEST(Debounce, HandlesButtonBounce)
{
    CREATE_MOCK(mymock);
    
    // Simulate bouncing signal over time
    EXPECT_CALL(mymock, ReadButton())
        .WillOnce(Return(true))   // Press
        .WillOnce(Return(false))  // Bounce low
        .WillOnce(Return(true))   // Bounce high
        .WillOnce(Return(false))  // Bounce low
        .WillOnce(Return(true))   // Stable high
        .WillRepeatedly(Return(true));
    
    for (int tick = 0; tick < 100; tick++)
    {
        Debounce_Tick1ms();
    }
}
```

### Pattern: Error Injection

```cpp
TEST(Communication, HandlesTransmissionError)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    EXPECT_CALL(mymock, TransmitByte(_))
        .WillOnce(Return(ERROR_TIMEOUT));
    EXPECT_CALL(mymock, ScheduleRetry())
        .Times(1);

    // ACT
    status_t result = Communication_Send(data);

    // ASSERT
    EXPECT_EQ(result, ERROR_TIMEOUT);
}
```

### Pattern: Conditional Mocking (KConfig)

```cpp
TEST(Component, BehaviorWithFeature)
{
    CREATE_MOCK(mymock);
    
#ifdef CONFIG_ADVANCED_FEATURE
    // Mock only called when feature enabled
    EXPECT_CALL(mymock, AdvancedFunction())
        .Times(1);
#else
    // Feature disabled, function should not be called
    EXPECT_CALL(mymock, AdvancedFunction())
        .Times(0);
#endif
    
    Component_Process();
}
```

## Debugging Mock Issues

### Issue: Uninteresting Mock Function Call

**Symptom**:

```text
GMOCK WARNING: Uninteresting mock function call - returning default value.
    Function call: HAL_GPIO_Write(3, 1)
```

**Cause**: Component called a mocked function without an `EXPECT_CALL`

**Solution**: Add expectation for the call

```cpp
EXPECT_CALL(mymock, HAL_GPIO_Write(3, true))
    .Times(1);
```

### Issue: Expected Call Not Made

**Symptom**:

```text
Expected: to be called once
  Actual: never called
```

**Cause**: Component logic didn't call the expected function

**Solutions**:

1. Check component logic - is the call conditional?
2. Verify preconditions are met
3. Check KConfig guards (`#ifdef CONFIG_X`)
4. Verify mock expectations match actual function signature

### Issue: Wrong Number of Calls

**Symptom**:

```text
Expected: to be called once
  Actual: called 3 times
```

**Cause**: Component calls function more than expected

**Solutions**:

1. Use `Times(3)` if 3 calls are correct
2. Use `Times(AtLeast(1))` if flexible
3. Check for loops or repeated logic in component

### Issue: Call Order Violation

**Symptom**:

```text
Expected: call sequence violated
```

**Cause**: Functions called in different order than `InSequence` expects

**Solutions**:

1. Verify call order actually matters for this test
2. Remove `InSequence` if order doesn't matter
3. Adjust expectations to match actual call order

### Issue: Argument Mismatch

**Symptom**:

```text
Unexpected mock function call
Expected: SetValue(42)
  Actual: SetValue(43)
```

**Cause**: Component passes different value than expected

**Solutions**:

1. Verify expected value is correct
2. Use wildcard `_` if exact value doesn't matter
3. Use range matcher `Gt(40)` if approximate match acceptable

## GMock Gotchas

These are subtle traps that produce confusing compile errors or false test failures. They are
generic to GMock but bite often in embedded C projects that wrap dependencies in function-like
macros and rely on output-parameter return conventions.

### Function-Like Macros Inside EXPECT_CALL

If a dependency is invoked through a **function-like macro** (common with generated RTE/service
call wrappers, e.g. `Xxx_Call_Service(...)`), you cannot put that macro inside `EXPECT_CALL`.
GMock builds an internal `gmock_`-prefixed token from the method name; the preprocessor then tries
to paste `gmock_` onto the macro's `(`, producing an invalid token and a compile error.

```cpp
// WRONG — Foo_Call_Service is a function-like macro; token-pasting breaks EXPECT_CALL
EXPECT_CALL(mymock, Foo_Call_Service(_, _)).Times(1);   // compile error

// CORRECT — use the bare mock function name from the MOCK_METHOD declaration
EXPECT_CALL(mymock, ServiceImpl(_, _)).Times(1);
```

**Rule:** Inside `EXPECT_CALL`, always use the plain function name that appears in `MOCK_METHOD` —
never a macro alias that expands to it.

### Output-Parameter Mocks Need SetArgPointee on Success Paths

When a mocked function returns its result through an **output pointer** (not a return value), the
default action for a `void` mock does **not** initialize the pointed-to value. It keeps whatever
the caller-allocated variable held — often uninitialized stack garbage. If the code under test then
branches on that value, it takes an unintended path instead of the one you meant to exercise.

```cpp
// WRONG — mock leaves *off_course uninitialised; the code under test branches on garbage
EXPECT_CALL(mymock, RteGetOffCourse(_)).Times(1);

// CORRECT — mock writes the intended value into the output argument (0-based index)
EXPECT_CALL(mymock, RteGetOffCourse(_))
    .WillOnce(SetArgPointee<0>(TRUE));   // arg 0 = bool_t *off_course
```

**Discovery method:** If a test lands on the wrong branch, trace back to the caller that read a
value from a mocked output parameter, and add `SetArgPointee<N>(value)` (or `DoAll(SetArgPointee<N>(value), Return(...))`
for non-void mocks) to that mock.

### AnyNumber() vs AtLeast(1) for Transitive Mocks

When the function under test triggers a *real* (unmocked) helper that only **indirectly** reaches
a mock, whether that mock is called depends on every intermediate guard in the chain. If any guard
short-circuits (e.g. "no active job — nothing to report"), the mock is never reached even though
the top-level trigger fired.

```cpp
// CORRECT — transitive mock may or may not be reached; assert only that it is NOT called on the negative path
if (param.expectTrigger) {
    EXPECT_CALL(mymock, DownstreamEffect(_)).Times(AnyNumber());
} else {
    EXPECT_CALL(mymock, DownstreamEffect(_)).Times(0);
}

// WRONG — AtLeast(1) fails whenever an intermediate guard short-circuits the chain
EXPECT_CALL(mymock, DownstreamEffect(_)).Times(AtLeast(1));
```

To positively assert a transitive call with `AtLeast(1)`, set up **all** intermediate state
required to activate the full chain, in a test case dedicated to that deep path.

### Suppressing Transitive Calls from Pass-Through Wrappers

Some call wrappers expand to **direct calls into other production functions of the same component**
rather than to a mock. When the function under test uses one, the real production function runs and
may call mocks your test does not care about — producing `GMOCK WARNING: Uninteresting mock
function call`. Suppress those with `Times(AnyNumber())`, guarded by the same feature flag that
conditionally compiles the callee:

```cpp
EXPECT_CALL(mymock, TraceUpdateSignal(_, _)).Times(AnyNumber());  // always-present trace hook

#ifdef CONFIG_AUTO_OFF
    // reached transitively via the pass-through wrapper, not by the code under test directly
    EXPECT_CALL(mymock, FeatureSideEffect(_, _)).Times(AnyNumber());
#endif
```

To tell pass-through wrappers from real stubs, inspect the generated call-wrapper header: a
pass-through expands to a real function call (`#define Xxx_Call_Handler(a,b) (Handler(a,b), OK)`),
a stub expands to the mocked function.

## Best Practices

### 1. Mock at Interface Boundaries

Mock external interfaces, not internal functions:

```cpp
// ✓ GOOD - Mock HAL interface
EXPECT_CALL(mymock, HAL_GPIO_Read(_));

// ✗ BAD - Don't mock internal helper functions
// EXPECT_CALL(mymock, Internal_ValidateInput(_));
```

### 2. Use Descriptive Matchers

Make expectations readable:

```cpp
// ✓ GOOD - Clear intent
EXPECT_CALL(mymock, SetBrightness(AllOf(Ge(0), Le(100))));

// ✗ BAD - Unclear wildcard
EXPECT_CALL(mymock, SetBrightness(_));
```

### 3. Prefer WillOnce for Sequences

```cpp
// ✓ GOOD - Explicit sequence
EXPECT_CALL(mymock, GetState())
    .WillOnce(Return(INIT))
    .WillOnce(Return(READY))
    .WillOnce(Return(ACTIVE));

// ✗ BAD - Unclear with Times()
EXPECT_CALL(mymock, GetState())
    .Times(3)
    .WillRepeatedly(Return(ACTIVE));  // Wrong - returns same value
```

### 4. Document Mock Behavior

Explain non-obvious mock setups:

```cpp
// ARRANGE: Sensor bounces for 30ms before stabilizing
EXPECT_CALL(mymock, ReadSensor())
    .Times(30)
    .WillRepeatedly(Return(UNSTABLE));
EXPECT_CALL(mymock, ReadSensor())
    .Times(20)
    .WillRepeatedly(Return(STABLE));
```

### 5. Keep Mocks Simple

If mock setup gets complex, consider:

- Breaking test into smaller tests
- Using helper functions for complex setups
- Testing at a higher level of abstraction

## Advanced Techniques

### Custom Actions

```cpp
// Define custom action
ACTION_P(SaveArg0To, variable)
{
    *variable = arg0;
}

// Use in test
TEST(Component, CapturesValue)
{
    CREATE_MOCK(mymock);
    uint8_t captured_value = 0;
    
    EXPECT_CALL(mymock, SetValue(_))
        .WillOnce(SaveArg0To(&captured_value));
    
    Component_Process();
    
    // Verify captured value
    EXPECT_EQ(captured_value, 42);
}
```

### Delegating to Real Implementation

```cpp
// Real function implementation
static bool RealValidation(uint8_t value)
{
    return value >= 10 && value <= 100;
}

TEST(Component, UsesMixOfMockAndReal)
{
    CREATE_MOCK(mymock);
    
    // Delegate validation to real function
    EXPECT_CALL(mymock, Validate(_))
        .WillRepeatedly(Invoke(RealValidation));
    
    Component_Process();
}
```

## Summary

Hammocking with mocks provides:

- **Isolation**: Test components independently
- **Control**: Deterministic test conditions
- **Speed**: Fast test execution
- **Coverage**: Easy error path testing

Key practices:

- Use `CREATE_MOCK(mymock)` always
- Mock at interface boundaries
- Use Arrange-Act-Assert for mock setup
- Keep expectations simple and readable
- Document complex mock behaviors
