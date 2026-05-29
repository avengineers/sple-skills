# Defensive Programming Checklist

Techniques to make C code robust against errors, unexpected inputs, and failures.
Focus on preventing problems before they occur and failing safely when they do.

## Input Validation

- [ ] **All public function inputs validated**

  ```c
  status_t process_data(const uint8_t *buffer, size_t length) {
      if (buffer == NULL) {
          return STATUS_INVALID_PARAM;
      }
      if (length == 0U || length > MAX_BUFFER_SIZE) {
          return STATUS_INVALID_PARAM;
      }
      /* proceed with valid inputs */
  }
  ```

- [ ] **Array indices bounds-checked**

  ```c
  if (index < ARRAY_SIZE) {
      value = array[index];
  }
  ```

- [ ] **String lengths verified before operations**
  - Use `strncpy()` not `strcpy()`
  - Use `snprintf()` not `sprintf()`

- [ ] **Numeric ranges checked before use**
  - Division: Check divisor ≠ 0
  - Shift: Check shift amount < bit width
  - Cast: Check value fits in target type

- [ ] **Enum values validated**

  ```c
  switch (state) {
      case STATE_IDLE:
      case STATE_RUNNING:
      case STATE_ERROR:
          /* handle known states */
          break;
      default:
          /* should never reach here */
          handle_invalid_state(state);
          break;
  }
  ```

## Pointer Safety

- [ ] **NULL checks before dereference**

  ```c
  if (ptr != NULL) {
      *ptr = value;
  }
  ```

- [ ] **Pointers set to NULL after free**

  ```c
  free(ptr);
  ptr = NULL;  /* prevent double-free or use-after-free */
  ```

- [ ] **No dangling pointers to automatic variables**
  - Don't return pointer to local variable
  - Don't store pointer to local in global

- [ ] **Pointer arithmetic within bounds**
  - Only on actual arrays
  - Result within array or one-past-end

## Resource Management

- [ ] **Resources acquired and released in pairs**
  - File: open → close
  - Memory: allocate → free
  - Lock: acquire → release
  - Hardware: init → deinit

- [ ] **Resource cleanup on all paths**
  - Including error paths
  - Consider cleanup labels or goto-for-cleanup pattern

- [ ] **No resource leaks in error handling**

  ```c
  status_t function(void) {
      resource_t *res = acquire_resource();
      if (res == NULL) {
          return STATUS_ERROR;
      }

      status_t result = do_work(res);
      if (result != STATUS_OK) {
          release_resource(res);  /* don't leak! */
          return result;
      }

      release_resource(res);
      return STATUS_OK;
  }
  ```

## Assertions and Contracts

- [ ] **Assertions document assumptions**

  ```c
  void process_calibrated_value(int16_t value) {
      /* Precondition: value has been calibrated and is in valid range */
      assert(value >= MIN_CALIBRATED && value <= MAX_CALIBRATED);
      /* ... */
  }
  ```

- [ ] **Assertions disabled in production**
  - Use `NDEBUG` to disable assert()
  - Or use custom assertion macro

- [ ] **No side effects in assertions**

  ```c
  /* WRONG: side effect lost when assertions disabled */
  assert(init_hardware() == SUCCESS);

  /* CORRECT: separate action from check */
  status_t result = init_hardware();
  assert(result == SUCCESS);
  ```

- [ ] **Critical checks not only in assertions**
  - Assertions can be disabled
  - Safety checks need runtime verification

## State Management

- [ ] **State machines have defined initial state**

  ```c
  typedef struct {
      state_t state;
      /* ... */
  } module_context_t;

  void module_init(module_context_t *ctx) {
      ctx->state = STATE_IDLE;  /* defined initial state */
  }
  ```

- [ ] **Invalid state transitions rejected**

  ```c
  status_t set_state(module_context_t *ctx, state_t new_state) {
      if (!is_valid_transition(ctx->state, new_state)) {
          return STATUS_INVALID_TRANSITION;
      }
      ctx->state = new_state;
      return STATUS_OK;
  }
  ```

- [ ] **State consistency checked periodically**
  - Watchdog checks
  - Health monitoring

## Error Handling

- [ ] **All function returns checked**

  ```c
  status_t result = do_something();
  if (result != STATUS_OK) {
      handle_error(result);
      return result;
  }
  ```

- [ ] **Error paths tested**
  - Unit tests cover error conditions
  - Integration tests include failure scenarios

- [ ] **Fail-safe defaults**
  - Unknown state → safe state
  - Communication loss → safe action
  - Sensor failure → fallback value or shutdown

- [ ] **No silent failures**
  - Log errors
  - Set error flags
  - Return status codes

## Concurrency / Interrupt Safety

- [ ] **Shared data protected**
  - Critical sections for interrupt-shared data
  - Atomic operations where appropriate

- [ ] **Volatile for hardware/interrupt variables**

  ```c
  volatile uint8_t interrupt_flag = 0U;
  ```

- [ ] **No race conditions in flag checks**

  ```c
  /* WRONG: TOCTOU race */
  if (data_ready) {
      process(data);  /* data_ready could change before this */
  }

  /* BETTER: atomic check-and-process */
  disable_interrupts();
  if (data_ready) {
      data_ready = false;
      enable_interrupts();
      process(data);
  } else {
      enable_interrupts();
  }
  ```

## Compile-Time Defenses

- [ ] **Static assertions for assumptions**

  ```c
  _Static_assert(sizeof(uint32_t) == 4, "uint32_t must be 4 bytes");
  _Static_assert(MAX_BUFFER_SIZE <= UINT16_MAX, "Buffer size exceeds limit");
  ```

- [ ] **Const correctness enforced**
  - Input parameters const where possible
  - Const for lookup tables

- [ ] **Compiler warnings enabled and addressed**
  - `-Wall -Wextra -Werror`
  - No ignored warnings

## Overall Assessment

| Category            | Status | Notes |
|---------------------|--------|-------|
| Input Validation    | ⬜     |       |
| Pointer Safety      | ⬜     |       |
| Resource Management | ⬜     |       |
| Assertions          | ⬜     |       |
| State Management    | ⬜     |       |
| Error Handling      | ⬜     |       |
| Concurrency         | ⬜     |       |
| Compile-Time        | ⬜     |       |
