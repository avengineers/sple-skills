# Integration Test Code Templates

## Basic BDD Integration Test Template

```cpp
#include <gtest/gtest.h>
extern "C" {
    #include "autoconf.h"
    #include "<component_a>.h"
    #include "<component_b>.h"
    #include "<component_c>.h"
}
#include "mockup_hal.h"  // Mock only HAL layer

class SubsystemIntegrationTest : public Test
{
protected:
    void SetUp() override {
        // Initialize all components
        ComponentA_Init();
        ComponentB_Init();
        ComponentC_Init();
    }
    
    void TearDown() override {
        // Cleanup if needed
    }
};

/*!
 * @rst
 * .. test:: SubsystemIntegration.DescriptiveScenario
 *    :id: IT_SUBSYS-001
 *    :tests: SRS_SUBSYS-100
 * 
 * Brief: Integration scenario description.
 * @endrst
 */
TEST_F(SubsystemIntegrationTest, DescriptiveScenario)
{
    CREATE_MOCK(hal_mock);  // Mock only hardware
    
    // GIVEN: Subsystem in known state
    EXPECT_CALL(hal_mock, HAL_GPIO_Read(SENSOR_PIN))
        .WillOnce(Return(HIGH));
    
    // WHEN: Stimulus triggers component A
    ComponentA_ProcessInput();
    
    // THEN: Data flows through B to C and produces output
    ComponentB_Process();
    ComponentC_Process();
    
    EXPECT_CALL(hal_mock, HAL_GPIO_Write(OUTPUT_PIN, HIGH))
        .Times(1);
}
```

## Data Flow Verification Template

```cpp
/*!
 * @rst
 * .. test:: DataFlow.SensorToActuator
 *    :id: IT_FLOW-001
 *    :tests: SRS_FLOW-001
 * @endrst
 */
TEST_F(SystemIntegrationTest, DataFlowSensorToActuator)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Sensor provides valid data
    SensorData input_data = {.temperature = 25.0, .humidity = 60.0};
    EXPECT_CALL(hal_mock, HAL_Sensor_Read())
        .WillOnce(Return(input_data));
    
    // WHEN: Processing pipeline executes
    SensorManager_ReadSensors();
    DataProcessor_ProcessSensorData();
    ActuatorController_UpdateOutputs();
    
    // THEN: Actuator receives processed data
    ActuatorCommand expected_cmd = {.fan_speed = 50, .heater_on = false};
    EXPECT_CALL(hal_mock, HAL_Actuator_Set(expected_cmd))
        .Times(1);
    
    ActuatorController_ExecuteCommands();
}
```

## Event Propagation Template

```cpp
/*!
 * @rst
 * .. test:: EventPropagation.ButtonToDisplay
 *    :id: IT_EVENT-001
 *    :tests: SRS_UI-001
 * @endrst
 */
TEST_F(UIIntegrationTest, EventPropagationButtonToDisplay)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: UI system initialized and display clear
    EXPECT_CALL(hal_mock, HAL_Display_Clear())
        .Times(1);
    DisplayManager_Init();
    
    // WHEN: Button press event occurs
    ButtonEvent event = {.button_id = BUTTON_MENU, .press_type = PRESS_SHORT};
    EventManager_PublishEvent(EVENT_BUTTON_PRESS, &event);
    EventManager_ProcessEvents();  // Process all pending events
    
    // THEN: Display updates with menu
    DisplayCommand expected_display = {
        .command = DISPLAY_SHOW_MENU,
        .menu_id = MAIN_MENU
    };
    EXPECT_CALL(hal_mock, HAL_Display_ShowMenu(MAIN_MENU))
        .Times(1);
    
    DisplayManager_ExecuteCommands();
}
```

## Component State Coordination Template

