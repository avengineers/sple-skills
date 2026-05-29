# Advanced Integration Test Patterns

## Pattern Catalog for Component Integration

### 1. Pipeline Integration

Testing data flowing through a processing pipeline:

```cpp
/*!
 * @rst
 * .. test:: DataPipeline.TransformsDataThroughStages
 *    :id: IT_PIPE-001
 *    :tests: SRS_PIPE-100
 * 
 * Raw sensor data transforms through filtering, scaling, and formatting stages.
 * @endrst
 */
TEST_F(PipelineIntegrationTest, TransformsDataThroughStages)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Raw sensor input
    const uint16_t raw_adc = 2048;  // Mid-scale ADC value
    EXPECT_CALL(hal_mock, ADC_Read(SENSOR_CH))
        .WillOnce(Return(raw_adc));
    
    // WHEN: Data flows through pipeline stages
    
    // Stage 1: Sensor reads ADC
    Sensor_Update();
    uint16_t sensor_out = Sensor_GetRawValue();
    EXPECT_EQ(sensor_out, raw_adc);
    
    // Stage 2: Filter smooths data (moving average)
    Filter_AddSample(sensor_out);
    uint16_t filtered = Filter_GetOutput();
    EXPECT_NEAR(filtered, raw_adc, 50);  // Allow filtering variance
    
    // Stage 3: Scaler converts to engineering units
    Scaler_SetInput(filtered);
    float scaled = Scaler_GetOutputFloat();  // Converts to °C
    EXPECT_NEAR(scaled, 25.0f, 1.0f);  // ~25°C
    
    // Stage 4: Formatter prepares for display
    Formatter_SetValue(scaled);
    const char* display_str = Formatter_GetString();
    EXPECT_STREQ(display_str, "25.0");
    
    // THEN: Output matches expected transformation
    EXPECT_CALL(hal_mock, Display_Write(display_str))
        .Times(1);
}
```

### 2. Fan-Out Integration

One input triggers multiple output paths:

```cpp
/*!
 * @rst
 * .. test:: FanOut.BroadcastsToMultipleConsumers
 *    :id: IT_FAN-002
 *    :tests: SRS_FAN-200
 * 
 * Event broadcaster notifies all registered consumers.
 * @endrst
 */
TEST_F(FanOutTest, BroadcastsToMultipleConsumers)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Multiple consumers registered with broadcaster
    bool consumer_a_called = false;
    bool consumer_b_called = false;
    bool consumer_c_called = false;
    
    Broadcaster_RegisterConsumer([&](uint8_t val) {
        consumer_a_called = true;
        ConsumerA_Process(val);
    });
    
    Broadcaster_RegisterConsumer([&](uint8_t val) {
        consumer_b_called = true;
        ConsumerB_Process(val);
    });
    
    Broadcaster_RegisterConsumer([&](uint8_t val) {
        consumer_c_called = true;
        ConsumerC_Process(val);
    });
    
    // WHEN: Event broadcast
    Broadcaster_SendEvent(42);
    
    // THEN: All consumers notified
    EXPECT_TRUE(consumer_a_called);
    EXPECT_TRUE(consumer_b_called);
    EXPECT_TRUE(consumer_c_called);
    
    // AND: All processed same value
    EXPECT_EQ(ConsumerA_GetLastValue(), 42);
    EXPECT_EQ(ConsumerB_GetLastValue(), 42);
    EXPECT_EQ(ConsumerC_GetLastValue(), 42);
}
```

### 3. Collector Integration (Fan-In)

Multiple inputs combine into single output:

```cpp
/*!
 * @rst
 * .. test:: Collector.AggregatesMultipleInputs
 *    :id: IT_COLL-003
 *    :tests: SRS_COLL-300
 * 
 * Aggregator combines multiple sensor inputs for decision logic.
 * @endrst
 */
TEST_F(CollectorTest, AggregatesMultipleInputs)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Multiple sensors provide inputs
    EXPECT_CALL(hal_mock, ADC_Read(TEMP_SENSOR))
        .WillOnce(Return(2500));  // 25°C
    EXPECT_CALL(hal_mock, ADC_Read(HUMIDITY_SENSOR))
        .WillOnce(Return(6000));  // 60%
    EXPECT_CALL(hal_mock, ADC_Read(PRESSURE_SENSOR))
        .WillOnce(Return(10132)); // 1013.2 hPa
    
    // WHEN: All sensors update
    TempSensor_Update();
    HumiditySensor_Update();
    PressureSensor_Update();
    
    // AND: Aggregator combines readings
    Aggregator_Collect();
    
    // THEN: Decision logic uses combined data
    DecisionEngine_Process();
    
    // THEN: Comfort index calculated from all inputs
    uint8_t comfort = DecisionEngine_GetComfortIndex();
    EXPECT_GT(comfort, 70);  // Good comfort level
}
```

