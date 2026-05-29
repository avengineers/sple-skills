---
name: c-integration-testing
description: Guide for writing BDD-style integration tests for embedded C components using GTest. Use when (1) Testing multiple components together, (2) Verifying component interactions and interfaces, (3) Testing data flow between components, (4) Validating component coordination, (5) Testing subsystems end-to-end, (6) Writing integration test scenarios in BDD/Gherkin notation. Focuses on testing real component interactions without mocking to verify system integration.
---

# Integration Testing for Embedded C

Test multiple components working together using real implementations. Mock only HAL/hardware.

```text
Unit Test:           Integration Test:
[Component A]        [Component A] <-> [Component B]
      |                     |              |  
  [Mocks]            [Component C] <-> [HAL (mocked)]
```

> **COMPANION SKILL**: For isolated single-component testing with full mocking, use the `c-unit-testing` skill.

## Quick Start

> **BUILD**: Invoke the `build-execution` skill to build and run integration tests.
> Provide: buildKit=test, buildType=Debug, variants=\<Name\>, target=integration\_\<subsystem\>\_test

For direct build commands without the helper skill, see [references/build-scripts.md](references/build-scripts.md).

### Basic Template

```cpp
#include <gtest/gtest.h>
extern "C" {
    #include "autoconf.h"
    #include "<component_a>.h"
    #include "<component_b>.h" 
}
#include "mockup_hal.h"  // Mock only HAL layer

class SubsystemIntegrationTest : public Test
{
protected:
    void SetUp() override {
        ComponentA_Init();
        ComponentB_Init();
    }
};

/*!
 * @rst
 * .. test:: SubsystemIntegration.DataFlowScenario
 *    :id: IT_SUBSYS-001
 *    :tests: SRS_SUBSYS-100
 * @endrst
 */
TEST_F(SubsystemIntegrationTest, DataFlowScenario)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: System in known state
    EXPECT_CALL(hal_mock, HAL_GPIO_Read(SENSOR_PIN))
        .WillOnce(Return(HIGH));
    
    // WHEN: Stimulus applied
    ComponentA_ProcessInput();
    
    // THEN: Expected behavior occurs
    ComponentB_Process();
    EXPECT_CALL(hal_mock, HAL_GPIO_Write(OUTPUT_PIN, HIGH));
}
```

## Mock Strategy

**Rule: Mock only HAL/hardware — never application components.**

```cpp
// ✓ DO: Mock hardware abstraction layer
CREATE_MOCK(hal_mock);
EXPECT_CALL(hal_mock, HAL_GPIO_Read(PIN)).WillOnce(Return(HIGH));

// ✗ DON'T: Mock application components  
// MockComponentB mock_b;  // Defeats integration testing purpose
```

For external dependencies (network, filesystem), mock selectively alongside HAL.

## Traceability

Integration tests trace to **System Requirements Specification (SRS)**, not SWDD:

```cpp
/*!
 * @rst
 * .. test:: SubsystemIntegration.DataFlowScenario
 *    :id: IT_SUBSYS-001
 *    :tests: SRS_SUBSYS-100
 * @endrst
 */
```

## Variant-Based Testing

Tests must handle multiple product variants with different component combinations:

| Variant | Components | Key Features |
|---------|-----------|--------------|
| Disco | `light_controller`, `blink_controller`, `main_control_knob` | `CONFIG_BLINKING` |
| Spa | `light_controller`, `auto_off_timer`, `main_control_knob` | `CONFIG_AUTO_OFF` |
| Base | `light_controller`, `power_button` | minimal |

Use `#ifdef CONFIG_*` guards for variant-conditional tests. See [references/variant-testing.md](references/variant-testing.md) for full strategies.

## Test Organization

```text
test/
├── integration/
│   ├── subsystem_a_integration_test.cpp
│   ├── subsystem_b_integration_test.cpp
│   └── end_to_end_integration_test.cpp
└── <variant>/
    └── variant_specific_integration.py
```

### CMake Registration

```cmake
add_executable(integration_subsystem_test
    src/integration_subsystem_test.cpp
    ${COMPONENT_SOURCES}
)
target_link_libraries(integration_subsystem_test
    PRIVATE gtest_main gmock component_libs mockup_hal
)
gtest_discover_tests(integration_subsystem_test
    TEST_PREFIX "Integration."
)
```

## Best Practices

- **Use real timing** via `SystemTick_Process()` loops instead of mocked timers where possible
- **Use setup helpers** for multi-component initialization sequences
- **One scenario per test** — avoid testing multiple integration paths in a single test

## Quick Checklist

- [ ] Unit tests exist for all components involved
- [ ] Only HAL/external interfaces are mocked
- [ ] Test uses BDD structure (Given-When-Then)
- [ ] Test has RST traceability to SRS

See [references/checklist.md](references/checklist.md) for comprehensive checklists.

## References

- [references/templates.md](references/templates.md) — Code templates for each integration pattern
- [references/integration-patterns.md](references/integration-patterns.md) — Pipeline, Fan-Out, Fan-In, Feedback Loop patterns
- [references/subsystem-testing.md](references/subsystem-testing.md) — Subsystem boundary testing strategies
- [references/variant-testing.md](references/variant-testing.md) — Variant-specific test strategies and CMake setup
- [references/build-scripts.md](references/build-scripts.md) — Build commands and Python orchestration scripts
- [references/checklist.md](references/checklist.md) — Development and review checklists

## Coverage Analysis

After running integration tests, analyze coverage to verify that component interactions are adequately exercised.

**READ**: [Coverage Analysis](../shared/test-reports/coverage-analysis.md) — Report locations, coverage.json extraction, junit.xml parsing, output format template, and variant mapping.

## Committing Integration Tests

> **COMMIT REQUIREMENT**: When committing new integration tests, invoke the `conventional-commits` skill
> to ensure proper commit message formatting (use `test:` type for test-only changes).

> **PROJECT MEMORY**: When discovering integration issues or defining subsystem contracts,
> use the `project-knowledge-base` skill to document them:
> - **Integration bugs found** → `doc/project_notes/bugs.md`
> - **Subsystem interface decisions** → `doc/project_notes/decisions.md`
