---
name: conventional-commits
description: Standard for creating conventional commit messages with JIRA issue extraction from branch names. Use this skill whenever changes need to be committed — including after completing any coding task, bug fix, refactoring, test addition, or documentation update. Trigger on any commit-related activity such as "git commit", "commit changes", "stage and commit", "save my changes", "commit message", "conventional commit", or when finishing a workflow step that produces file changes.
---

# Conventional Commits

Standard guide for creating properly formatted conventional commit messages with JIRA issue extraction.

> **Philosophy**: Clear, consistent commit messages that document change history and link to JIRA issues.

---

## Agent Execution Instructions

Following a consistent order prevents mistakes like committing unstaged files or forgetting the JIRA reference. The steps below ensure every commit is traceable and well-formatted.

### First-Run Setup: Ensure AGENTS.md Enforcement

On the first invocation of this skill in a repository, check whether the project's `AGENTS.md` (or `CLAUDE.md` or `.github/copilot-instructions.md`) contains a mandatory commit rule. If not, add the following to the Git Workflow section:

```markdown
- **MANDATORY**: Before every `git commit`, extract the JIRA issue ID from the current branch name and include it in the commit subject line. Format: `<type>: <description> (<ISSUE-REF>)`. Use the `conventional-commits` skill workflow for proper formatting.
```

This ensures all agents working in the repository follow the convention — even if this skill is not explicitly invoked.

### Commit Workflow

> **CRITICAL**: Never commit or stage files autonomously. Do not run `git add` or `git commit`
> without explicit user instruction. The user reviews changes in the "Changes" section of
> their IDE before deciding what to stage. Present a summary of modified files and the
> proposed commit message, then wait for the user to say "commit", "stage", or equivalent.

When committing changes — whether triggered directly by the user or as the final step of another workflow — follow these steps:

```text
1. Present changes for review ← BLOCKING
   → Show: list of modified files and proposed commit message
   → Do NOT run git add — let the user review in their IDE first
   → Wait for explicit user instruction to proceed

2. Stage changes (only after user says to stage/commit)
   → Run: git add <files>
   → Verify staged changes with: git --no-pager diff --staged

3. Extract issue reference from branch name
   → Run extraction command (see Issue Reference Extraction below)
   → Follows priority: JIRA > GitHub issue > none

4. Determine commit type
   → Analyze staged changes to select appropriate type
   → See Commit Types table below

5. Generate commit message
   → With issue:    <type>: <description> (<ISSUE-REF>)
   → Without issue: <type>: <description>
   → Optional: Add body for complex changes

6. Execute commit
   → Run: git commit -m "<message>"
   → OR: git commit -m "<subject>" -m "<body>" for multi-line

7. Verify commit
   → Run: git --no-pager log -1
   → Show commit hash as evidence
```

---

## Commit Message Format

Consistent formatting makes `git log` scannable and enables automated tooling (changelogs, release notes). Use this format for every commit:

```text
<type>: <description> (<ISSUE-REF>)

[optional body]
```

If no issue reference is found in the branch name, omit the parenthesized suffix:

```text
<type>: <description>
```

### Format Rules

| Element | Rule |
|---------|------|
| **Type** | One of: `feat`, `fix`, `refactor`, `style`, `chore`, `docs`, `test` |
| **Description** | Max 72 chars total subject line, imperative mood, lowercase, no period |
| **Issue Ref** | Auto-extracted from branch: JIRA (`PROJ-1234`), GitHub (`#123`), or omitted |
| **Body** | Optional, wrap at 72 chars, explain "why" not "what" |

---

## Commit Types

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | New feature or capability | `feat: add baudrate configuration for UART (PROJ-1001)` |
| `fix` | Bug fix that corrects behavior | `fix: correct ADC channel selection bitmask (PROJ-1004)` |
| `refactor` | Code restructuring without behavior change | `refactor: extract validation logic from StateMgr (PROJ-1010)` |
| `style` | Formatting-only changes (whitespace, indentation) | `style: apply BARR-C formatting to HAL module (PROJ-1011)` |
| `chore` | Maintenance tasks (build, config, deps) | `chore: update CMake minimum version (PROJ-1007)` |
| `docs` | Documentation-only changes | `docs: add README for component setup (PROJ-1008)` |
| `test` | Adding or modifying tests (no production code) | `test: add StateMgr state machine unit tests (PROJ-1002)` |

### Type Selection Decision Tree

```text
Did you change production code?
├── YES: Did behavior change?
│   ├── YES: Is it a bug fix?    → `fix`
│   │   └── NO: Is it a new feature? → `feat`
│   └── NO: Is it restructuring? → `refactor`
│       └── NO: Is it formatting? → `style`
└── NO: Did you change tests only?
    ├── YES → `test`
    └── NO: Did you change docs only?
        ├── YES → `docs`
        └── NO → `chore`
```

---

## Issue Reference Extraction

The extraction follows a priority chain: JIRA first, then GitHub issue, then no reference. This ensures the commit always links to the right tracker.

### PowerShell

```powershell
$branch = git rev-parse --abbrev-ref HEAD

# Priority 1: JIRA issue (any project key, e.g., PROJ-1234, HW-89)
if ($branch -match '([A-Z]{2,}-\d+)') {
    $issueRef = "($($matches[1]))"
}
# Priority 2: GitHub issue (number after /, e.g., feature/123-description)
elseif ($branch -match '/(\d+)[-/]') {
    $issueRef = "(#$($matches[1]))"
}
# No issue found — commit without reference
else {
    $issueRef = ""
}
Write-Host "Issue reference: $issueRef"
```

### Bash