### 4. Feedback Loop Integration

Output feeds back as input:

```cpp
/*!
 * @rst
 * .. test:: FeedbackControl.StabilizesWithFeedback
 *    :id: IT_FB-004
 *    :tests: SRS_FB-400
 * 
 * Closed-loop controller stabilizes system using feedback.
 * @endrst
 */
TEST_F(FeedbackControlTest, StabilizesWithFeedback)
{
    CREATE_MOCK(hal_mock);
    
    const float setpoint = 50.0f;
    const float tolerance = 2.0f;
    
    // GIVEN: System starts below setpoint
    float current_value = 30.0f;
    
    // WHEN: Controller runs with feedback
    for (int iteration = 0; iteration < 50; iteration++)
    {
        // Read current state
        EXPECT_CALL(hal_mock, ADC_Read(FEEDBACK_SENSOR))
            .WillOnce(Return(static_cast<uint16_t>(current_value * 10)));
        
        FeedbackSensor_Update();
        
        // Controller calculates correction
        Controller_SetSetpoint(setpoint);
        Controller_Process();
        
        // Apply control output
        float control_output = Controller_GetOutput();
        
        // Simulate system response (simple model)
        current_value += (control_output - 50.0f) * 0.1f;
        
        // Check if stabilized
        if (fabs(current_value - setpoint) < tolerance)
        {
            break;
        }
    }
    
    // THEN: System stabilizes near setpoint
    EXPECT_NEAR(current_value, setpoint, tolerance);
}
```

### 5. State Machine Coordination

Multiple state machines coordinate:

```cpp
/*!
 * @rst
 * .. test:: StateMachineCoord.CoordinatesSubsystemStates
 *    :id: IT_SM-005
 *    :tests: SRS_SM-500
 * 
 * Master state machine coordinates subsystem state transitions.
 * @endrst
 */
TEST_F(StateMachineCoordTest, CoordinatesSubsystemStates)
{
    CREATE_MOCK(hal_mock);
    InSequence seq;
    
    // GIVEN: All subsystems in IDLE state
    EXPECT_EQ(SubsystemA_GetState(), STATE_IDLE);
    EXPECT_EQ(SubsystemB_GetState(), STATE_IDLE);
    EXPECT_EQ(SubsystemC_GetState(), STATE_IDLE);
    
    // WHEN: Master transitions to STARTING
    MasterController_SetState(STATE_STARTING);
    MasterController_Process();
    
    // THEN: Subsystems transition in coordinated order
    EXPECT_EQ(SubsystemA_GetState(), STATE_INITIALIZING);
    EXPECT_EQ(SubsystemB_GetState(), STATE_IDLE);  // Waits for A
    EXPECT_EQ(SubsystemC_GetState(), STATE_IDLE);  // Waits for B
    
    // WHEN: Subsystem A completes initialization
    SubsystemA_CompleteInit();
    MasterController_Process();
    
    // THEN: Subsystem B starts
    EXPECT_EQ(SubsystemA_GetState(), STATE_READY);
    EXPECT_EQ(SubsystemB_GetState(), STATE_INITIALIZING);
    EXPECT_EQ(SubsystemC_GetState(), STATE_IDLE);
    
    // WHEN: Subsystem B completes initialization
    SubsystemB_CompleteInit();
    MasterController_Process();
    
    // THEN: Subsystem C starts and all become ready
    EXPECT_EQ(SubsystemA_GetState(), STATE_READY);
    EXPECT_EQ(SubsystemB_GetState(), STATE_READY);
    EXPECT_EQ(SubsystemC_GetState(), STATE_INITIALIZING);
    
    SubsystemC_CompleteInit();
    MasterController_Process();
    
    // THEN: Master transitions to RUNNING
    EXPECT_EQ(MasterController_GetState(), STATE_RUNNING);
}
```

### 6. Producer-Consumer with Queue

Testing queued communication between components:

