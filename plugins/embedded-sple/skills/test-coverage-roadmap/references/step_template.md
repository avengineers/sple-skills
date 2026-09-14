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
| Test level | Unit / Integration — reason: `<why>` (planned in Step 2.2) |
| Started | - |
| Completed | - |
| Line Coverage Before | <NN>% |
| Line Coverage After | - |
| Line Coverage Gain | - |
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

#### Untestable Lines (Step 2.1a — leave empty when there are none)

Candidates for the roadmap's NOT_TESTABLE register. Approved together with the plan in Step 2.3,
never separately. Only `DEFENSIVE_BY_DESIGN` or `UNREACHABLE_DEFECT`; a third reason does not exist.

| Location | Lines | Reason | Evidence |
|----------|-------|--------|----------|
| `<file.c>:<NN>` | <N> | `<one of the two>` | `<checklist item, or UNR finding / MISRA rule>` |

For `UNREACHABLE_DEFECT`, state that removal is recommended and hand it to
`modernization-roadmap` — this skill does not remove production code.

#### Specification (Step 2.1b — filled before the test scenarios)

| Attribute | Value |
|-----------|-------|
| Spec documents read | `<path>` (component `doc/index.md`, unit spec) |
| Spec IDs read | `<SWDD-ID>, <SWDD-ID>` |
| Spec exists for this function | Yes / No — "No" is a finding, record it |
| Spec vs. implementation discrepancy | None / `<what differs>` |
| A/B decision | - (A = test pins the implementation, B = test pins the spec) |
| Decided by | - (human, together with the plan approval in Step 2.3) |

#### Test Scenarios

| ID | Scenario | Req (SWDD ID) | Given | When | Then |
|----|----------|---------------|-------|------|------|
| T1 | Happy path | `<SWDD-ID>` | Valid input | Function called | Expected output |
| T2 | Null pointer | `<SWDD-ID>` | NULL parameter | Function called | Returns error |
| T3 | Boundary | `<SWDD-ID>` | Max value input | Function called | Handles correctly |

#### Test File Structure

```text
components/<path>/test/
  test_<Component>_<Function>.cc              # unit test  (test level: Unit)
  test_<Component>_integration.cc             # integration test (test level: Integration)
```

The name follows the test level approved in Step 2.3 — `c-unit-testing` owns the unit name,
`c-integration-testing` the integration one. Do not invent a third form; the naming check rejects it.

#### Prerequisites

- [ ] Component builds without errors
- [ ] Existing tests pass
- [ ] Hammock setup available for dependencies

#### Definition of Done

<!-- dod:delegated -->

The DoD is the checklist in the skill — `SKILL.md` → *Step Definition of Done (DoD) Checklist*.
Paste the completed box with real evidence. The items below are additional to it, never a
replacement.

#### Additional Checks For This Step

- [ ] Test level approved by the human together with the plan (Step 2.3)
- [ ] Untestable lines classified; any entry approved with the plan and copied into the roadmap register
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
| Line Coverage Before | <NN>% |
| Line Coverage After | <NN>% |
| Line Coverage Gain | +<N>% |
| Approved by | <Name> |

#### Tests Added

| Test File | Test Case | Description |
|-----------|-----------|-------------|
| `test_<Component>_<Function>.cc` | `<TestName>` | <what it tests> |

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

- [ ] Skill for the approved test level invoked (`c-unit-testing` or `c-integration-testing`)
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
