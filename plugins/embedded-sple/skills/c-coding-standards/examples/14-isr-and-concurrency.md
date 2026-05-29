# 14 — ISR & Concurrency Examples (BARR‑C:2018‑Aligned Patterns)

**Purpose:** Provide practical, copy‑pasteable patterns for safe interaction between interrupt context and foreground (bare metal) or tasks/threads (RTOS).
**Use this document when:** implementing ISRs, shared flags/counters, ring buffers, event signaling, critical sections, or when you suspect race conditions / “glitches” at higher optimization levels.

> **Key idea:** `volatile` prevents compiler caching/reordering of accesses, but it **does not** make multi‑step operations atomic or race‑free. You still need safe access patterns and/or critical sections.

---

## 0) Quick terminology

- **ISR context:** runs asynchronously; must be short, deterministic, and non-blocking.
- **Foreground / “straight-line” code:** main loop or normal functions called from main/task.
- **Task/thread context:** RTOS scheduled; can block; runs concurrently with other tasks and ISRs.
- **Critical section:** region protected from concurrent modification (e.g., interrupts disabled, scheduler locked, mutex).

---

## 1) Golden Rules (Review triggers)

### 1.1 ISR should do the minimum

**ISR responsibilities:**
- read status (if needed)
- capture minimal data
- clear/acknowledge interrupt source
- signal deferred work

**Avoid in ISR:**

- dynamic allocation
- long loops / heavy computations
- blocking calls
- calls into non-ISR-safe drivers/OS APIs

### 1.2 Shared state must be explicit

- Name ISR-shared objects clearly (globals are especially suspicious).
- Use `volatile` where required **and** ensure atomicity.

### 1.3 Never rely on “it seems to work”

- Race bugs often show up only with:
  - higher optimization
  - different clock speed
  - different interrupt rate
  - different timing in release builds

---

## 2) Pattern: ISR sets a flag, foreground clears it safely

### Use when

- ISR indicates “something happened” (edge, timer tick, RX ready)
- Foreground performs the heavier work

### Example

```c
/* Shared flag set by ISR, cleared by foreground. */
static volatile uint8_t g_rx_ready = 0u;

ISR_ATTR static void uart_rx_isr (void)
{
    /* Capture/clear hardware condition as required. */
    g_rx_ready = 1u;

    /* Ack interrupt at HW (platform specific). */
    *p_uart_status = UART_INT_ACK_MASK;
}

void uart_poll (void)
{
    if (0u != g_rx_ready)
    {
        enter_critical();
        g_rx_ready = 0u;
        exit_critical();

        uart_process_rx();
    }
}
```

### Notes

- The critical section is short—just long enough to make the “clear” atomic relative to ISR.
- If `g_rx_ready` is a single byte and your MCU guarantees atomic byte writes, the critical section can be optional—but keep it if unsure or if future ports are likely.

---

## 3) Pattern: ISR increments a counter, foreground reads it safely

### Use when

- ISR generates a tick count, event count, or overflow counter

### Example (safe read)

```c
static volatile uint32_t g_tick_count = 0u;

ISR_ATTR static void timer_isr (void)
{
    g_tick_count++;
    *p_timer_status = TIMER_INT_ACK_MASK;
}

uint32_t timer_get_ticks (void)
{
    uint32_t ticks;

    enter_critical();
    ticks = g_tick_count;
    exit_critical();

    return ticks;
}
```

### Why the critical section?

- On some targets, 32-bit reads/writes are not atomic (e.g., 8/16-bit MCUs), which can produce torn reads.

### Optional optimization: “double read” technique (no critical section)

Use only if:

- ISR only increments (monotonic)
- target guarantees aligned reads are consistent enough for this strategy

```c
uint32_t timer_get_ticks_relaxed (void)
{
    uint32_t a;
    uint32_t b;

    do
    {
        a = g_tick_count;
        b = g_tick_count;
    } while (a != b);

    return a;
}
```

**WARNING:** This can still fail if the ISR updates more frequently than you can get two stable reads. Prefer critical sections unless you have strong platform guarantees.

---

## 4) Pattern: ISR writes data into a ring buffer, foreground reads it

### Use when

- UART RX, SPI RX, ADC samples, etc.
- You need to decouple ISR from processing

### Minimal ring buffer example

```c
#define RX_BUF_SIZE  (128u)

static volatile uint16_t g_rx_head = 0u;
static volatile uint16_t g_rx_tail = 0u;
static uint8_t           g_rx_buf[RX_BUF_SIZE];

static uint16_t next_index (uint16_t idx)
{
    return (uint16_t)((idx + 1u) % RX_BUF_SIZE);
}

ISR_ATTR static void uart_rx_isr (void)
{
    uint16_t head = g_rx_head;
    uint16_t next = next_index(head);

    /* Read byte from HW early. */
    uint8_t byte = *p_uart_data;

    if (next != g_rx_tail)
    {
        g_rx_buf[head] = byte;
        g_rx_head      = next;
    }
    else
    {
        /* NOTE: RX overflow. Optionally set an overflow flag/counter. */
    }

    *p_uart_status = UART_INT_ACK_MASK;
}

bool uart_try_get_byte (uint8_t * p_byte)
{
    uint16_t tail;

    if (NULL == p_byte)
    {
        return false;
    }

    enter_critical();
    tail = g_rx_tail;

    if (tail == g_rx_head)
    {
        exit_critical();
        return false; /* empty */
    }

    *p_byte   = g_rx_buf[tail];
    g_rx_tail = next_index(tail);
    exit_critical();

    return true;
}
```