```cpp
/*!
 * @rst
 * .. test:: ProducerConsumer.HandlesQueuedMessages
 *    :id: IT_QUEUE-006
 *    :tests: SRS_QUEUE-600
 * 
 * Producer and consumer communicate via message queue correctly.
 * @endrst
 */
TEST_F(ProducerConsumerTest, HandlesQueuedMessages)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Empty message queue
    EXPECT_EQ(MessageQueue_GetCount(), 0);
    
    // WHEN: Producer generates multiple messages
    for (int i = 1; i <= 5; i++)
    {
        Message msg = {.id = i, .data = i * 10};
        Producer_SendMessage(&msg);
    }
    
    // THEN: All messages queued
    EXPECT_EQ(MessageQueue_GetCount(), 5);
    
    // WHEN: Consumer processes messages
    for (int i = 1; i <= 5; i++)
    {
        Consumer_ProcessNext();
        
        // THEN: Messages processed in order
        EXPECT_EQ(Consumer_GetLastProcessedId(), i);
        EXPECT_EQ(Consumer_GetLastProcessedData(), i * 10);
    }
    
    // THEN: Queue empty
    EXPECT_EQ(MessageQueue_GetCount(), 0);
}
```

### 7. Multi-Rate Coordination

Components running at different rates coordinate correctly:

```cpp
/*!
 * @rst
 * .. test:: MultiRate.CoordinatesDifferentRates
 *    :id: IT_RATE-007
 *    :tests: SRS_RATE-700
 * 
 * Fast and slow components exchange data at correct intervals.
 * @endrst
 */
TEST_F(MultiRateTest, CoordinatesDifferentRates)
{
    CREATE_MOCK(hal_mock);
    
    uint8_t fast_executions = 0;
    uint8_t slow_executions = 0;
    uint8_t data_exchanges = 0;
    
    // GIVEN: Fast component (10ms), Slow component (50ms)
    
    // WHEN: System runs for 100ms
    for (uint32_t tick = 0; tick < 100; tick++)
    {
        // Fast component runs every 10ms
        if (tick % 10 == 0)
        {
            FastComponent_Process();
            fast_executions++;
        }
        
        // Slow component runs every 50ms
        if (tick % 50 == 0)
        {
            SlowComponent_Process();
            slow_executions++;
            
            // Check data exchange
            if (FastComponent_HasNewData())
            {
                uint16_t data = FastComponent_GetData();
                SlowComponent_ReceiveData(data);
                data_exchanges++;
            }
        }
    }
    
    // THEN: Execution counts correct
    EXPECT_EQ(fast_executions, 10);  // 100ms / 10ms
    EXPECT_EQ(slow_executions, 2);   // 100ms / 50ms
    
    // AND: Data exchanged at slow rate
    EXPECT_EQ(data_exchanges, 2);
}
```

### 8. Cascading Timeouts

Testing timeout chain across components:

```cpp
/*!
 * @rst
 * .. test:: TimeoutChain.PropagatesTimeoutThroughLayers
 *    :id: IT_TO-008
 *    :tests: SRS_TO-800
 * 
 * Timeout in lower layer propagates correctly to upper layers.
 * @endrst
 */
TEST_F(TimeoutChainTest, PropagatesTimeoutThroughLayers)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Communication initiated
    ApplicationLayer_SendRequest();
    
    // WHEN: Transport layer waits for response
    for (uint32_t tick = 0; tick < 100; tick++)
    {
        TransportLayer_Tick1ms();
    }
    
    // THEN: Transport timeout triggers
    EXPECT_EQ(TransportLayer_GetStatus(), TRANSPORT_TIMEOUT);
    
    // WHEN: Application layer processes transport result
    ApplicationLayer_Process();
    
    // THEN: Application receives timeout notification
    EXPECT_EQ(ApplicationLayer_GetStatus(), APP_COMM_TIMEOUT);
    
    // AND: Error handler invoked
    EXPECT_TRUE(ErrorHandler_WasInvoked());
    EXPECT_EQ(ErrorHandler_GetLastError(), ERR_COMMUNICATION_TIMEOUT);
}
```

### 9. Resource Sharing

Multiple components share limited resource:

```cpp
/*!
 * @rst
 * .. test:: ResourceSharing.ArbitratesAccessCorrectly
 *    :id: IT_RES-009
 *    :tests: SRS_RES-900
 * 
 * Resource manager arbitrates access between competing components.
 * @endrst
 */
TEST_F(ResourceSharingTest, ArbitratesAccessCorrectly)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Shared SPI bus with multiple users
    
    // WHEN: Component A requests bus
    SPIManager_RequestAccess(COMPONENT_A);
    
    // THEN: Access granted
    EXPECT_TRUE(SPIManager_HasAccess(COMPONENT_A));
    
    // WHEN: Component B requests bus (conflict)
    SPIManager_RequestAccess(COMPONENT_B);
    
    // THEN: Access denied (A still owns it)
    EXPECT_FALSE(SPIManager_HasAccess(COMPONENT_B));
    EXPECT_TRUE(SPIManager_HasAccess(COMPONENT_A));
    
    // WHEN: Component A releases bus
    ComponentA_CompleteSPITransaction();
    SPIManager_ReleaseAccess(COMPONENT_A);
    
    // THEN: Component B gains access
    EXPECT_TRUE(SPIManager_HasAccess(COMPONENT_B));
    EXPECT_FALSE(SPIManager_HasAccess(COMPONENT_A));
}
```

