# Branch Workflow Patterns

Detailed branching strategies and workflow patterns for trunk-based development.

> **NOTE**: For commit message formatting (types, JIRA extraction, etc.), 
> see the `conventional-commits` skill.

## Core Principles

1. **One main integration branch**: Typically `develop` or `main`
2. **Short-lived feature branches**: Merge within 1-2 days
3. **Frequent integration**: Merge to main branch multiple times per day
4. **No long-lived branches**: Avoid feature branches that live for weeks
5. **Small incremental changes**: Each merge is a small, working increment

## Branch Naming Convention

Format: `feature/<JIRA-ISSUE>-<short-description>`

JIRA issue is extracted from the branch name for commit messages.

### Examples

```
✓ feature/PROJ-1001-uart-config
✓ feature/PROJ-1002-gpio-toggle
✓ feature/PROJ-1003-hal-spi-driver
✓ feature/PROJ-2001-fix-adc-bitmask
✓ feature/PROJ-3001-update-docs
```

### Avoid

```
✗ feature/new-feature (missing JIRA issue)
✗ feature/PROJ-1001 (missing description)
✗ uart-config (missing prefix)
✗ feature/PROJ-1001-uart (lowercase JIRA issue)
✗ feature/SPLE_1001_uart (use hyphens)
✗ dev/PROJ-1001-uart (use 'feature' not 'dev')
```

## Standard Workflows

### Workflow 1: Simple Feature Addition

**Scenario**: Adding a new feature that takes < 2 hours

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch (include JIRA issue)
git checkout -b feature/PROJ-1001-uart-config

# 3. Implement feature
# ... make changes ...
git add src/uart.c src/uart.h
git commit -m "feat: add UART baudrate configuration (PROJ-1001)"

# 4. Push and create PR
git push origin feature/PROJ-1001-uart-config

# 5. After PR approval, merge via GitHub/GitLab
# (typically squash merge)

# 6. Clean up locally
git checkout develop
git pull origin develop
git branch -d feature/PROJ-1001-uart-config
```

### Workflow 2: Multi-commit Feature

**Scenario**: Feature requiring multiple logical commits

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/PROJ-1003-hal-spi

# 3. First commit - interface
git add include/hal_spi.h
git commit -m "feat: add SPI interface definition for HAL (PROJ-1003)"

# 4. Second commit - implementation
git add src/hal_spi.c
git commit -m "feat: implement SPI driver for HAL (PROJ-1003)"

# 5. Third commit - tests
git add test/test_hal_spi.cc
git commit -m "feat: add SPI driver unit tests (PROJ-1003)"

# 6. Push all commits
git push origin feature/PROJ-1003-hal-spi

# 7. After PR approval, squash merge
git checkout develop
git pull origin develop
git branch -d feature/PROJ-1003-hal-spi
```

### Workflow 3: Quick Bug Fix

**Scenario**: Urgent bug fix needed in develop

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create fix branch
git checkout -b feature/PROJ-2001-adc-fix

# 3. Fix and commit
git add src/adc.c
git commit -m "fix: correct ADC channel selection bitmask (PROJ-2001)"

# 4. Push and create PR
git push origin feature/PROJ-2001-adc-fix

# 5. Fast-track review and merge
# After merge:
git checkout develop
git pull origin develop
git branch -d feature/PROJ-2001-adc-fix
```

### Workflow 4: Staying Up-to-Date

**Scenario**: Feature branch falls behind develop

```bash
# 1. On feature branch
git checkout feature/PROJ-1001-uart-config

# 2. Fetch latest develop
git fetch origin develop

# 3. Rebase on develop
git rebase origin/develop

# 4. Resolve conflicts if any
# ... resolve conflicts ...
git add <resolved-files>
git rebase --continue

# 5. Force push (since history changed)
git push origin feature/PROJ-1001-uart-config --force-with-lease
```

### Workflow 5: Feature Too Large

**Scenario**: Feature will take > 2 days, split into smaller pieces

Instead of:
```bash
# BAD: Long-lived branch
feature/PROJ-1001-complete-uart-driver (5 days of work)
```

Use feature flags or split:
```bash
# GOOD: Multiple short-lived branches
feature/PROJ-1001-uart-interface     (day 1, merged)
feature/PROJ-1001-uart-basic-tx      (day 2, merged, flagged off)
feature/PROJ-1001-uart-basic-rx      (day 3, merged, flagged off)
feature/PROJ-1001-uart-dma           (day 4, merged, flagged off)
feature/PROJ-1001-uart-enable-all    (day 5, merged, flags enabled)
```

## Keeping Branches Short-Lived

### Strategy 1: Work in Small Increments

```bash
# Instead of one large feature:
✗ feature/PROJ-1001-complete-hal-layer (200 files, 2 weeks)

# Break into smaller pieces:
✓ feature/PROJ-1001-hal-gpio      (10 files, 1 day)
✓ feature/PROJ-1002-hal-uart      (15 files, 1 day)
✓ feature/PROJ-1003-hal-spi       (12 files, 1 day)
✓ feature/PROJ-1004-hal-i2c       (14 files, 1 day)
```

### Strategy 2: Use Feature Flags

```c
// In config.h or generated from KConfig
#define FEATURE_NEW_UART_DRIVER 0

// In code
#if FEATURE_NEW_UART_DRIVER
    // New implementation (merged but disabled)
    new_uart_init();
#else
    // Old implementation (still active)
    old_uart_init();
