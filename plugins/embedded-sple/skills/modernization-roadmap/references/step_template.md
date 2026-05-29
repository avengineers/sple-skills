# Step Template

Use this template when adding a new step to the roadmap.

---

### Step N: <Step Name>

**Status**: `NOT_STARTED`

| Field       | Value              |
| ----------- | ------------------ |
| Started     | -                  |
| Completed   | -                  |
| Approved by | -                  |
| RAM Delta   | -                  |
| ROM Delta   | -                  |

#### Objective

<Clear, concise statement of what this step achieves>

#### Rationale

<Why this step is needed - link to review findings or technical debt>

#### Prerequisites

- [ ] <Previous step completed>
- [ ] <Required knowledge/documentation available>
- [ ] <Dependencies resolved>

#### Changes Planned

Files to modify:

| File                    | Change Type | Description          |
| ----------------------- | ----------- | -------------------- |
| `path/to/file.c`        | Refactor    | <What will change>   |
| `path/to/file.h`        | Interface   | <What will change>   |

Specific changes:

- [ ] <Change 1: e.g., "Extract function X from Y">
- [ ] <Change 2: e.g., "Add input validation to Z">
- [ ] <Change 3: e.g., "Remove dead code in W">

#### Definition of Done

**Mandatory (non-negotiable)**:

- [ ] All unit tests pass
- [ ] RAM increase < 10%
- [ ] ROM increase < 10%
- [ ] Human review approved

**Quality gates**:

- [ ] No new compiler warnings
- [ ] No new static analysis findings
- [ ] Code follows BARR-C:2018 style

**Documentation**:

- [ ] Step documented in roadmap
- [ ] Lessons learned updated
- [ ] Commit message follows `conventional-commits` skill format

#### Risks

| Risk ID | Description       | Probability | Impact     | Mitigation            |
| ------- | ----------------- | ----------- | ---------- | --------------------- |
| R-N.1   | <Risk>            | low/med/hi  | low/med/hi | <Mitigation>          |

#### Test Plan

Tests to run:

```powershell
# Run component tests
.\build.ps1 -build -buildKit test -buildType Debug -variant <VARIANT> -target components_<path>_unittests
```

Expected results:

- All existing tests pass
- <Any new tests added>

#### Rollback Plan

If step fails:

1. `git checkout -- <files changed>`
2. <Additional rollback steps if needed>

---

## After Step Completion

Update the step entry with:

```markdown
**Status**: `COMPLETED`

| Field       | Value              |
| ----------- | ------------------ |
| Started     | YYYY-MM-DD HH:MM   |
| Completed   | YYYY-MM-DD HH:MM   |
| Approved by | <Name>             |
| RAM Delta   | +X% (Y bytes)      |
| ROM Delta   | +X% (Y bytes)      |

#### Actual Changes

- [x] <What was actually done>
- [x] <What was actually done>
- [ ] <What was deferred to later step>

#### Retrospective Notes

**What went well**: <brief>

**What to improve**: <brief>

**Lessons learned**: <brief - also add to central lessons learned file>

#### Commit

- SHA: `<full_sha>`
- Message: `modernization(<component>): <description>`
```