### 10. Graceful Degradation

System continues with reduced functionality after component failure:

```cpp
/*!
 * @rst
 * .. test:: GracefulDegradation.ContinuesWithReducedCapability
 *    :id: IT_DEG-010
 *    :tests: SRS_DEG-1000
 * 
 * System degrades gracefully when non-critical sensor fails.
 * @endrst
 */
TEST_F(GracefulDegradationTest, ContinuesWithReducedCapability)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: System operating with all sensors
    EXPECT_EQ(SystemManager_GetMode(), MODE_NORMAL);
    EXPECT_EQ(SystemManager_GetCapability(), CAP_FULL);
    
    // WHEN: Non-critical ambient light sensor fails
    EXPECT_CALL(hal_mock, ADC_Read(AMBIENT_SENSOR))
        .WillRepeatedly(Return(ADC_ERROR));
    
    AmbientSensor_Update();
    
    // THEN: Sensor reports fault
    EXPECT_EQ(AmbientSensor_GetStatus(), SENSOR_FAULT);
    
    // WHEN: Supervisor processes fault
    Supervisor_Process();
    
    // THEN: System continues in reduced mode
    EXPECT_EQ(SystemManager_GetMode(), MODE_REDUCED);
    EXPECT_EQ(SystemManager_GetCapability(), CAP_WITHOUT_AMBIENT);
    
    // WHEN: Core functionality executes
    CoreController_Process();
    
    // THEN: Core features still work
    EXPECT_TRUE(CoreController_IsOperational());
    
    // AND: Features depending on ambient sensor disabled
    EXPECT_FALSE(AutoDimming_IsEnabled());
    EXPECT_FALSE(PowerSaving_IsEnabled());
    
    // BUT: Manual control still available
    EXPECT_TRUE(ManualControl_IsEnabled());
}
```

### 11. Synchronization Barrier

Components wait at barrier until all ready:

```cpp
/*!
 * @rst
 * .. test:: Synchronization.WaitsAtBarrierUntilAllReady
 *    :id: IT_SYNC-011
 *    :tests: SRS_SYNC-1100
 * 
 * Synchronization barrier ensures all components ready before proceeding.
 * @endrst
 */
TEST_F(SynchronizationTest, WaitsAtBarrierUntilAllReady)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Three components starting initialization
    ComponentA_StartInit();
    ComponentB_StartInit();
    ComponentC_StartInit();
    
    // WHEN: A completes quickly
    ComponentA_CompleteInit();
    Barrier_NotifyReady(COMPONENT_A);
    
    // THEN: Barrier not released (waiting for B and C)
    EXPECT_FALSE(Barrier_IsReleased());
    EXPECT_EQ(SystemController_GetPhase(), PHASE_INIT);
    
    // WHEN: B completes
    ComponentB_CompleteInit();
    Barrier_NotifyReady(COMPONENT_B);
    
    // THEN: Still waiting for C
    EXPECT_FALSE(Barrier_IsReleased());
    EXPECT_EQ(SystemController_GetPhase(), PHASE_INIT);
    
    // WHEN: C completes (last one)
    ComponentC_CompleteInit();
    Barrier_NotifyReady(COMPONENT_C);
    
    // THEN: Barrier releases, system proceeds
    EXPECT_TRUE(Barrier_IsReleased());
    
    SystemController_Process();
    EXPECT_EQ(SystemController_GetPhase(), PHASE_RUNNING);
}
```

### 12. Data Consistency Across Components

Ensuring consistent view of shared data:

