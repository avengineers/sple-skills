# Variant-Based Integration Testing Reference

## Variant Impact on Integration Tests

Integration tests are more sensitive to variant configuration than unit tests because:

1. **Component availability**: Not all components exist in all variants
2. **Feature interactions**: Different features may interact differently
3. **Subsystem composition**: Variants may have different subsystem structures
4. **Integration points**: RTE interfaces may vary by variant

## Variant Configuration Examples

### Disco Variant
- **Components**: `light_controller`, `main_control_knob`, `power_button`, `power_signal_processing`
- **Features**: `CONFIG_BLINKING=y`, `CONFIG_LIGHT_INTENSITY_LEVELS=5`
- **Integration points**: Knob → Light Controller → LED Driver

### Spa Variant
- **Components**: `light_controller`, `main_control_knob`, `power_button`, `auto_off_timer`, `power_signal_processing`
- **Features**: `CONFIG_AUTO_OFF=y`, `CONFIG_TIMER_DURATION=300`, `CONFIG_LIGHT_INTENSITY_LEVELS=10`
- **Integration points**: Timer → Light Controller + Manual Controls

### Base Variant
- **Components**: `light_controller`, `power_button`, `power_signal_processing`
- **Features**: `CONFIG_LIGHT_INTENSITY_LEVELS=3`
- **Integration points**: Simple on/off control

## Variant Integration Test Strategies

### Strategy 1: Common Integration Tests

Tests that run on ALL variants with conditional behavior:

```cpp
/*!
 * @rst
 * .. test:: CommonIntegration.PowerOnSequence
 *    :id: IT_COMMON-001
 *    :tests: SRS_POWER-001
 * @endrst
 */
TEST_F(PowerIntegrationTest, PowerOnSequence)
{
    // GIVEN: System powered off
    PowerSystem_Initialize();
    
    // WHEN: Power button pressed
    PowerButton_Press();
    
    // THEN: Core components power on (all variants)
    EXPECT_EQ(STATE_ON, LightController_GetState());
    EXPECT_EQ(STATE_ON, PowerButton_GetState());
    
#ifdef CONFIG_AUTO_OFF
    // Additional behavior in Spa variant
    EXPECT_EQ(STATE_ARMED, AutoOffTimer_GetState());
#endif
    
#ifdef CONFIG_BLINKING
    // Additional behavior in Disco variant  
    EXPECT_EQ(BLINK_MODE_STARTUP, LightController_GetBlinkMode());
#endif
}
```

### Strategy 2: Variant-Conditional Integration Tests

Tests that only run when specific features are enabled:

```cpp
#ifdef CONFIG_AUTO_OFF
/*!
 * @rst
 * .. test:: SpaIntegration.AutoOffTimerIntegration
 *    :id: IT_SPA-001
 *    :tests: SRS_AUTO_OFF-001
 * @endrst
 */
TEST_F(SpaIntegrationTest, AutoOffTimerIntegration)
{
    // GIVEN: Spa variant with auto-off enabled
    LightController_TurnOn();
    AutoOffTimer_Start(CONFIG_TIMER_DURATION);
    
    // WHEN: Timer expires
    SimulateTimeAdvance(CONFIG_TIMER_DURATION + 1);
    AutoOffTimer_Process();
    
    // THEN: Light automatically turns off
    EXPECT_EQ(STATE_OFF, LightController_GetState());
    EXPECT_EQ(TIMER_STATE_EXPIRED, AutoOffTimer_GetState());
}
#endif // CONFIG_AUTO_OFF

#ifdef CONFIG_BLINKING
/*!
 * @rst
 * .. test:: DiscoIntegration.BlinkingLightPattern
 *    :id: IT_DISCO-001  
 *    :tests: SRS_BLINK-001
 * @endrst
 */
TEST_F(DiscoIntegrationTest, BlinkingLightPattern)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Disco variant with blinking enabled
    LightController_SetBlinkMode(BLINK_MODE_PARTY);
    
    // WHEN: Blink sequence executes
    for (int cycle = 0; cycle < 5; cycle++) {
        LightController_Process();
        SimulateTimeAdvance(BLINK_PERIOD_MS);
    }
    
    // THEN: PWM output follows blink pattern
    EXPECT_CALL(hal_mock, HAL_PWM_SetDutyCycle(_, _))
        .Times(AtLeast(5));  // Multiple duty cycle changes
}
#endif // CONFIG_BLINKING
```

### Strategy 3: Variant-Specific Test Files

Separate test files for each variant:

**File: `test/Disco/disco_integration_test.cpp`**

```cpp
// Tests specific to Disco variant only
#if defined(VARIANT_DISCO) && defined(CONFIG_BLINKING)

class DiscoIntegrationTest : public Test
{
protected:
    void SetUp() override {
        // Initialize Disco-specific components
        LightController_Init();
        MainControlKnob_Init(); 
        PowerButton_Init();
        BlinkController_Init();  // Disco-specific
    }
};

TEST_F(DiscoIntegrationTest, KnobControlsBlinkSpeed)
{
    // Disco-specific integration test
    // Tests knob → blink controller → light controller
}

#endif // VARIANT_DISCO
```