```cpp
/*!
 * @rst
 * .. test:: StateCoordination.SystemStartup
 *    :id: IT_STATE-001
 *    :tests: SRS_STARTUP-001
 * @endrst
 */
TEST_F(StartupIntegrationTest, StateCoordinationSystemStartup)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: System in reset state
    EXPECT_CALL(hal_mock, HAL_PowerOn_SelfTest())
        .WillOnce(Return(SELF_TEST_PASS));
    
    // WHEN: System startup sequence executes
    SystemController_Initialize();
    ComponentManager_InitializeAll();
    SystemController_StartOperations();
    
    // THEN: All components reach operational state
    EXPECT_EQ(COMPONENT_STATE_OPERATIONAL, ComponentA_GetState());
    EXPECT_EQ(COMPONENT_STATE_OPERATIONAL, ComponentB_GetState());
    EXPECT_EQ(COMPONENT_STATE_OPERATIONAL, SystemController_GetState());
}
```

## Parameterized Integration Test Template

```cpp
class ParameterizedIntegrationTest : public SubsystemIntegrationTest,
                                   public WithParamInterface<TestScenario>
{};

/*!
 * @rst
 * .. test:: ParameterizedIntegration.MultipleInputScenarios
 *    :id: IT_PARAM-001
 *    :tests: SRS_INPUT-001, SRS_INPUT-002, SRS_INPUT-003
 * @endrst
 */
TEST_P(ParameterizedIntegrationTest, MultipleInputScenarios)
{
    CREATE_MOCK(hal_mock);
    TestScenario scenario = GetParam();
    
    // GIVEN: Input configured for scenario
    EXPECT_CALL(hal_mock, HAL_Input_Read())
        .WillOnce(Return(scenario.input_value));
    
    // WHEN: Processing occurs
    InputManager_ProcessInput();
    BusinessLogic_Execute();
    OutputManager_UpdateOutputs();
    
    // THEN: Expected output is produced
    EXPECT_CALL(hal_mock, HAL_Output_Set(scenario.expected_output))
        .Times(1);
    
    OutputManager_ApplyOutputs();
}

INSTANTIATE_TEST_SUITE_P(
    MultipleScenarios,
    ParameterizedIntegrationTest,
    Values(
        TestScenario{.input_value = 10, .expected_output = OUTPUT_LOW},
        TestScenario{.input_value = 50, .expected_output = OUTPUT_MED},
        TestScenario{.input_value = 90, .expected_output = OUTPUT_HIGH}
    )
);
```

## Error Recovery Template

```cpp
/*!
 * @rst
 * .. test:: ErrorRecovery.ComponentFailureRecovery
 *    :id: IT_ERROR-001
 *    :tests: SRS_ERROR-001
 * @endrst
 */
TEST_F(ErrorRecoveryIntegrationTest, ComponentFailureRecovery)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: System operating normally
    SystemController_Initialize();
    ComponentA_Init();
    ComponentB_Init();
    
    // WHEN: Component A fails
    ComponentA_InjectError(ERROR_COMMUNICATION_TIMEOUT);
    SystemController_ProcessErrors();
    
    // THEN: System switches to Component B backup
    EXPECT_EQ(COMPONENT_STATE_FAILED, ComponentA_GetState());
    EXPECT_EQ(COMPONENT_STATE_BACKUP_ACTIVE, ComponentB_GetState());
    EXPECT_EQ(SYSTEM_MODE_DEGRADED, SystemController_GetMode());
}
```

## CMake Registration Template

```cmake
# Integration test executable
add_executable(integration_subsystem_test
    src/integration_subsystem_test.cpp
    ${COMPONENT_A_SOURCES}
    ${COMPONENT_B_SOURCES}
    ${COMPONENT_C_SOURCES}
)

target_link_libraries(integration_subsystem_test
    PRIVATE
        gtest_main
        gmock
        component_a
        component_b
        component_c
        mockup_hal
)

target_include_directories(integration_subsystem_test
    PRIVATE
        ${CMAKE_SOURCE_DIR}/src/components/component_a
        ${CMAKE_SOURCE_DIR}/src/components/component_b
        ${CMAKE_SOURCE_DIR}/src/components/component_c
        ${CMAKE_SOURCE_DIR}/test/mocks
)

# Register with CTest
gtest_discover_tests(integration_subsystem_test
    TEST_PREFIX "Integration."
    PROPERTIES LABELS "integration"
)
```