# Step Template

Use this template when adding or detailing a step in the coverage roadmap.

---

### Step N: <FUNCTION_NAME>

> **MANDATORY**: Each step covers exactly ONE function. For large functions with many branches,
> split into multiple steps targeting different paths — but each step still focuses on one function.

**Status**: `NOT_STARTED`

| Field | Value |
|-------|-------|
| Function | `<function_name>` |
| File | `<file.c>` |
| Line | <line_number> |
| Complexity | Low/Medium/High |
| Started | - |
| Completed | - |
| Coverage Before | <NN>% |
| Coverage After | - |
| Coverage Gain | - |
| Approved by | - |

#### Objective

Add unit tests for `<function_name>` to increase coverage by approximately <N>%.

#### Function Under Test

| Attribute | Value |
|-----------|-------|
| Function | `<function_name>` |
| File | `<file.c>` |
| Line Coverage | <NN>% |
| Branch Coverage | <NN>% |

#### Test Scenarios

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| T1 | Happy path | Valid input | Function called | Expected output |
| T2 | Null pointer | NULL parameter | Function called | Returns error |
| T3 | Boundary | Max value input | Function called | Handles correctly |

#### Test File Structure

```text
components/<path>/test/
  <Component>_<Function>_test.cpp   # New test file
```

#### Prerequisites

- [ ] Component builds without errors
- [ ] Existing tests pass
- [ ] Hammock setup available for dependencies

#### Definition of Done

**Mandatory**:

- [ ] All planned test scenarios implemented
- [ ] All tests pass
- [ ] Expected coverage gain achieved (+/- 2%)
- [ ] Human review approved

**Quality**:

- [ ] Tests follow BDD/Gherkin style
- [ ] Tests are independent (no order dependency)
- [ ] Test names clearly describe behavior
- [ ] No flaky tests

---

## After Step Completion

Update the step entry with:

```markdown
**Status**: `COMPLETED`

| Field | Value |
|-------|-------|
| Started | YYYY-MM-DD HH:MM |
| Completed | YYYY-MM-DD HH:MM |
| Coverage Before | <NN>% |
| Coverage After | <NN>% |
| Coverage Gain | +<N>% |
| Approved by | <Name> |

#### Tests Added

| Test File | Test Case | Description |
|-----------|-----------|-------------|
| `<file>_test.cpp` | `<TestName>` | <what it tests> |

#### Retrospective Notes

**What went well**: <brief>

**What to improve**: <brief>

**Lessons learned**: <brief - also add to lessons learned file>

#### Commit

- SHA: `<commit_sha>`
- Message: `feat: add <component> unit tests for <scope> (<JIRA-ISSUE>)`
```

---

## Test Writing Checklist

Before writing tests, verify:

- [ ] `c-unit-testing` skill invoked for guidance
- [ ] Hammock dependencies identified
- [ ] Test file naming follows convention
- [ ] BDD style understood (Given/When/Then)

When writing tests:

- [ ] One logical assertion per test (or closely related assertions)
- [ ] Test name describes behavior, not implementation
- [ ] Setup/teardown properly handled
- [ ] Edge cases considered
- [ ] Error paths tested

After writing tests:

- [ ] All tests pass locally
- [ ] No compiler warnings in test code
- [ ] Coverage measured and documented