#endif
```

```bash
# Enable progressive merging:
feature/PROJ-1001-uart-new-impl      # New code, flagged off, merged day 1
feature/PROJ-1001-uart-testing       # Tests added, flagged off, merged day 2
feature/PROJ-1001-uart-enable        # Enable flag, merged day 3
```

### Strategy 3: Stub Out Incomplete Features

```c
// Merge interface first
void new_feature_init(void) {
    // TODO: Full implementation in next PR
    return; // Stub - does nothing yet
}
```

```bash
feature/PROJ-1001-interface-stub     # Stub merged, doesn't break anything
feature/PROJ-1001-implementation     # Real implementation follows
```

## Integration Patterns

### Pattern 1: Direct Merge (Small Teams)

```bash
# For teams < 5 developers
git checkout develop
git merge feature/PROJ-1001-uart-config
git push origin develop
```

### Pattern 2: Squash Merge (Recommended)

```bash
# Condense feature branch into single commit on develop
# Done via GitHub/GitLab UI or:
git checkout develop
git merge --squash feature/PROJ-1001-uart-config
git commit -m "feat: add UART baudrate configuration (PROJ-1001)"
git push origin develop
```

### Pattern 3: Rebase and Merge (Clean History)

```bash
# Rebase feature commits onto develop
git checkout feature/PROJ-1001-PROJ-1001-uart-config
git rebase develop
git checkout develop
git merge --ff-only feature/PROJ-1001-uart-config
git push origin develop
```

## Conflict Resolution

### When Conflicts Occur During Rebase

```bash
# 1. Start rebase
git checkout feature/PROJ-1001-uart-config
git rebase develop

# Conflict occurs!
# 2. Check status
git status

# 3. Resolve conflicts in files
# ... edit conflicting files ...

# 4. Stage resolved files
git add <resolved-files>

# 5. Continue rebase
git rebase --continue

# 6. If more conflicts, repeat 3-5

# 7. Force push updated branch
git push origin feature/PROJ-1001-uart-config --force-with-lease
```

### When Conflicts Occur During Merge

```bash
# 1. Attempt merge
git checkout develop
git merge feature/PROJ-1001-uart-config

# Conflict occurs!
# 2. Resolve conflicts
# ... edit conflicting files ...

# 3. Stage resolved files
git add <resolved-files>

# 4. Complete merge
git commit -m "feat: add UART baudrate configuration (PROJ-1001)"

# 5. Push
git push origin develop
```

## Pull Request Workflow

### Creating a PR

```bash
# 1. Push feature branch
git push origin feature/PROJ-1001-uart-config

# 2. Open PR via GitHub/GitLab UI
# Title: feat: add UART baudrate configuration (PROJ-1001)
# Description:
#   - Adds configuration functions
#   - Updates documentation
#   - Includes unit tests
```

### PR Review Process

1. **Code review**: Team reviews changes
2. **CI checks**: Automated tests pass
3. **Approval**: Required approvers sign off
4. **Merge**: Squash merge to develop
5. **Cleanup**: Delete feature branch

### After PR Merged

```bash
# Update local develop
git checkout develop
git pull origin develop

# Delete local feature branch
git branch -d feature/PROJ-1001-uart-config

# Delete remote feature branch (if not auto-deleted)
git push origin --delete feature/PROJ-1001-uart-config
```

## Anti-Patterns to Avoid

### ✗ Long-Lived Feature Branches

```bash
# BAD: Branch lives for weeks
feature/PROJ-1001-big-refactor (created 3 weeks ago, 500+ commits behind develop)

# Causes:
# - Difficult merge conflicts
# - Integration hell
# - Delayed feedback
```

### ✗ Massive Pull Requests

```bash
# BAD: 100+ files changed
feature/PROJ-1001-complete-rewrite

# Better: Split into smaller PRs
feature/PROJ-1001-refactor-part1 (10 files)
feature/PROJ-1001-refactor-part2 (12 files)
feature/PROJ-1001-refactor-part3 (15 files)
```

### ✗ Merging Broken Code

```bash
# BAD: Tests failing
git commit -m "feat: add UART config (WIP) (PROJ-1001)"
git push origin feature/PROJ-1001-uart-config
# PR merged with failing tests!

# GOOD: Only merge working code
git commit -m "feat: add UART baudrate configuration (PROJ-1001)"
# All tests pass before merge
```

### ✗ Multiple Feature Branches per Developer

```bash
# BAD: Developer has 5 open branches
feature/PROJ-1001-uart-config
feature/PROJ-1002-gpio-toggle
feature/PROJ-1003-spi-driver
feature/PROJ-1004-hal-refactor
feature/PROJ-3001-docs-update

# GOOD: One branch at a time
feature/PROJ-1001-uart-config (working on this)
# Complete and merge before starting next
```

## Team Coordination

### Before Starting Work

```bash
# Check for existing branches
git fetch origin
git branch -r | grep feature/PROJ-1001

# If branch exists, coordinate with teammate
# If not, create new branch
```

### Communicating Changes

```
# In team chat:
"Starting work on feature/PROJ-1001-uart-config, should be done by EOD"
"Opened PR for feature/PROJ-1002-gpio-toggle, needs review"
"Merged feature/PROJ-1003-hal-spi, everyone please pull latest develop"
```

### Daily Integration

```bash
# At least once per day:
git checkout develop
git pull origin develop

# Rebase your feature branch
git checkout feature/PROJ-1001-uart-config
git rebase develop
```
