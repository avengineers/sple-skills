# Advanced Test Patterns

## Table of Contents

| Section | Line | Behavior type |
|---------|------|---------------|
| [1. Multi-State Sequences](#1-multi-state-sequences) | ~5 | State transitions |
| [2. Accumulator/Counter](#2-accumulatorcounter-behavior) | ~43 | Value accumulation |
| [3. Hysteresis/Threshold](#3-hysteresisthreshold-behavior) | ~98 | Threshold with deadband |
| [4. Rate Limiting/Throttling](#4-rate-limitingthrottling) | ~172 | Action frequency limits |
| [5. Moving Average/Filtering](#5-moving-averagefiltering) | ~252 | Signal smoothing |
| [6. Retry Logic](#6-retry-logic) | ~311 | Transient failure handling |
| [7. Circular Buffers](#7-circular-buffers) | ~371 | Queue/FIFO behavior |
| [8. Watchdog/Timeout](#8-watchdogtimeout-behavior) | ~434 | Stuck detection |
| [9. Multi-Phase Initialization](#9-multi-phase-initialization) | ~495 | Startup sequences |
| [10. Event Coalescing](#10-event-coalescing) | ~558 | Merge rapid events |
| [Pattern Selection Guide](#pattern-selection-guide) | ~588 | Which pattern for which behavior |

## Pattern Catalog for Embedded C Testing

### 1. Multi-State Sequences

Testing components that transition through multiple states:

```cpp
/*!
 * @rst
 * .. test:: StateMachine.TransitionsThrough_InitReadyActive
 *    :id: TS_SM-001
 *    :tests: SWDD_SM-100
 * 
 * State machine progresses through initialization sequence correctly.
 * @endrst
 */
TEST(StateMachine, TransitionsThrough_InitReadyActive)
{
    CREATE_MOCK(mymock);
    InSequence seq;

    // ARRANGE: initial state check
    EXPECT_EQ(StateMachine_GetState(), STATE_INIT);

    // ARRANGE step 1 + ACT step 1
    EXPECT_CALL(mymock, CheckHardware()).WillOnce(Return(OK));
    StateMachine_Process();

    // ASSERT step 1
    EXPECT_EQ(StateMachine_GetState(), STATE_READY);

    // ARRANGE step 2 + ACT step 2
    EXPECT_CALL(mymock, StartOperation()).WillOnce(Return(OK));
    StateMachine_Start();

    // ASSERT step 2
    EXPECT_EQ(StateMachine_GetState(), STATE_ACTIVE);
}
```

### 2. Accumulator/Counter Behavior

Testing components that accumulate values over time:

```cpp
/*!
 * @rst
 * .. test:: Counter.Accumulates_AcrossMultipleCalls
 *    :id: TS_CNT-002
 *    :tests: SWDD_CNT-200
 * 
 * Counter increments correctly with repeated inputs.
 * @endrst
 */
TEST(Counter, Accumulates_AcrossMultipleCalls)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    Counter_Reset();
    EXPECT_EQ(Counter_GetValue(), 0);

    // ACT
    Counter_Increment();
    Counter_Increment();
    Counter_Increment();

    // ASSERT
    EXPECT_EQ(Counter_GetValue(), 3);
}

/*!
 * @rst
 * .. test:: Counter.RollsOver_AtMaxValue
 *    :id: TS_CNT-003
 *    :tests: SWDD_CNT-201
 * 
 * Counter wraps to zero when exceeding maximum value.
 * @endrst
 */
TEST(Counter, RollsOver_AtMaxValue)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    Counter_SetValue(COUNTER_MAX);

    // ACT
    Counter_Increment();

    // ASSERT
    EXPECT_EQ(Counter_GetValue(), 0);
}
```

### 3. Hysteresis/Threshold Behavior

Testing components with different thresholds for rising/falling:

```cpp
/*!
 * @rst
 * .. test:: Thermostat.TurnsOn_WhenBelowLowerThreshold
 *    :id: TS_THERM-004
 *    :tests: SWDD_THERM-300
 * 
 * Heating activates when temperature drops below 18C.
 * @endrst
 */
TEST(Thermostat, TurnsOn_WhenBelowLowerThreshold)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    EXPECT_CALL(mymock, ReadTemperature())
        .WillOnce(Return(17));  // Below 18C
    EXPECT_CALL(mymock, SetHeater(true)).Times(1);

    // ACT
    Thermostat_Process();
}

/*!
 * @rst
 * .. test:: Thermostat.TurnsOff_WhenAboveUpperThreshold
 *    :id: TS_THERM-005
 *    :tests: SWDD_THERM-300
 * 
 * Heating deactivates when temperature rises above 22C.
 * @endrst
 */
TEST(Thermostat, TurnsOff_WhenAboveUpperThreshold)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    Thermostat_SetHeating(true);
    EXPECT_CALL(mymock, ReadTemperature())
        .WillOnce(Return(23));  // Above 22C
    EXPECT_CALL(mymock, SetHeater(false)).Times(1);

    // ACT
    Thermostat_Process();
}

/*!
 * @rst
 * .. test:: Thermostat.RemainsOn_InHysteresisRange
 *    :id: TS_THERM-006
 *    :tests: SWDD_THERM-301
 * 
 * Heating stays active between 18-22C to prevent oscillation.
 * @endrst
 */
TEST(Thermostat, RemainsOn_InHysteresisRange)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    Thermostat_SetHeating(true);
    EXPECT_CALL(mymock, ReadTemperature())
        .WillOnce(Return(20));  // Between 18C and 22C
    EXPECT_CALL(mymock, SetHeater(_)).Times(0);

    // ACT
    Thermostat_Process();
}
```

### 4. Rate Limiting/Throttling

Testing components that limit action frequency:

```cpp
/*!
 * @rst
 * .. test:: RateLimiter.AllowsFirstCall_Immediately
 *    :id: TS_RATE-007
 *    :tests: SWDD_RATE-400
 * 
 * First call to rate-limited function succeeds without delay.
 * @endrst
 */
TEST(RateLimiter, AllowsFirstCall_Immediately)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    RateLimiter_Reset();

    // ACT
    bool allowed = RateLimiter_CheckAllowed();

    // ASSERT
    EXPECT_TRUE(allowed);
}

/*!
 * @rst
 * .. test:: RateLimiter.BlocksSecondCall_Within100ms
 *    :id: TS_RATE-008
 *    :tests: SWDD_RATE-401
 * 
 * Rapid successive calls blocked until minimum interval elapses.
 * @endrst
 */
TEST(RateLimiter, BlocksSecondCall_Within100ms)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    RateLimiter_CheckAllowed();
    for (int tick = 0; tick < 99; tick++)
    {
        RateLimiter_Tick1ms();
    }

    // ACT + ASSERT
    EXPECT_FALSE(RateLimiter_CheckAllowed());
}

/*!
 * @rst
 * .. test:: RateLimiter.AllowsCall_After100ms
 *    :id: TS_RATE-009
 *    :tests: SWDD_RATE-401
 * 
 * Call allowed after minimum interval has passed.
 * @endrst
 */
TEST(RateLimiter, AllowsCall_After100ms)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    RateLimiter_CheckAllowed();
    for (int tick = 0; tick < 100; tick++)
    {
        RateLimiter_Tick1ms();
    }

    // ACT
    bool allowed = RateLimiter_CheckAllowed();

    // ASSERT
    EXPECT_TRUE(allowed);
}
```

### 5. Moving Average/Filtering

Testing signal processing or filtering logic:

```cpp
/*!
 * @rst
 * .. test:: MovingAverage.CalculatesAverage_OfLastNSamples
 *    :id: TS_AVG-010
 *    :tests: SWDD_AVG-500
 * 
 * Moving average correctly computed from last 4 samples.
 * @endrst
 */
TEST(MovingAverage, CalculatesAverage_OfLastNSamples)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    MovingAverage_AddSample(10);
    MovingAverage_AddSample(20);
    MovingAverage_AddSample(30);
    MovingAverage_AddSample(40);

    // ACT
    uint16_t average = MovingAverage_GetValue();

    // ASSERT: Average is (10+20+30+40)/4 = 25
    EXPECT_EQ(average, 25);
}

/*!
 * @rst
 * .. test:: MovingAverage.DiscardsOldestSample_WhenWindowFull
 *    :id: TS_AVG-011
 *    :tests: SWDD_AVG-501
 * 
 * Sliding window discards oldest when new sample added.
 * @endrst
 */
TEST(MovingAverage, DiscardsOldestSample_WhenWindowFull)
{
    CREATE_MOCK(mymock);
    const uint8_t capacity = RingBuffer_GetCapacity();

    // ARRANGE: Window full with [10, 20, 30, 40]
    MovingAverage_AddSample(10);
    MovingAverage_AddSample(20);
    MovingAverage_AddSample(30);
    MovingAverage_AddSample(40);

    // ACT
    MovingAverage_AddSample(50);

    // ASSERT: Average is (20+30+40+50)/4 = 35 (10 discarded)
    EXPECT_EQ(MovingAverage_GetValue(), 35);
}
```

### 6. Retry Logic

Testing components with retry mechanisms:

```cpp
/*!
 * @rst
 * .. test:: Communication.RetriesOnFailure_UpToThreeTimes
 *    :id: TS_COMM-012
 *    :tests: SWDD_COMM-600
 * 
 * Failed transmissions retried up to 3 times before giving up.
 * @endrst
 */
TEST(Communication, RetriesOnFailure_UpToThreeTimes)
{
    CREATE_MOCK(mymock);
    InSequence seq;

    // ARRANGE: All 4 attempts fail
    EXPECT_CALL(mymock, TransmitData(_))
        .WillOnce(Return(ERROR))    // Attempt 1 fails
        .WillOnce(Return(ERROR))    // Attempt 2 fails
        .WillOnce(Return(ERROR))    // Attempt 3 fails
        .WillOnce(Return(ERROR));   // Attempt 4 fails

    // ACT
    status_t result = Communication_Send(data);

    // ASSERT
    EXPECT_EQ(result, ERROR);
}

/*!
 * @rst
 * .. test:: Communication.SucceedsImmediately_OnSecondRetry
 *    :id: TS_COMM-013
 *    :tests: SWDD_COMM-600
 * 
 * Successful retry stops further attempts.
 * @endrst
 */
TEST(Communication, SucceedsImmediately_OnSecondRetry)
{
    CREATE_MOCK(mymock);
    InSequence seq;

    // ARRANGE: First attempt fails, second succeeds
    EXPECT_CALL(mymock, TransmitData(_))
        .WillOnce(Return(ERROR))    // Attempt 1 fails
        .WillOnce(Return(OK));      // Attempt 2 succeeds

    // ACT
    status_t result = Communication_Send(data);

    // ASSERT
    EXPECT_EQ(result, OK);
}
```

### 7. Circular Buffers

Testing ring buffer or FIFO behavior:

```cpp
/*!
 * @rst
 * .. test:: RingBuffer.StoresAndRetrievesInOrder
 *    :id: TS_BUF-014
 *    :tests: SWDD_BUF-700
 * 
 * FIFO ordering maintained: first in, first out.
 * @endrst
 */
TEST(RingBuffer, StoresAndRetrievesInOrder)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    RingBuffer_Push(10);
    RingBuffer_Push(20);
    RingBuffer_Push(30);

    // ACT + ASSERT: Retrieved in same order
    EXPECT_EQ(RingBuffer_Pop(), 10);
    EXPECT_EQ(RingBuffer_Pop(), 20);
    EXPECT_EQ(RingBuffer_Pop(), 30);
}

/*!
 * @rst
 * .. test:: RingBuffer.OverwritesOldest_WhenFull
 *    :id: TS_BUF-015
 *    :tests: SWDD_BUF-701
 * 
 * Oldest data overwritten when buffer capacity exceeded.
 * @endrst
 */
TEST(RingBuffer, OverwritesOldest_WhenFull)
{
    CREATE_MOCK(mymock);
    const uint8_t capacity = RingBuffer_GetCapacity();

    // ARRANGE: Buffer filled to capacity
    for (uint8_t i = 0; i < capacity; i++)
    {
        RingBuffer_Push(i);
    }

    // ACT
    RingBuffer_Push(99);

    // ASSERT: Oldest value (0) is lost, newest values retained
    EXPECT_EQ(RingBuffer_Pop(), 1);   // 0 was overwritten

    for (uint8_t i = 2; i < capacity; i++)
    {
        RingBuffer_Pop();
    }
    EXPECT_EQ(RingBuffer_Pop(), 99);  // Newest value present
}
```

### 8. Watchdog/Timeout Behavior

Testing components that detect stuck states:

```cpp
/*!
 * @rst
 * .. test:: Watchdog.TriggersReset_AfterTimeout
 *    :id: TS_WDG-016
 *    :tests: SWDD_WDG-800
 * 
 * System reset triggered if watchdog not kicked within timeout period.
 * @endrst
 */
TEST(Watchdog, TriggersReset_AfterTimeout)
{
    CREATE_MOCK(mymock);
    const uint32_t timeout_ms = 1000;

    // ARRANGE
    EXPECT_CALL(mymock, TriggerReset()).Times(1);
    Watchdog_Start(timeout_ms);

    // ACT: Timeout period elapses
    for (uint32_t tick = 0; tick < timeout_ms; tick++)
    {
        Watchdog_Tick1ms();
    }
    Watchdog_Process();
}

/*!
 * @rst
 * .. test:: Watchdog.ResetsTimer_WhenKicked
 *    :id: TS_WDG-017
 *    :tests: SWDD_WDG-801
 * 
 * Periodic watchdog kicks prevent timeout.
 * @endrst
 */
TEST(Watchdog, ResetsTimer_WhenKicked)
{
    CREATE_MOCK(mymock);
    const uint32_t timeout_ms = 1000;

    // ARRANGE
    EXPECT_CALL(mymock, TriggerReset()).Times(0);
    Watchdog_Start(timeout_ms);

    // ACT: Kick every 500ms for 2 seconds
    for (int cycle = 0; cycle < 4; cycle++)
    {
        for (int tick = 0; tick < 500; tick++)
        {
            Watchdog_Tick1ms();
        }
        Watchdog_Kick();
    }
}
```

### 9. Multi-Phase Initialization

Testing components with complex startup sequences:

```cpp
/*!
 * @rst
 * .. test:: Initialization.CompletesAllPhases_InOrder
 *    :id: TS_INIT-018
 *    :tests: SWDD_INIT-900
 * 
 * Multi-phase initialization completes in correct sequence.
 * @endrst
 */
TEST(Initialization, CompletesAllPhases_InOrder)
{
    CREATE_MOCK(mymock);
    InSequence seq;

    // ARRANGE
    EXPECT_CALL(mymock, Phase1_HardwareReset()).Times(1);
    EXPECT_CALL(mymock, Phase2_ClockSetup()).Times(1);
    EXPECT_CALL(mymock, Phase3_MemoryInit()).Times(1);
    EXPECT_CALL(mymock, Phase4_PeripheralInit()).Times(1);
    EXPECT_CALL(mymock, Phase5_SoftwareInit()).Times(1);

    // ACT
    status_t result = System_Initialize();

    // ASSERT
    EXPECT_EQ(result, STATUS_OK);
}

/*!
 * @rst
 * .. test:: Initialization.AbortsEarly_OnPhaseFailure
 *    :id: TS_INIT-019
 *    :tests: SWDD_INIT-901
 * 
 * Initialization stops at first failed phase without proceeding.
 * @endrst
 */
TEST(Initialization, AbortsEarly_OnPhaseFailure)
{
    CREATE_MOCK(mymock);
    InSequence seq;

    // ARRANGE: Phase 2 fails, later phases must not run
    EXPECT_CALL(mymock, Phase1_HardwareReset())
        .WillOnce(Return(STATUS_OK));
    EXPECT_CALL(mymock, Phase2_ClockSetup())
        .WillOnce(Return(STATUS_ERROR));
    EXPECT_CALL(mymock, Phase3_MemoryInit()).Times(0);
    EXPECT_CALL(mymock, Phase4_PeripheralInit()).Times(0);

    // ACT
    status_t result = System_Initialize();

    // ASSERT
    EXPECT_EQ(result, STATUS_ERROR);
}
```

### 10. Event Coalescing

Testing components that merge rapid events:

```cpp
/*!
 * @rst
 * .. test:: EventHandler.Coalesces_RapidUpdates
 *    :id: TS_EVT-020
 *    :tests: SWDD_EVT-1000
 * 
 * Multiple rapid value updates coalesced into single notification.
 * @endrst
 */
TEST(EventHandler, Coalesces_RapidUpdates)
{
    CREATE_MOCK(mymock);

    // ARRANGE
    EXPECT_CALL(mymock, NotifyValueChanged(40)).Times(1);
    EventHandler_Update(10);
    EventHandler_Update(20);
    EventHandler_Update(30);
    EventHandler_Update(40);

    // ACT
    EventHandler_Process();
}
```

## Pattern Selection Guide

| Behavior Type                     | Pattern to Use             |
|-----------------------------------|----------------------------|
| Time-dependent (debounce, timers) | Temporal Behavior          |
| State transitions                 | Multi-State Sequences      |
| Ordered operations                | Sequential State Machines  |
| Threshold with deadband           | Hysteresis/Threshold       |
| Limit action frequency            | Rate Limiting              |
| Signal smoothing                  | Moving Average             |
| Transient failures                | Retry Logic                |
| Queue/FIFO                        | Circular Buffers           |
| Stuck detection                   | Watchdog/Timeout           |
| Startup sequence                  | Multi-Phase Initialization |
| Merge rapid events                | Event Coalescing           |
| Value accumulation                | Accumulator/Counter        |
| Same logic, different data        | **Parameterized (TEST_P)** |
| Boundary values (below/at/above)  | **Parameterized (TEST_P)** |
| Multiple error codes, same result | **Parameterized (TEST_P)** |
| Input→output mapping              | **Parameterized (TEST_P)** |
| Multi-platform RTE symbol names   | **RTE Platform Aliasing**  |

**See**: [parameterized-tests.md](parameterized-tests.md) for `TEST_P()` templates and examples
