# Integration Test Checklists

## Pre-Test Development Checklist

Before writing integration test, verify:

- [ ] Unit tests exist for all components involved
- [ ] Component interfaces are well-defined
- [ ] Components are properly initialized in SetUp()
- [ ] Only HAL/external interfaces are mocked
- [ ] Test uses BDD structure (Given-When-Then)
- [ ] Test focuses on one integration scenario
- [ ] Test has proper RST traceability
- [ ] Test name describes the scenario
- [ ] Cleanup occurs in TearDown() if needed

## Integration Test Review Checklist

Before code review:

- [ ] Test follows BDD Given-When-Then pattern
- [ ] Test name clearly describes scenario being tested
- [ ] Only necessary dependencies are mocked (HAL/hardware only)
- [ ] Setup and teardown are balanced
- [ ] Test is deterministic (no race conditions)
- [ ] Test has appropriate timeout values
- [ ] Error conditions are properly handled
- [ ] Test has RST traceability link

## Variant Integration Test Checklist

Before merging changes:

- [ ] Integration tests pass in primary variant (e.g., Disco)
- [ ] Integration tests pass in minimal variant (e.g., Base)
- [ ] Integration tests pass in feature-rich variant (e.g., Spa with auto-off)
- [ ] Variant-conditional tests properly guarded with `#ifdef`
- [ ] Pytest variant tests (`.\build.ps1 -selftests`) all pass
- [ ] Test reports generated successfully for each variant
- [ ] No unexpected test skips (verify `GTEST_SKIP()` usage is correct)

## Debugging Checklist

When integration tests fail:

- [ ] Check component initialization order in SetUp()
- [ ] Verify mock configurations are correct
- [ ] Check for timing issues (add delays if needed)
- [ ] Verify component state synchronization
- [ ] Check for memory leaks (valgrind if available)
- [ ] Verify variant-specific configuration
- [ ] Check log output for error messages
- [ ] Isolate failing test to minimal reproduction case