```cpp
/*!
 * @rst
 * .. test:: DataConsistency.MaintainsConsistentView
 *    :id: IT_CONS-012
 *    :tests: SRS_CONS-1200
 * 
 * Multiple readers see consistent snapshot of shared data.
 * @endrst
 */
TEST_F(DataConsistencyTest, MaintainsConsistentView)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: Shared data structure
    SharedData data = {.value_a = 10, .value_b = 20, .checksum = 30};
    DataManager_Write(&data);
    
    // WHEN: Multiple components read simultaneously
    const SharedData* reader1 = ComponentA_ReadData();
    const SharedData* reader2 = ComponentB_ReadData();
    const SharedData* reader3 = ComponentC_ReadData();
    
    // THEN: All see same consistent snapshot
    EXPECT_EQ(reader1->value_a, 10);
    EXPECT_EQ(reader1->value_b, 20);
    EXPECT_EQ(reader1->checksum, 30);
    
    EXPECT_EQ(reader2->value_a, reader1->value_a);
    EXPECT_EQ(reader2->value_b, reader1->value_b);
    EXPECT_EQ(reader2->checksum, reader1->checksum);
    
    EXPECT_EQ(reader3->value_a, reader1->value_a);
    EXPECT_EQ(reader3->value_b, reader1->value_b);
    EXPECT_EQ(reader3->checksum, reader1->checksum);
    
    // WHEN: Writer updates data
    data.value_a = 15;
    data.value_b = 25;
    data.checksum = 40;
    DataManager_Write(&data);
    
    // THEN: New readers see updated values
    const SharedData* reader4 = ComponentA_ReadData();
    EXPECT_EQ(reader4->value_a, 15);
    EXPECT_EQ(reader4->value_b, 25);
    EXPECT_EQ(reader4->checksum, 40);
}
```

## Pattern Selection Guide

| Integration Scenario | Pattern to Use |
|----------------------|----------------|
| Sequential data transformation | Pipeline Integration |
| One-to-many event distribution | Fan-Out Integration |
| Many-to-one data collection | Collector Integration |
| Control with sensor feedback | Feedback Loop Integration |
| Dependent state transitions | State Machine Coordination |
| Asynchronous communication | Producer-Consumer with Queue |
| Mixed execution frequencies | Multi-Rate Coordination |
| Chained error propagation | Cascading Timeouts |
| Shared hardware/bus | Resource Sharing |
| Non-critical failures | Graceful Degradation |
| Waiting for multiple tasks | Synchronization Barrier |
| Shared data access | Data Consistency |

## Complex Scenario Examples

### Example: Complete Automotive Window Control

```cpp
TEST_F(WindowControlSystem, CompleteOperation)
{
    CREATE_MOCK(hal_mock);
    
    // GIVEN: System initialized, window closed
    ButtonHandler_Init();
    MotorController_Init();
    PositionSensor_Init();
    SafetyMonitor_Init();
    
    EXPECT_EQ(PositionSensor_GetPosition(), WINDOW_CLOSED);
    
    // WHEN: User presses window down button
    EXPECT_CALL(hal_mock, GPIO_Read(BUTTON_DOWN_PIN))
        .Times(100)
        .WillRepeatedly(Return(PRESSED));
    
    // Process button debounce (50ms)
    for (int i = 0; i < 50; i++)
    {
        ButtonHandler_Tick1ms();
    }
    
    // THEN: Button press detected
    EXPECT_TRUE(ButtonHandler_GetDownPressed());
    
    // WHEN: Motor controller starts motor
    MotorController_Process();
    EXPECT_CALL(hal_mock, PWM_SetDutyCycle(MOTOR_PWM, 80))
        .Times(1);
    
    // Simulate window movement
    for (int pos = 0; pos < 100; pos++)
    {
        EXPECT_CALL(hal_mock, ADC_Read(POS_SENSOR))
            .WillOnce(Return(pos * 10));
        
        PositionSensor_Update();
        SafetyMonitor_Check();
        MotorController_Update();
        
        // Simulate obstacle at 50%
        if (pos == 50)
        {
            EXPECT_CALL(hal_mock, ADC_Read(FORCE_SENSOR))
                .WillRepeatedly(Return(FORCE_THRESHOLD + 100));
        }
    }
    
    // THEN: Safety monitor detects obstacle
    EXPECT_TRUE(SafetyMonitor_ObstacleDetected());
    
    // AND: Motor reverses direction
    EXPECT_EQ(MotorController_GetDirection(), MOTOR_REVERSE);
    
    // WHEN: Window returns to safe position
    EXPECT_CALL(hal_mock, PWM_SetDutyCycle(MOTOR_PWM, 0))
        .Times(1);
    
    // THEN: System in safe state
    EXPECT_EQ(SafetyMonitor_GetState(), SAFETY_ACTIVE);
}
```

This demonstrates integration of:
- Button handling with debounce
- Motor control with PWM
- Position sensing with ADC
- Safety monitoring
- Event-driven coordination
