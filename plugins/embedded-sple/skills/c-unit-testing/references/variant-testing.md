# Variant-Based Testing Guide

SPLED is a **Software Product Line** with multiple product variants. Each variant has different features enabled via KConfig, requiring variant-aware testing strategies.

## Table of Contents

| Section | Line | When to read |
|---------|------|--------------|
| [Understanding Variants](#understanding-variants) | ~20 | Variant concepts and differences |
| [C++ Unit Tests (GTest)](#c-unit-tests-gtest) | ~35 | Building and running unit tests per variant |
| [Python Integration Tests (Pytest)](#python-integration-tests-pytest) | ~107 | Variant-level pytest integration |
| [Variant Testing Workflow](#variant-testing-workflow) | ~204 | End-to-end workflow |
| [Variant-Specific Test Considerations](#variant-specific-test-considerations) | ~262 | Feature guards, component availability |
| [Continuous Integration](#continuous-integration) | ~306 | Jenkins CI parallel testing |
| [Viewing Test Reports](#viewing-test-reports) | ~326 | HTML reports for results/coverage |
| [Best Practices](#best-practices) | ~343 | Variant-agnostic testing guidelines |

## Understanding Variants

Each variant represents a distinct product configuration:

- **Disco**: Interactive light effects with knob control
- **Spa**: Relaxation-focused lighting
- **Sleep**: Sleep timer functionality
- **Base/Dev**: Development baseline
- **IDEA/Sloemada**: Customer-specific variants

Variants differ in:
- **Features**: Which components/capabilities are enabled (via `config.txt`)
- **Components**: Which source files are compiled (via `parts.cmake`)
- **Configuration**: Variant-specific settings (via `config.cmake`)

## C++ Unit Tests (GTest)

Component-level unit tests are **variant-agnostic** - they test component logic independent of variant configuration.

### Building Unit Tests

```powershell
# Build unit tests for a specific variant
.\build.ps1 -build -buildKit test -buildType Debug -variants Disco

# Build unit tests for specific component
.\build.ps1 -build -buildKit test -buildType Debug -variants Disco -target components_spled_unittests

# Run all unit tests for a variant
.\build.ps1 -build -buildKit test -buildType Debug -variants Disco -target unittests
```

### Why Specify Variant?

Even though unit tests are component-focused, variant selection matters for:

1. **Build context**: CMake needs variant configuration to resolve dependencies
2. **Feature guards**: Tests may check `#ifdef CONFIG_FEATURE` behavior
3. **Mock generation**: Auto-generated mocks depend on variant's component selection

### Feature-Conditional Testing

Test variant-specific features using KConfig guards:

```cpp
TEST(SPLED, FeatureConditionalBehavior)
{
    CREATE_MOCK(mymock);

#ifdef CONFIG_AUTO_OFF
    // ARRANGE: Auto-off feature is enabled in this variant
    EXPECT_CALL(mymock, Timer_Start(AUTO_OFF_TIMEOUT_MS))
        .Times(1);

    // ACT
    SPLED_Init();
#else
    // ARRANGE: Auto-off feature disabled in this variant
    EXPECT_CALL(mymock, Timer_Start(_))
        .Times(0);

    SPLED_Init();
#endif
}
```

### Component-Specific Unit Tests

Each component's unit tests live in `components/<name>/test/`:

```
components/
  spled/
    src/
      spled.c
    test/
      test_spled.cc        # C++ GTest unit tests
    CMakeLists.txt         # Includes spl_add_test_source()
```

Tests are registered via CMake:

```cmake
# In components/spled/CMakeLists.txt
spl_add_test_source(test/test_spled.cc)
```

## Python Integration Tests (Pytest)

Python tests in `test/<VariantName>/` verify **variant-level integration** using the SplBuild helper.

### Test Structure

```python
# test/Disco/test_Disco.py
from spl_core.test_utils.spl_build import SplBuild
import pytest

class Test_Disco:
    variant: str = "Disco"
    components: list[str] = [
        "components/light_controller",
        "components/main_control_knob",
    ]
    
    @pytest.mark.unittests
    def test_unittests(self):
        """Run all component unit tests for this variant."""
        spl_build = SplBuild(
            variant=self.variant,
            build_kit="test",
            build_type="Debug",
            target="unittests",
        )
        result = spl_build.execute()
        assert result == 0, "Unit tests failed"
    
    @pytest.mark.reports
    def test_reports(self):
        """Generate and validate test reports."""
        spl_build = SplBuild(
            variant=self.variant,
            build_kit="test",
            build_type="Debug",
            target="reports",
        )
        result = spl_build.execute()
        assert result == 0, "Report generation failed"
```

### Running Variant Tests

```powershell
# Run all tests for all variants
.\build.ps1 -selftests

# Run tests for specific variant
.\build.ps1 -selftests -filter "Disco"

# Run specific test type (using pytest markers)
.\build.ps1 -selftests -marker "unittests"
.\build.ps1 -selftests -marker "reports"
.\build.ps1 -selftests -marker "build_debug"
```

### Pytest Markers

Markers categorize tests (defined in `pytest.ini`):

- **unittests**: Component unit test execution
- **reports**: Test report generation (traceability, coverage)
- **build_debug**: Debug build verification
- **build_release**: Release build verification
- **static_analysis**: Static code analysis (Polyspace)
- **quality_gates**: PR validation checks

Example: Run only unit tests for Disco:

```powershell
.\build.ps1 -selftests -filter "Disco" -marker "unittests"
```

### SplBuild Helper Usage

The `SplBuild` class wraps `build.ps1` for test automation:

```python
from spl_core.test_utils.spl_build import SplBuild

# Build variant production code
spl_build = SplBuild(
    variant="Disco",
    build_kit="prod",
    build_type="Release",
    target="all",
)
result = spl_build.execute()
assert result == 0

# Get build artifacts for archiving
artifacts = spl_build.get_variant_artifacts()
# Returns: [build/Disco/prod/Release/kconfig/autoconf.h, ...]
```

## Variant Testing Workflow

### 1. Develop Component with Unit Tests

Write C++ GTest unit tests in `components/<name>/test/`:

```cpp
// components/my_component/test/test_my_component.cc
TEST(MyComponent, DoesCorrectly)
{
    CREATE_MOCK(mymock);
    // Test component logic
}
```

Register in `CMakeLists.txt`:

```cmake
spl_add_test_source(test/test_my_component.cc)
```

### 2. Test Component Locally

```powershell
# Build and run component unit tests
.\build.ps1 -build -buildKit test -buildType Debug -variants Disco -target components_my_component_unittests
```

### 3. Integrate into Variant Pytest

Ensure variant's Python test executes unit tests:

```python
# test/Disco/test_Disco.py
@pytest.mark.unittests
def test_unittests(self):
    spl_build = SplBuild(
        variant=self.variant,
        build_kit="test",
        build_type="Debug",
        target="unittests",  # Runs ALL component unit tests
    )
    result = spl_build.execute()
    assert result == 0
```

### 4. Verify Across Variants

Test component in all variants that include it:

```powershell
# Test all variants
.\build.ps1 -selftests -marker "unittests"

# Test specific variants
.\build.ps1 -selftests -filter "Disco|Spa" -marker "unittests"
```

## Variant-Specific Test Considerations

### Feature Availability

Component behavior may differ based on variant features:

```cpp
TEST(LightController, BlinksWhenEnabled)
{
    CREATE_MOCK(mymock);

#ifdef CONFIG_BLINKING
    // ARRANGE
    EXPECT_CALL(mymock, Timer_Start(_)).Times(1);

    // ACT
    LightController_SetMode(MODE_BLINK);
#else
    // Feature disabled - skip test
    GTEST_SKIP() << "CONFIG_BLINKING not enabled in this variant";
#endif
}
```

### Component Availability

Some components exist only in specific variants:

```cmake
# In variant's parts.cmake
if(AUTO_OFF STREQUAL "True")
    spl_add_component(components/auto_off)
endif()
```

Tests for such components automatically skip in variants without them.

### Dependency Resolution

Mock generation adapts to variant's component selection:

- **Variant A**: Includes `auto_off` component → mocks generated for its dependencies
- **Variant B**: Excludes `auto_off` → no mocks for `auto_off` dependencies

## Continuous Integration

Jenkins CI runs variant tests in parallel:

```groovy
// Jenkinsfile (simplified)
variants.each { variant ->
    stage("Test ${variant}") {
        steps {
            sh """
                ./build.ps1 -selftests -filter "${variant}" -marker "unittests"
                ./build.ps1 -selftests -filter "${variant}" -marker "reports"
            """
        }
    }
}
```

Each variant is tested independently to catch variant-specific issues.

## Viewing Test Reports

After running tests:

```powershell
# Open variant test report (HTML)
# VS Code Task: "Open variant test report"

# Open coverage report
# VS Code Task: "Open variant coverage report"
```

Reports show:
- **Test results**: Pass/fail status for all tests
- **Coverage**: Line/branch coverage per component
- **Traceability**: Test-to-requirement links

## Best Practices

1. **Write variant-agnostic tests**: Test component logic, not variant configuration
2. **Use feature guards**: Conditionally test variant-specific features with `#ifdef`
3. **Test in representative variant**: Choose variant with maximum feature set for comprehensive testing
4. **Run full variant suite before PR**: `.\build.ps1 -selftests` ensures all variants pass
5. **Check reports**: Review coverage and traceability in generated reports
