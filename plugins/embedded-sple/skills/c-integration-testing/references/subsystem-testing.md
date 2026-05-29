# Subsystem Testing Strategies

## Subsystem Definition

A **subsystem** is a cohesive group of related components that together provide a specific system capability.

Examples:
- **Lighting Subsystem**: Sensor + Dimmer Logic + PWM Controller + LED Driver
- **Communication Subsystem**: Protocol Handler + Buffer Manager + UART Driver
- **Power Management**: Battery Monitor + Voltage Regulator + Power Sequencer
- **User Interface**: Button Handler + Display Controller + Menu Manager

## Subsystem Testing Approach

### 1. Identify Subsystem Boundaries

Define clear boundaries for the subsystem under test:

```
┌─────────────────────────────────────────────┐
│        LIGHTING SUBSYSTEM                    │
│                                              │
│  ┌──────────┐  ┌─────────┐  ┌────────────┐ │
│  │ Light    │→ │ Dimmer  │→ │ PWM        │ │
│  │ Sensor   │  │ Logic   │  │ Controller │ │
│  └──────────┘  └─────────┘  └────────────┘ │
│       ↓             ↓              ↓         │
└───────┼─────────────┼──────────────┼─────────┘
        │             │              │
    [HAL_ADC]    [Calculation]   [HAL_PWM]
    (mocked)      (real)         (mocked)
```

**Test Strategy**:
- Mock external interfaces (HAL)
- Use real implementations within subsystem
- Test subsystem as a complete unit

### 2. Subsystem Test Structure

```cpp
class LightingSubsystemTest : public Test
{
protected:
    // Subsystem components
    void SetUp() override
    {
        CREATE_MOCK(hal_mock);
        
        // Initialize all subsystem components
        LightSensor_Init();
        DimmerLogic_Init();
        PWMController_Init();
        LEDDriver_Init();
        
        // Set up default HAL behaviors
        SetupDefaultHALBehaviors();
    }
    
    void TearDown() override
    {
        // Cleanup subsystem
        LEDDriver_Deinit();
        PWMController_Deinit();
        DimmerLogic_Deinit();
        LightSensor_Deinit();
    }
    
    // Helper methods for subsystem-level operations
    void RunSubsystemCycle()
    {
        LightSensor_Update();
        DimmerLogic_Calculate();
        PWMController_Update();
        LEDDriver_Process();
    }
    
    void SimulateAmbientLight(uint16_t lux)
    {
        uint16_t adc_value = ConvertLuxToADC(lux);
        EXPECT_CALL(hal_mock, ADC_Read(LIGHT_SENSOR_CH))
            .WillOnce(Return(adc_value));
    }
    
private:
    void SetupDefaultHALBehaviors()
    {
        ON_CALL(hal_mock, GetSystemTick())
            .WillByDefault(Return(0));
    }
    
    uint16_t ConvertLuxToADC(uint16_t lux)
    {
        // Simplified conversion
        return lux * 4;
    }
};
```

### 3. End-to-End Subsystem Scenarios

Test complete workflows through the subsystem:

```cpp
/*!
 * @rst
 * .. test:: LightingSubsystem.AutoDimming_DarkToBright
 *    :id: IT_LIGHT-001
 *    :tests: SRS_LIGHT-100
 * 
 * Complete auto-dimming flow from dark to bright ambient conditions.
 * @endrst
 */
TEST_F(LightingSubsystemTest, AutoDimming_DarkToBright)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Very dark environment (10 lux)
    SimulateAmbientLight(10);
    
    // WHEN: Subsystem processes one cycle
    RunSubsystemCycle();
    
    // THEN: LED at maximum brightness
    uint8_t brightness = PWMController_GetDutyCycle();
    EXPECT_GE(brightness, 90);  // ≥90% in dark
    
    EXPECT_CALL(hal_mock, PWM_SetDutyCycle(LED_PWM_CH, brightness))
        .Times(1);
    
    // WHEN: Ambient light increases to bright (500 lux)
    SimulateAmbientLight(500);
    RunSubsystemCycle();
    
    // THEN: LED brightness reduced
    brightness = PWMController_GetDutyCycle();
    EXPECT_LE(brightness, 30);  // ≤30% in bright light
    
    EXPECT_CALL(hal_mock, PWM_SetDutyCycle(LED_PWM_CH, brightness))
        .Times(1);
}
```

## Subsystem Testing Patterns

### Pattern 1: Nominal Operation

Test the happy path through the subsystem:

```cpp
/*!
 * @rst
 * .. test:: CommunicationSubsystem.SendsMessageSuccessfully
 *    :id: IT_COMM-002
 *    :tests: SRS_COMM-200
 * 
 * Complete message transmission through communication stack.
 * @endrst
 */
TEST_F(CommunicationSubsystemTest, SendsMessageSuccessfully)
{
    CREATE_MOCK(hal_mock);
    InSequence seq;
    
    // GIVEN: Message to send
    const char* message = "Hello";
    
    // WHEN: Application sends message
    ApplicationLayer_Send(message);
    
    // THEN: Protocol handler formats message
    ProtocolHandler_Process();
    
    // AND: Buffer manager queues message
    EXPECT_TRUE(BufferManager_HasData());
    
    // AND: UART driver transmits bytes
    EXPECT_CALL(hal_mock, UART_Transmit('H')).Times(1);
    EXPECT_CALL(hal_mock, UART_Transmit('e')).Times(1);
    EXPECT_CALL(hal_mock, UART_Transmit('l')).Times(1);
    EXPECT_CALL(hal_mock, UART_Transmit('l')).Times(1);
    EXPECT_CALL(hal_mock, UART_Transmit('o')).Times(1);
    
    UARTDriver_Process();
    
    // AND: Transmission completes
    EXPECT_EQ(ApplicationLayer_GetStatus(), APP_TX_COMPLETE);
}
```

### Pattern 2: Stress/Load Testing

Test subsystem under high load:

```cpp
/*!
 * @rst
 * .. test:: BufferSubsystem.HandlesRapidMessages
 *    :id: IT_BUF-003
 *    :tests: SRS_BUF-300
 * 
 * Buffer subsystem handles rapid message bursts without loss.
 * @endrst
 */
TEST_F(BufferSubsystemTest, HandlesRapidMessages)
{
    CREATE_MOCK(hal_mock);
    
    const uint32_t message_count = 100;
    uint32_t messages_sent = 0;
    uint32_t messages_received = 0;
    
    // GIVEN: Empty buffers
    EXPECT_EQ(InputBuffer_GetCount(), 0);
    EXPECT_EQ(OutputBuffer_GetCount(), 0);
    
    // WHEN: Rapid message burst
    for (uint32_t i = 0; i < message_count; i++)
    {
        Message msg = {.id = i, .data = {i, i+1, i+2}};
        
        if (InputBuffer_Push(&msg) == STATUS_OK)
        {
            messages_sent++;
        }
    }
    
    // THEN: Most messages buffered (some may be dropped if buffer full)
    EXPECT_GT(messages_sent, message_count * 0.95);  // ≥95% success
    
    // WHEN: Processing all buffered messages
    while (InputBuffer_GetCount() > 0)
    {
        BufferProcessor_Process();
        OutputBuffer_Process();
        messages_received++;
    }
    
    // THEN: No message loss during processing
    EXPECT_EQ(messages_received, messages_sent);
}
```

### Pattern 3: Fault Injection

Test subsystem error handling:

```cpp
/*!
 * @rst
 * .. test:: PowerSubsystem.HandlesUndervoltage
 *    :id: IT_PWR-004
 *    :tests: SRS_PWR-400
 * 
 * Power subsystem detects and handles undervoltage condition.
 * @endrst
 */
TEST_F(PowerSubsystemTest, HandlesUndervoltage)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Normal voltage operation
    EXPECT_CALL(hal_mock, ADC_Read(VOLTAGE_MONITOR_CH))
        .WillOnce(Return(3300));  // 3.3V normal
    
    VoltageMonitor_Update();
    PowerSequencer_Process();
    
    EXPECT_EQ(PowerSubsystem_GetStatus(), POWER_NORMAL);
    
    // WHEN: Voltage drops below threshold
    EXPECT_CALL(hal_mock, ADC_Read(VOLTAGE_MONITOR_CH))
        .WillRepeatedly(Return(2800));  // 2.8V undervoltage
    
    VoltageMonitor_Update();
    
    // THEN: Monitor detects fault
    EXPECT_EQ(VoltageMonitor_GetStatus(), VOLTAGE_LOW);
    
    // WHEN: Power sequencer reacts
    PowerSequencer_Process();
    
    // THEN: Non-critical loads shed
    EXPECT_TRUE(PowerSequencer_IsLoadShed(LOAD_DISPLAY));
    EXPECT_TRUE(PowerSequencer_IsLoadShed(LOAD_LED));
    
    // AND: Critical loads maintained
    EXPECT_FALSE(PowerSequencer_IsLoadShed(LOAD_CPU));
    EXPECT_FALSE(PowerSequencer_IsLoadShed(LOAD_MEMORY));
    
    // AND: System in degraded mode
    EXPECT_EQ(PowerSubsystem_GetStatus(), POWER_DEGRADED);
}
```

### Pattern 4: Recovery Scenarios

Test subsystem recovery from faults:

```cpp
/*!
 * @rst
 * .. test:: SensorSubsystem.RecoversFromTemporaryFault
 *    :id: IT_SENS-005
 *    :tests: SRS_SENS-500
 * 
 * Sensor subsystem recovers when transient fault clears.
 * @endrst
 */
TEST_F(SensorSubsystemTest, RecoversFromTemporaryFault)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Normal operation
    EXPECT_CALL(hal_mock, I2C_Read(SENSOR_ADDR, _, _))
        .WillOnce(DoAll(
            SetArrayArgument<1>({0x12, 0x34}),
            Return(I2C_OK)
        ));
    
    SensorDriver_Read();
    DataValidator_Check();
    SensorFusion_Update();
    
    EXPECT_EQ(SensorSubsystem_GetHealth(), HEALTH_OK);
    
    // WHEN: Transient I2C error occurs
    EXPECT_CALL(hal_mock, I2C_Read(SENSOR_ADDR, _, _))
        .Times(3)
        .WillRepeatedly(Return(I2C_ERROR));
    
    for (int i = 0; i < 3; i++)
    {
        SensorDriver_Read();
        DataValidator_Check();
    }
    
    // THEN: Subsystem detects fault
    EXPECT_EQ(SensorSubsystem_GetHealth(), HEALTH_DEGRADED);
    
    // WHEN: Communication recovers
    EXPECT_CALL(hal_mock, I2C_Read(SENSOR_ADDR, _, _))
        .WillOnce(DoAll(
            SetArrayArgument<1>({0x56, 0x78}),
            Return(I2C_OK)
        ));
    
    SensorDriver_Read();
    DataValidator_Check();
    SensorFusion_Update();
    
    // THEN: Subsystem recovers
    EXPECT_EQ(SensorSubsystem_GetHealth(), HEALTH_OK);
    EXPECT_TRUE(SensorFusion_HasValidData());
}
```

### Pattern 5: Timing Verification

Test subsystem timing requirements:

```cpp
/*!
 * @rst
 * .. test:: ControlSubsystem.MeetsTimingConstraints
 *    :id: IT_CTRL-006
 *    :tests: SRS_CTRL-600
 * 
 * Control subsystem completes processing within deadline.
 * @endrst
 */
TEST_F(ControlSubsystemTest, MeetsTimingConstraints)
{
    CREATE_MOCK(hal_mock);
    
    const uint32_t deadline_ms = 10;
    uint32_t max_execution_time = 0;
    
    // GIVEN: Subsystem initialized
    
    // WHEN: Running 1000 cycles
    for (uint32_t cycle = 0; cycle < 1000; cycle++)
    {
        uint32_t start_time = GetTickCount();
        
        // Execute subsystem processing
        SensorInterface_Read();
        ControlAlgorithm_Calculate();
        ActuatorInterface_Write();
        
        uint32_t execution_time = GetTickCount() - start_time;
        
        if (execution_time > max_execution_time)
        {
            max_execution_time = execution_time;
        }
    }
    
    // THEN: Worst-case execution time within deadline
    EXPECT_LE(max_execution_time, deadline_ms);
}
```

## Multi-Subsystem Integration

### Testing Subsystem Interactions

Test how multiple subsystems work together:

```cpp
class MultiSubsystemTest : public Test
{
protected:
    void SetUp() override
    {
        CREATE_MOCK(hal_mock);
        
        // Initialize all subsystems
        SensorSubsystem_Init();
        ControlSubsystem_Init();
        ActuatorSubsystem_Init();
        CommunicationSubsystem_Init();
    }
    
    void RunSystemCycle()
    {
        // Run all subsystems in coordination
        SensorSubsystem_Process();
        ControlSubsystem_Process();
        ActuatorSubsystem_Process();
        CommunicationSubsystem_Process();
    }
};

/*!
 * @rst
 * .. test:: MultiSubsystem.CoordinatesClosedLoop
 *    :id: IT_MULTI-007
 *    :tests: SRS_MULTI-700
 * 
 * Sensor, control, and actuator subsystems form working control loop.
 * @endrst
 */
TEST_F(MultiSubsystemTest, CoordinatesClosedLoop)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: System setpoint
    const float setpoint = 100.0f;
    ControlSubsystem_SetSetpoint(setpoint);
    
    // Simulated plant value
    float plant_value = 50.0f;
    
    // WHEN: Closed loop runs for several iterations
    for (int iteration = 0; iteration < 20; iteration++)
    {
        // Sensor reads plant
        EXPECT_CALL(hal_mock, ADC_Read(PLANT_SENSOR))
            .WillOnce(Return(static_cast<uint16_t>(plant_value * 10)));
        
        SensorSubsystem_Process();
        
        // Controller calculates output
        ControlSubsystem_Process();
        float control_output = ControlSubsystem_GetOutput();
        
        // Actuator applies control
        EXPECT_CALL(hal_mock, PWM_SetDutyCycle(ACTUATOR_PWM, _))
            .Times(1);
        
        ActuatorSubsystem_Process();
        
        // Simulate plant response (simple integrator)
        plant_value += (control_output - 50.0f) * 0.2f;
        
        // Communication subsystem logs telemetry
        CommunicationSubsystem_Process();
    }
    
    // THEN: System converges toward setpoint
    EXPECT_NEAR(plant_value, setpoint, 5.0f);
}
```