```bash
branch=$(git rev-parse --abbrev-ref HEAD)

# Priority 1: JIRA issue (any project key, e.g., PROJ-1234, HW-89)
jira_issue=$(echo "$branch" | grep -oE '[A-Z]{2,}-[0-9]+' | head -1)
if [ -n "$jira_issue" ]; then
    issue_ref="($jira_issue)"
else
    # Priority 2: GitHub issue (number after /, e.g., feature/123-description)
    gh_issue=$(echo "$branch" | sed -n 's|.*/\([0-9]\+\)-.*|\1|p')
    if [ -n "$gh_issue" ]; then
        issue_ref="(#$gh_issue)"
    else
        issue_ref=""
    fi
fi
echo "Issue reference: $issue_ref"
```

### Branch Naming Convention

Feature branches should include an issue reference so it can be extracted automatically — this is the link between your code changes and the backlog item:

```text
feature/PROJ-1234-short-description   → (PROJ-1234)
feature/PROJ-567-short-description    → (PROJ-567)
feature/123-short-description         → (#123)
feature/short-description             → no suffix
```

---

## Commit Examples

### Simple Commits

```text
feat: add compiler switch to enable/disable LoS (PROJ-2145)
feat: add baudrate configuration for UART (PROJ-1001)
fix: correct I2C timeout handling in HAL (HW-234)
fix: prevent timer overflow in StateMgr (#45)
test: add unit tests for StateMgr state machine (PROJ-1002)
test: add GPIO toggle integration tests (#103)
refactor: extract CAN message parsing to module (PROJ-2000)
style: apply consistent indentation to HAL (PROJ-2001)
docs: update HAL documentation (PROJ-408)
chore: update CMake minimum version
```

### Multi-line Commits (Complex Changes)

```text
fix: prevent overflow in timer period calculation (PROJ-1234)

Calculation was using uint16_t causing overflow for periods > 65535.
Changed to uint32_t to support full range.

Refs: doc/project_notes/bugs/timer_overflow.md
```

### Test Coverage Step Commit

```text
test: add StateMgr tests for InitState function (PROJ-1234)

Step 3 of coverage roadmap - 45.2% -> 52.8% coverage (+7.6%)
- test/StateMgr/test_StateMgr.cc

Refs: doc/test-coverage/StateMgr_coverage_roadmap_20260205.md
```

### Modernization Step Commit

```text
refactor: extract StateMgr timer logic to separate module (PROJ-1234)

Step 2 of modernization roadmap
- Extracted timer functions to StateMgr_Timer.c
- Added unit tests for timer module
- Coverage maintained at 78%

Refs: doc/modernization/StateMgr_modernization_roadmap_20260205.md
```

### Commit with Skipped Items

```text
test: add StateMgr tests for ProcessMessage (PROJ-1234)

Step 4 of coverage roadmap - 52.8% -> 58.1% coverage (+5.3%)
- test/StateMgr/test_StateMgr.cc

SKIPPED: 2.9b (timeout) - approved by user

Refs: doc/test-coverage/StateMgr_coverage_roadmap_20260205.md
```

---

## Complete Commit Workflow Example

### Agent Execution Flow

```powershell
# ========== STEP 1: Stage changes ==========
git add test/StateMgr/test_StateMgr.cc
git --no-pager diff --staged --stat

# ========== STEP 2: Extract issue reference ==========
$branch = git rev-parse --abbrev-ref HEAD
if ($branch -match '([A-Z]{2,}-\d+)') {
    $issueRef = "($($matches[1]))"
} elseif ($branch -match '/(\d+)[-/]') {
    $issueRef = "(#$($matches[1]))"
} else {
    $issueRef = ""
}
Write-Host "Branch: $branch"
Write-Host "Issue reference: $issueRef"

# ========== STEP 3: Determine commit type ==========
# Analyzing staged changes:
# - Only test files modified → type: test

# ========== STEP 4 & 5: Generate and execute commit ==========
$msg = "test: add StateMgr InitState unit tests $issueRef".Trim()
git commit -m $msg

# ========== STEP 6: Verify commit ==========
git --no-pager log --oneline -1
```

---

## Validation

### Description Length Check

The total subject line (type + description + JIRA) should stay within 72 characters. This keeps `git log --oneline` and GitHub's commit list readable without truncation:

```powershell
$message = "feat: add feature description (PROJ-1234)"
if ($message.Length -gt 72) {
    Write-Warning "Commit message too long: $($message.Length) chars (max 72)"
} else {
    Write-Host "Message length OK: $($message.Length) chars"
}
```

### Commit Message Checklist

Before committing, verify:

- [ ] **Type**: Correct type selected based on changes
- [ ] **Description**: Imperative mood ("add" not "added")
- [ ] **Description**: Lowercase first letter
- [ ] **Description**: No period at end
- [ ] **Description**: Includes component name if applicable
- [ ] **Issue Ref**: Extracted from branch name (JIRA, GitHub, or none)
- [ ] **Length**: Total subject line ≤72 characters
- [ ] **Body**: Added if change is complex (optional)

---

## Best Practices

1. **Keep commits atomic**: One logical change per commit
2. **Commit frequently**: Small, focused commits are easier to review
3. **Use imperative mood**: "add" not "added" or "adds"
4. **Be specific**: Include component name in description
5. **Link to artifacts**: Reference roadmaps, bug reports, etc. in body
6. **Verify before push**: Check commit with `git log -1`
7. **Document "why"**: Use body to explain reasoning for complex changes

---

## References

- AGENTS.md - Project-wide commit conventions
- [references/branch-patterns.md](references/branch-patterns.md) - Branch workflow and merge strategy
- `project-knowledge-base` skill - Log completed work in `doc/project_notes/issues.md`