## Variant Build Configuration

### CMake Variant Detection

```cmake
# Determine which integration tests to build based on variant
if(VARIANT_DISCO)
    set(VARIANT_INTEGRATION_TESTS
        disco_light_integration_test
        disco_blink_integration_test
    )
elseif(VARIANT_SPA) 
    set(VARIANT_INTEGRATION_TESTS
        spa_light_integration_test
        spa_timer_integration_test
    )
elseif(VARIANT_BASE)
    set(VARIANT_INTEGRATION_TESTS
        base_light_integration_test
    )
endif()

# Common integration tests (all variants)
set(COMMON_INTEGRATION_TESTS
    power_integration_test
    basic_light_integration_test
)

# Build all applicable tests
foreach(test_name IN LISTS COMMON_INTEGRATION_TESTS VARIANT_INTEGRATION_TESTS)
    add_executable(${test_name} src/${test_name}.cpp)
    target_link_libraries(${test_name} PRIVATE variant_components gtest_main)
    gtest_discover_tests(${test_name})
endforeach()
```

### Python Variant Orchestration

```python
class VariantIntegrationTestSuite:
    def __init__(self):
        self.variants = {
            "Disco": {
                "features": ["CONFIG_BLINKING", "CONFIG_LIGHT_INTENSITY_LEVELS=5"],
                "components": ["light_controller", "blink_controller", "knob"],
                "tests": ["disco_light_integration", "disco_blink_integration"]
            },
            "Spa": {
                "features": ["CONFIG_AUTO_OFF", "CONFIG_TIMER_DURATION=300"],
                "components": ["light_controller", "auto_off_timer", "knob"], 
                "tests": ["spa_light_integration", "spa_timer_integration"]
            },
            "Base": {
                "features": ["CONFIG_LIGHT_INTENSITY_LEVELS=3"],
                "components": ["light_controller"],
                "tests": ["base_light_integration"]
            }
        }
    
    def run_variant_tests(self, variant_name):
        """Run integration tests for specific variant."""
        if variant_name not in self.variants:
            raise ValueError(f"Unknown variant: {variant_name}")
        
        config = self.variants[variant_name]
        
        # Build variant
        build_cmd = [
            "powershell", "./build.ps1", "-build", "-buildKit", "test",
            "-variants", variant_name
        ]
        subprocess.run(build_cmd, check=True)
        
        # Run variant-specific integration tests
        results = {}
        for test in config["tests"]:
            print(f"Running {test} for {variant_name}...")
            test_cmd = [f"./build/test_{variant_name}/{test}"]
            result = subprocess.run(test_cmd, capture_output=True, text=True)
            results[test] = result.returncode == 0
        
        return all(results.values())
```

## Debugging Variant Integration Issues

### Issue: Integration Test Fails in One Variant Only

**Symptoms**: Test passes in Disco, fails in Spa
**Diagnosis Steps**:

1. **Check component availability**:
   ```bash
   grep -r "ComponentName" build/Spa/generated/
   ```

2. **Verify feature flags**:
   ```cpp
   #ifndef CONFIG_REQUIRED_FEATURE
   GTEST_SKIP() << "Feature not available in this variant";
   #endif
   ```

3. **Check variant-specific initialization**:
   ```cpp
   void SetUp() override {
   #ifdef VARIANT_SPA
       AutoOffTimer_Init();  // Spa-specific component
   #endif
       CommonComponent_Init();  // All variants
   }
   ```

### Issue: Missing Component in Variant

**Symptoms**: Linker error - undefined reference to component function
**Solution**: Add variant guards

```cpp
#ifdef HAS_COMPONENT_X
   ComponentX_Function();
#else
   // Alternative behavior or skip test
   GTEST_SKIP() << "ComponentX not available in this variant";
#endif
```

## Continuous Integration for Variants

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Variant Integration Tests') {
            parallel {
                stage('Disco') {
                    steps {
                        powershell './build.ps1 -build -buildKit test -variants Disco'
                        publishTestResults 'build/Disco/test_results/*.xml'
                    }
                }
                stage('Spa') {
                    steps {
                        powershell './build.ps1 -build -buildKit test -variants Spa'
                        publishTestResults 'build/Spa/test_results/*.xml'
                    }
                }
                stage('Base') {
                    steps {
                        powershell './build.ps1 -build -buildKit test -variants Base'
                        publishTestResults 'build/Base/test_results/*.xml'
                    }
                }
            }
        }
    }
}
```

## Best Practices for Variant Integration Testing

1. **Start with Common Tests**: Write tests that work across all variants first
2. **Use Feature Flags Wisely**: Guard variant-specific code with appropriate `#ifdef`s
3. **Test Variant Transitions**: If components can be enabled/disabled at runtime
4. **Validate Configuration**: Ensure test setup matches variant's actual configuration
5. **Separate Concerns**: Keep variant-specific tests in separate files when possible
6. **Document Variant Behavior**: Use RST comments to explain variant differences
7. **Test Edge Cases**: Focus on interactions that vary between variants