## Subsystem Test Organization

### Directory Structure

```
test/
├── integration/
│   ├── subsystem_lighting/
│   │   ├── test_lighting_nominal.cc
│   │   ├── test_lighting_faults.cc
│   │   ├── test_lighting_performance.cc
│   │   └── CMakeLists.txt
│   ├── subsystem_communication/
│   │   ├── test_comm_nominal.cc
│   │   ├── test_comm_errors.cc
│   │   ├── test_comm_stress.cc
│   │   └── CMakeLists.txt
│   └── system/
│       ├── test_multi_subsystem.cc
│       └── CMakeLists.txt
```

### CMake Setup for Subsystem Tests

```cmake
# subsystem_lighting/CMakeLists.txt

# Subsystem integration test executable
add_executable(integration_lighting_subsystem
    test_lighting_nominal.cc
    test_lighting_faults.cc
    test_lighting_performance.cc
)

# Link all subsystem components (REAL implementations)
target_link_libraries(integration_lighting_subsystem
    PRIVATE
        component_light_sensor
        component_dimmer_logic
        component_pwm_controller
        component_led_driver
        # Mock only HAL
        mock_hal
        GTest::gtest_main
)

# Register tests
add_test(NAME LightingSubsystemNominal 
         COMMAND integration_lighting_subsystem --gtest_filter=*Nominal*)
add_test(NAME LightingSubsystemFaults
         COMMAND integration_lighting_subsystem --gtest_filter=*Fault*)
```

## Subsystem Test Checklist

Before writing subsystem test:

- [ ] Subsystem components identified
- [ ] Subsystem boundaries clearly defined
- [ ] External interfaces identified (to be mocked)
- [ ] Internal interfaces use real implementations
- [ ] Unit tests exist for individual components
- [ ] Test scenarios cover:
  - [ ] Nominal operation (happy path)
  - [ ] Error conditions and recovery
  - [ ] Boundary conditions
  - [ ] Timing constraints
  - [ ] Load/stress conditions
- [ ] BDD structure (Given-When-Then)
- [ ] Proper traceability (IT_xxx to SRS)
- [ ] Fixture provides subsystem-level helpers

## Best Practices

### 1. Test Subsystem Capabilities, Not Implementation

Focus on what the subsystem provides:

```cpp
// ✓ GOOD - Test capability
TEST(LightingSubsystem, AutoAdjustsBrightnessBasedOnAmbient)

// ✗ BAD - Test implementation details
TEST(LightingSubsystem, DimmerLogicCallsPWMWithCalculatedValue)
```

### 2. Use Realistic Scenarios

Test realistic use cases:

```cpp
// ✓ GOOD - Realistic scenario
TEST(PowerSubsystem, HandlesStartupSequence)
{
    // Simulates actual power-on sequence
}

// ✗ BAD - Artificial scenario
TEST(PowerSubsystem, CallsFunctions)
{
    // Just calls functions without context
}
```

### 3. Mock Only External Boundaries

```cpp
// ✓ GOOD - Mock HAL only
#include "mock_hal.h"
#include "sensor.h"  // Real
#include "controller.h"  // Real
#include "actuator.h"  // Real

// ✗ BAD - Mock internal components
#include "mock_sensor.h"
#include "mock_controller.h"
#include "actuator.h"  // Only test actuator?
```

### 4. Provide Subsystem-Level Helpers

```cpp
class SubsystemFixture : public Test
{
protected:
    // High-level helpers hide details
    void SimulateUserAction(Action action);
    void SimulateEnvironmentalChange(Condition cond);
    void ExpectSubsystemInState(State state);
};
```

## Summary

Subsystem testing:
- Groups related components into logical units
- Tests component interactions within subsystem
- Mocks only external boundaries
- Verifies end-to-end subsystem capabilities
- Covers nominal, fault, and stress scenarios
- Provides confidence before system-level testing

Key practices:
- Define clear subsystem boundaries
- Use real implementations within subsystem
- Test realistic scenarios
- Verify timing and performance
- Test fault handling and recovery
- Provide subsystem-level test helpers
