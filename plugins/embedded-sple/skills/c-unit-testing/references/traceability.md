# Test Traceability Guide

Complete guide to linking tests to requirements using RST documentation blocks.

## Table of Contents

| Section | Line | When to read |
|---------|------|--------------|
| [Overview](#overview) | ~22 | New to traceability |
| [RST Block Structure](#rst-block-structure) | ~30 | Writing RST doc blocks |
| [Test Name Matching Rules](#test-name-matching-rules) | ~53 | TEST, TEST_F, TEST_P naming |
| [Test ID Format](#test-id-format) | ~142 | TS_COMP-### numbering |
| [Requirement Links](#requirement-links-tests-field) | ~190 | Linking to SWDD IDs |
| [Description Guidelines](#description-guidelines) | ~292 | Good vs bad descriptions |
| [Traceability Reports](#traceability-reports) | ~346 | Generating and reading reports |
| [Common Mistakes](#common-mistakes) | ~384 | Name mismatch, duplicates, format errors |
| [Workflow Integration](#workflow-integration) | ~467 | Step-by-step traceability workflow |
| [Template Reference](#template-reference) | ~549 | Complete test template |

## Overview

Every test must link to design requirements for traceability. This enables:
- **Requirement coverage tracking**: Which requirements have tests
- **Change impact analysis**: Which tests affected by requirement changes
- **Compliance verification**: Proof of requirement validation
- **Documentation generation**: Auto-generated test reports

## RST Block Structure

```cpp
/*!
 * @rst
 * .. test:: <TestSuite>.<TestName>
 *    :id: TS_<COMPONENT>-###
 *    :tests: SWDD_<COMPONENT>-###, SWDD_<COMPONENT>-###
 * 
 * Brief description of test behavior.
 * @endrst
 */
```

### Fields Explained

| Field | Purpose | Format | Example |
|-------|---------|--------|---------|
| `.. test::` | Test identifier | `<Suite>.<Name>` | `Button.DebounceWorks` |
| `:id:` | Unique test ID | `TS_<COMP>-###` | `TS_BTN-001` |
| `:tests:` | Requirement links | Comma-separated | `SWDD_BTN-100, SWDD_BTN-101` |
| Description | What test validates | Free text | Brief explanation |

## Test Name Matching Rules

### TEST() - Simple Tests

```cpp
/*!
 * @rst
 * .. test:: LED.TurnsOn_When_ButtonPressed
 *    :id: TS_LED-001
 *    :tests: SWDD_LED-100
 * 
 * LED activates when button input goes high.
 * @endrst
 */
TEST(LED, TurnsOn_When_ButtonPressed)
{
    // Test implementation
}
```

**Rule**: `.. test:: <SuiteName>.<TestName>` matches `TEST(SuiteName, TestName)`

### TEST_F() - Fixture Tests

```cpp
class PowerTest : public Test
{
protected:
    void SetUp() override { Power_Init(); }
};

/*!
 * @rst
 * .. test:: PowerTest.ShutsDown_After_Timeout
 *    :id: TS_PWR-005
 *    :tests: SWDD_PWR-300
 * 
 * Auto-shutdown activates after configured timeout.
 * @endrst
 */
TEST_F(PowerTest, ShutsDown_After_Timeout)
{
    // Test implementation
}
```

**Rule**: `.. test:: <FixtureName>.<TestName>` matches `TEST_F(FixtureName, TestName)`

### TEST_P() - Parameterized Tests

```cpp
class BrightnessTest : public TestWithParam<BrightnessParam>
{
};

/*!
 * @rst
 * .. test:: BrightnessTests/BrightnessTest.CalculatesCorrectly/*
 *    :id: TS_LED-020
 *    :tests: SWDD_LED-400
 * 
 * Brightness calculation for all ambient light values.
 * @endrst
 */
TEST_P(BrightnessTest, CalculatesCorrectly)
{
    // Test implementation
}

INSTANTIATE_TEST_SUITE_P(
    BrightnessTests,
    BrightnessTest,
    Values(/* parameters */)
);
```

**Rule**: `.. test:: <SuiteName>/<FixtureName>.<TestName>/*` matches all parameter instances.

The `/*` wildcard covers all generated test cases under a single TS-ID.

**Traceability decision:**

| Situation | Approach |
|---|---|
| All parameter cases test the **same requirement(s)** (e.g., boundary values for one behavior) | `TEST_P()` + wildcard — one TS-ID is correct |
| Different cases test **different requirements** (e.g., each error code maps to a different SWDD) | Use plain `TEST()` with individual RST blocks — each case gets its own TS-ID |

> Using the wildcard when cases map to different requirements makes the traceability matrix meaningless: you can no longer tell which test case covers which requirement.

## Test ID Format

### Pattern

```
TS_<COMPONENT_ABBREVIATION>-###
```

### Rules

1. **Prefix**: Always `TS_` (Test Specification)
2. **Component**: Short abbreviation (3-5 chars typical)
3. **Separator**: Single hyphen `-`
4. **Number**: Three-digit sequential number, zero-padded
5. **Sequential**: Start at 001, increment for each new test

### Examples

| Component | Test ID | Valid? | Reason |
|-----------|---------|--------|--------|
| Button | `TS_BTN-001` | ✅ | Correct format |
| LED Controller | `TS_LED-042` | ✅ | Zero-padded |
| Power Management | `TS_PWR-100` | ✅ | Three digits |
| GPIO | `TS_GPIO_001` | ❌ | Wrong separator |
| Sensor | `TS_SEN-1` | ❌ | Not zero-padded |
| Motor | `TS-MOT-001` | ❌ | Component separator |

### Choosing Abbreviations

Use consistent abbreviations across the codebase:

```cpp
// Good: Consistent abbreviations
TS_BTN-001   // Button
TS_LED-001   // LED
TS_PWR-001   // Power
TS_UART-001  // UART
TS_ADC-001   // ADC

// Bad: Inconsistent
TS_BUTTON-001
TS_L-001
TS_PM-001
TS_SERIAL-001
```

Check `components/<name>/doc/index.md` for existing abbreviations used in requirements.

## Requirement Links (`:tests:` Field)

### Finding Requirements

Requirements are documented in component design documents:

```powershell
# Read component design doc
cat components\<component>\doc\index.md
```

Look for requirement IDs:

```markdown
## Requirements

### SWDD_LED-100: LED Activation
The LED shall activate within 10ms of button press.

### SWDD_LED-101: LED Deactivation  
The LED shall deactivate within 10ms of button release.

### SWDD_LED-200: Brightness Control
The LED brightness shall be adjustable from 0-100%.
```

### Linking Single Requirement

```cpp
/*!
 * @rst
 * .. test:: LED.TurnsOn_When_ButtonPressed
 *    :id: TS_LED-001
 *    :tests: SWDD_LED-100
 * 
 * Validates LED activation timing requirement.
 * @endrst
 */
```

### Linking Multiple Requirements

Use comma-separated list (no spaces after commas):

```cpp
/*!
 * @rst
 * .. test:: LED.RespondsTo_ButtonEvents
 *    :id: TS_LED-010
 *    :tests: SWDD_LED-100,SWDD_LED-101
 * 
 * Validates both activation and deactivation requirements.
 * @endrst
 */
```

### Many-to-Many Relationships

- **One test → multiple requirements**: Test validates several requirements
- **One requirement → multiple tests**: Requirement needs several test scenarios

Example: One requirement, multiple tests:

```cpp
// SWDD_BTN-200: Debouncing requirement

/*!
 * @rst
 * .. test:: Button.IgnoresShortPulses_LessThan50ms
 *    :id: TS_BTN-002
 *    :tests: SWDD_BTN-200
 * 
 * Debounce prevents spurious triggers (lower boundary).
 * @endrst
 */
TEST(Button, IgnoresShortPulses_LessThan50ms) { /* ... */ }

/*!
 * @rst
 * .. test:: Button.AcceptsLongPulses_GreaterThan50ms
 *    :id: TS_BTN-003
 *    :tests: SWDD_BTN-200
 * 
 * Debounce accepts valid presses (upper boundary).
 * @endrst
 */
TEST(Button, AcceptsLongPulses_GreaterThan50ms) { /* ... */ }

/*!
 * @rst
 * .. test:: Button.HandlesRapidToggling
 *    :id: TS_BTN-004
 *    :tests: SWDD_BTN-200
 * 
 * Debounce handles noisy input (stress test).
 * @endrst
 */
TEST(Button, HandlesRapidToggling) { /* ... */ }
```

All three tests validate `SWDD_BTN-200` from different angles.

## Description Guidelines

### Good Descriptions

Clear, concise, explains what behavior is validated:

```cpp
/*!
 * @rst
 * .. test:: Timer.FiresCallback_After_ConfiguredDelay
 *    :id: TS_TMR-015
 *    :tests: SWDD_TMR-100
 * 
 * Timer callback executes exactly once after configured delay expires.
 * @endrst
 */
```

### Bad Descriptions

Too vague or implementation-focused:

```cpp
// Too vague
/*!
 * @rst
 * .. test:: Timer.Works
 *    :id: TS_TMR-015
 *    :tests: SWDD_TMR-100
 * 
 * Timer works correctly.
 * @endrst
 */

// Too implementation-focused
/*!
 * @rst
 * .. test:: Timer.IncrementsCounterAndChecksThreshold
 *    :id: TS_TMR-015
 *    :tests: SWDD_TMR-100
 * 
 * Test increments internal counter variable and checks if it exceeds threshold.
 * @endrst
 */
```

### Description Best Practices

1. **Focus on behavior**: What the component does, not how
2. **Be specific**: Mention key values/conditions
3. **Keep brief**: One or two sentences
4. **Use active voice**: "Timer fires callback" not "Callback is fired"
5. **Match test name**: Description expands on test name

## Traceability Reports

After building tests, generate traceability report:

```powershell
.\build.ps1 -build -buildKit test -variants Disco -target reports
```

Report shows:
- **Test → Requirement mapping**: Which tests validate which requirements
- **Requirement coverage**: Which requirements have tests
- **Uncovered requirements**: Requirements without tests
- **Test results**: Pass/fail status

Open report with VS Code task: "Open component test report"

### Example Report Output

```
Requirement Coverage Report
==========================

SWDD_LED-100: LED Activation [COVERED]
  ✓ TS_LED-001: LED.TurnsOn_When_ButtonPressed

SWDD_LED-101: LED Deactivation [COVERED]
  ✓ TS_LED-002: LED.TurnsOff_When_ButtonReleased

SWDD_LED-200: Brightness Control [PARTIALLY COVERED]
  ✓ TS_LED-020: LED.SetsBrightness_ValidRange
  ⚠ Missing: Boundary value tests

SWDD_LED-300: Color Temperature [UNCOVERED]
  ✗ No tests found

Coverage: 75% (3/4 requirements covered)
```

## Common Mistakes

### 1. Mismatched Test Names

```cpp
// WRONG: Test name doesn't match RST
/*!
 * @rst
 * .. test:: LED.TurnsOn
 *    :id: TS_LED-001
 *    :tests: SWDD_LED-100
 * @endrst
 */
TEST(LED, ActivatesOnButtonPress)  // Name mismatch!
{
    // ...
}

// CORRECT: Names match
/*!
 * @rst
 * .. test:: LED.ActivatesOnButtonPress
 *    :id: TS_LED-001
 *    :tests: SWDD_LED-100
 * @endrst
 */
TEST(LED, ActivatesOnButtonPress)
{
    // ...
}
```

### 2. Duplicate Test IDs

```cpp
// WRONG: Same ID used twice
TEST(LED, Test1) { /* :id: TS_LED-001 */ }
TEST(LED, Test2) { /* :id: TS_LED-001 */ }  // Duplicate!

// CORRECT: Sequential IDs
TEST(LED, Test1) { /* :id: TS_LED-001 */ }
TEST(LED, Test2) { /* :id: TS_LED-002 */ }
```

### 3. Invalid Requirement Format

```cpp
// WRONG: Various format errors
:tests: SWDD-LED-100      // Hyphen in component
:tests: LED-100           // Missing prefix
:tests: SWDD_LED_100      // Underscore instead of hyphen
:tests: SWDD_LED-100,     // Trailing comma

// CORRECT:
:tests: SWDD_LED-100
:tests: SWDD_LED-100,SWDD_LED-101
```

### 4. Missing RST Block

```cpp
// WRONG: No traceability
TEST(LED, ImportantTest)
{
    // No RST block - test not traceable!
}

// CORRECT: Always include RST
/*!
 * @rst
 * .. test:: LED.ImportantTest
 *    :id: TS_LED-050
 *    :tests: SWDD_LED-500
 * 
 * Validates critical LED behavior.
 * @endrst
 */
TEST(LED, ImportantTest)
{
    // ...
}
```

### 5. Invented Requirement or Test IDs

Never fabricate a `:tests:` requirement ID or a `:id:` test ID. An ID that does not exist in the
spec files silently breaks the traceability tooling — the mapping looks complete but points at
nothing.

```cpp
// WRONG: guessed the requirement ID because it "looked about right"
:tests: SWDD_LED-999      // no such requirement in doc/index.md

// CORRECT: grep the spec first, use only IDs that actually exist
//   rg "SWDD_LED-" components/led/doc/index.md
:tests: SWDD_LED-100
```

Requirement IDs live in `components/<name>/doc/index.md` (and any linked software/unit
specification). Search for the ID before writing it.

### 6. Paraphrased Requirement Text in Comments

When you copy requirement text into a traceability comment, copy it **verbatim** from the source.
A paraphrase drifts from the requirement and misleads the next reader into trusting a summary that
may no longer match the spec.

```cpp
// CORRECT — verbatim from the component design doc (doc/index.md, SWDD_PSP-002)
/* traceability: SWDD_PSP-002 - If the retrieved power state is POWER_STATE_OFF, the
   function shall set the power state to POWER_STATE_ON. */

// WRONG — paraphrased interpretation
/* traceability: SWDD_PSP-002 - turns power on when it was off */
```

## Workflow Integration

### 1. Create Test with Traceability

```cpp
/*!
 * @rst
 * .. test:: MyComponent.NewBehavior
 *    :id: TS_MYCOMP-???  // Fill in next available ID
 *    :tests: SWDD_MYCOMP-???  // Find requirement ID
 * 
 * Description here.
 * @endrst
 */
TEST(MyComponent, NewBehavior)
{
    // Implementation
}
```

### 2. Find Next Test ID

```powershell
# Search existing test IDs
rg "TS_MYCOMP-" components\mycomponent\test\

# Output shows existing IDs:
# TS_MYCOMP-001
# TS_MYCOMP-002
# TS_MYCOMP-003

# Use next sequential: TS_MYCOMP-004
```

### 3. Find Requirement ID

```powershell
# Read design doc
cat components\mycomponent\doc\index.md

# Search for relevant requirement
# Copy requirement ID (e.g., SWDD_MYCOMP-200)
```

### 4. Complete RST Block

```cpp
/*!
 * @rst
 * .. test:: MyComponent.NewBehavior
 *    :id: TS_MYCOMP-004
 *    :tests: SWDD_MYCOMP-200
 * 
 * Component responds correctly to new input condition.
 * @endrst
 */
TEST(MyComponent, NewBehavior)
{
    CREATE_MOCK(mymock);
    
    // ARRANGE
    // ACT
    // ASSERT
}
```

### 5. Verify Traceability

```powershell
# Build tests
.\build.ps1 -build -buildKit test -buildType Debug -variants Disco -target components_mycomponent_unittests

# Generate reports
.\build.ps1 -build -buildKit test -buildType Debug -variants Disco -target reports

# Open report (VS Code task: "Open component test report")
# Verify:
# - Test appears in report
# - Requirement link is correct
# - Test passes
```

## Template Reference

### Complete Test Template with Traceability

```cpp
#include <gtest/gtest.h>

extern "C"
{
#include "autoconf.h"
#include "<component>.h"
}

#include "mockup_components_<component>.h"

/*!
 * @rst
 * .. test:: <Component>.<DescriptiveTestName>
 *    :id: TS_<COMP>-###
 *    :tests: SWDD_<COMP>-###
 * 
 * Brief description of what this test validates.
 * @endrst
 */
TEST(<Component>, <DescriptiveTestName>)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    EXPECT_CALL(mymock, Setup()).WillOnce(Return(OK));

    // ACT
    Component_Function();
}
```
