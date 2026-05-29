# Clean Code Checklist for Embedded C

Based on "Clean Code" by Robert C. Martin, adapted for embedded C development.
Focus on readability, maintainability, and reducing cognitive load.

## Naming

- [ ] **Names reveal intent**: Variable/function names describe purpose
  - ❌ `int d;` → ✅ `int elapsed_days;`
  - ❌ `void proc(uint8_t *p);` → ✅ `void process_message(uint8_t *buffer);`

- [ ] **No disinformation**: Names don't mislead about type or purpose
  - ❌ `accountList` when it's not a list
  - ❌ `hp, aix, sco` (look like OS names)

- [ ] **Pronounceable names**: Can discuss code verbally
  - ❌ `genymdhms` → ✅ `generation_timestamp`

- [ ] **Searchable names**: Important values have named constants
  - ❌ `for (i = 0; i < 7; i++)` → ✅ `for (i = 0; i < DAYS_PER_WEEK; i++)`

- [ ] **No encodings**: No Hungarian notation, type prefixes
  - ❌ `uint8_t u8Counter;` → ✅ `uint8_t counter;`
  - Exception: Project convention may require prefixes (e.g., `App_` for modules)

- [ ] **Avoid mental mapping**: No single-letter names except loop indices
  - ❌ `int r;` → ✅ `int result;`

## Functions

- [ ] **Small functions**: Functions do one thing
  - Target: ≤ 20 lines
  - If description needs "and", function does too much

- [ ] **One level of abstraction**: All statements at same level
  - Don't mix high-level logic with low-level bit manipulation

- [ ] **Descriptive names**: Function name describes what it does
  - ✅ `validate_message_checksum()`
  - ❌ `check()` or `do_it()`

- [ ] **Few arguments**: Ideally 0-2, at most 3
  - More than 3 → consider struct parameter
  - Flag arguments (bool) often mean function does two things

- [ ] **No side effects**: Functions don't do hidden things
  - If function is `get_value()`, it shouldn't also modify state

- [ ] **Command-Query Separation**: Functions either do or ask, not both
  - ❌ `if (set_value(x))` — unclear if checking success or old value

- [ ] **Prefer exceptions to error codes**: Return early on errors
  - In C: Return status enum, check at call site

- [ ] **DRY - Don't Repeat Yourself**: No duplicated code
  - If same logic appears twice, extract to function

## Comments

- [ ] **Comments don't compensate for bad code**: Clean code needs few comments
  - If you need a comment, first try to make the code clearer

- [ ] **Explain intent, not mechanism**: Comment why, not what
  - ❌ `i++; /* increment i */`
  - ✅ `/* Retry connection up to 3 times per protocol spec */`

- [ ] **No commented-out code**: Delete it, version control remembers
  - Exception: Temporary during development (remove before commit)

- [ ] **No redundant comments**: Don't repeat what code says
  - ❌ `int day_of_month; /* the day of the month */`

- [ ] **No journal comments**: No change logs in source files
  - Use version control for history

- [ ] **TODO comments resolved**: No stale TODOs in production code
  - If TODO must stay, link to issue tracker

## Formatting

- [ ] **Consistent formatting**: Follow project style guide
  - Consistent indentation, brace placement, spacing

- [ ] **Vertical openness**: Separate concepts with blank lines
  - Group related statements, separate different concerns

- [ ] **Vertical density**: Related code stays together
  - Declare variables close to their usage

- [ ] **Horizontal alignment**: Don't align assignments/declarations
  - Makes diffs harder to read

- [ ] **Line length**: Keep lines readable (80-120 characters)
  - Long lines indicate complex expressions

## Error Handling

- [ ] **Don't return NULL**: Return empty value or status code
  - Caller can forget to check NULL

- [ ] **Don't pass NULL**: Validate inputs, fail fast
  - Use assertions in debug builds

- [ ] **Use status codes consistently**: Define error enums

  ```c
  typedef enum {
      STATUS_OK = 0,
      STATUS_INVALID_PARAM,
      STATUS_TIMEOUT,
      STATUS_ERROR
  } status_t;
  ```

- [ ] **Wrap third-party calls**: Isolate external dependencies
  - Easier to mock for testing

## Data Structures

- [ ] **Data/behavior separation**: Structs contain data, not behavior
  - Functions operate on structs, not embedded in them (no OOP in C)

- [ ] **Hide internals**: Don't expose structure details unnecessarily
  - Use opaque pointers where appropriate

- [ ] **Prefer composition**: Build complex structures from simple ones

## Tests (if applicable)

- [ ] **One assert per test**: Tests check one thing
  - Multiple asserts indicate test does too much

- [ ] **Readable tests**: Test code is documentation
  - Use BDD-style: Given/When/Then

- [ ] **Fast tests**: Tests run quickly
  - Mock external dependencies

- [ ] **Independent tests**: Tests don't depend on each other
  - No shared state between tests

## Overall Assessment

| Category        | Status | Notes |
|-----------------|--------|-------|
| Naming          | ⬜     |       |
| Functions       | ⬜     |       |
| Comments        | ⬜     |       |
| Formatting      | ⬜     |       |
| Error Handling  | ⬜     |       |
| Data Structures | ⬜     |       |