### Notes / pitfalls

- Keep indices and buffer operations consistent and documented.
- Consider atomicity of index reads/writes and size type choices.
- If `RX_BUF_SIZE` is power-of-two, you can optimize modulo with masking:
  - `idx = (idx + 1u) & (RX_BUF_SIZE - 1u)`
  - **Only** if size is power-of-two and documented.

---

## 5) Pattern: Event queue / mailbox signal from ISR to task (RTOS)

### Use when

- ISR should wake a task to process data
- Your RTOS provides ISR-safe “FromISR” APIs

### Guideline

- Use only RTOS APIs that are explicitly ISR-safe.
- If your RTOS requires a special yield/pend call after sending from ISR, follow it.

### Generic sketch (pseudo-RTOS)

```c
ISR_ATTR static void uart_rx_isr (void)
{
    uint8_t byte = *p_uart_data;

    /* Put into ISR-safe queue (RTOS-specific). */
    os_queue_send_from_isr(uart_rx_queue, &byte);

    *p_uart_status = UART_INT_ACK_MASK;
    os_yield_from_isr(); /* if required by RTOS */
}

void uart_rx_thread (void * p_arg)
{
    uint8_t byte;

    (void)p_arg;

    for (;;)
    {
        os_queue_receive(uart_rx_queue, &byte, OS_WAIT_FOREVER);
        uart_process_byte(byte);
    }
}
```

### Notes

- Keep task entry function naming consistent (`*_thread` / `*_task`).
- Avoid sharing raw globals between ISR and task when the RTOS queue suffices.

---

## 6) Pattern: Multi-field shared state (copy-then-process)

### Use when

- ISR updates multiple related fields (e.g., timestamp + value)
- Foreground needs a consistent snapshot

### Example: snapshot under critical section

```c
typedef struct
{
    uint32_t timestamp;
    uint16_t sample;
    uint8_t  b_valid;
} sample_snapshot_t;

static volatile sample_snapshot_t g_latest = { 0u, 0u, 0u };

ISR_ATTR static void adc_isr (void)
{
    g_latest.timestamp = timer_get_hw_ticks();
    g_latest.sample    = *p_adc_data;
    g_latest.b_valid   = 1u;

    *p_adc_status = ADC_INT_ACK_MASK;
}

bool adc_get_latest (sample_snapshot_t * p_out)
{
    if (NULL == p_out)
    {
        return false;
    }

    enter_critical();
    *p_out = (sample_snapshot_t)g_latest; /* copy snapshot */
    exit_critical();

    return (0u != p_out->b_valid);
}
```

### Notes

- Snapshot copy ensures consistency across multiple fields.
- If your toolchain warns about casting volatile to non-volatile, you can copy field-by-field inside the critical section.

---

## 7) Pattern: Protect read-modify-write (RMW) sequences

### Use when

- Foreground does `x = x | mask` or `x++` on shared state
- ISR might modify the same variable concurrently

### Example

```c
static volatile uint32_t g_flags = 0u;

void set_flag (uint32_t mask)
{
    enter_critical();
    g_flags |= mask;
    exit_critical();
}

ISR_ATTR static void event_isr (void)
{
    g_flags |= EVENT_ISR_MASK; /* also an RMW */
}
```

### Warning

- RMW in both contexts can still collide.
- Prefer: ISR sets a dedicated flag, foreground consolidates; or use atomic primitives if available.

---

## 8) Safe `volatile` usage: what it does and does not do

### `volatile` DOES

- Forces the compiler to actually perform reads/writes as written.
- Prevents some optimizations that remove or cache accesses.

### `volatile` DOES NOT

- Make an operation atomic.
- Provide mutual exclusion.
- Prevent races between ISR and foreground, or between tasks.

**Rule of thumb:** If you need to update multiple related fields, or do an RMW, you likely need a critical section or an atomic primitive.

---

## 9) Default ISR handler pattern (unexpected vectors)

### Use when

- You want deterministic behavior for unexpected interrupts

### Example

```c
ISR_ATTR static void default_isr (void)
{
    /* WARNING: Unexpected interrupt. Investigate vector table configuration. */
    assert(false);

    for (;;)
    {
        /* Halt or enter safe state (project policy). */
    }
}
```

---

## 10) Review checklist (ISR & concurrency)

### Interrupt handlers

- [ ] ISR declared with correct compiler attribute/pragma/keyword
- [ ] Name ends with `_isr`
- [ ] ISR is minimal; no blocking; no heavy work
- [ ] Interrupt source is acknowledged/cleared correctly
- [ ] Default handler exists for unexpected vectors (policy dependent)

### Shared state

- [ ] All ISR/task shared objects are clearly identified (naming + comments)
- [ ] `volatile` applied where required
- [ ] Atomicity is guaranteed (critical sections for multi-byte/RMW or unknown targets)
- [ ] Snapshot pattern used for multi-field shared state
- [ ] No hidden side effects in conditions; clear constant-on-left comparisons

### Task/threads

- [ ] Entry points named `_thread/_task/_process`
- [ ] Infinite loops use `for (;;)`
- [ ] RTOS “FromISR” APIs used where required; no non-ISR-safe calls

---

## 11) Minimal deviation template (if required)

Use this when platform constraints force a non-ideal pattern:

```c
/* DEVIATION (BARR-C X.Y):
 * Reason:
 * Risk:
 * Mitigation:
 * Approved-by:
 * Date:
 */
```
