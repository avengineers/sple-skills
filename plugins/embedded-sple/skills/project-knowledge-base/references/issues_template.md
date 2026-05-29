# Issues/Work Log Template

This file demonstrates the format for logging work completed on tickets. Keep it simple - just enough to remember what was done. Full details live in Jira/GitHub.

## Format

Each entry should include:

- Date (YYYY-MM-DD)
- Ticket ID
- Brief description (1-2 lines)
- URL to ticket (if available)
- Status (optional: completed, in-progress, blocked)

Use bullet lists for simplicity. This is NOT a replacement for your ticket system - it's a quick reference log.

## Example Entries

### 2025-03-10 - PROJ-1042: Integrate Polyspace Bug Finder into CI

- **Status**: Completed
- **Description**: Added Polyspace Bug Finder analysis step to Jenkins pipeline for the `develop` branch
- **URL**: <https://jira.example.com/browse/PROJ-1680>
- **Notes**: Configured for MISRA C:2012 mandatory rules; 3 existing violations baselined

### 2025-03-12 - PROJ-1048: Fix CAN Message Handler Stack Overflow

- **Status**: Completed
- **Description**: Reduced ISR stack usage by moving RX buffer from local to static scope
- **URL**: <https://jira.example.com/browse/PROJ-1145>
- **Notes**: See bugs.md for root cause details; added stack usage annotation for HIS metrics

### 2025-03-15 - PROJ-1055: Increase Unit Test Coverage for NVM Module

- **Status**: In Progress
- **Description**: Writing GTest unit tests for `nvm_read()` and `nvm_write()` with hammock mocking
- **URL**: <https://jira.example.com/browse/PROJ-1164>
- **Notes**: Coverage currently at 62%, target is 90%. CRC error paths still untested.

### 2025-03-18 - PROJ-1060: MISRA Deviation for Hardware Register Cast

- **Status**: Completed
- **Description**: Documented Rule 11.3 deviation for memory-mapped I/O register access pattern
- **URL**: <https://jira.example.com/browse/PROJ-78>
- **Notes**: ADR-003 policy applied; deviation record added to doc/quality/misra_deviations.md

### 2025-03-20 - PROJ-1063: Watchdog Timer Configuration Review

- **Status**: Blocked
- **Description**: Need to validate watchdog timeout against worst-case task execution time
- **URL**: <https://jira.example.com/browse/PROJ-2064>
- **Notes**: Waiting for HIS metrics analysis of cyclomatic complexity in `diag_main()` task

## Alternative Format (Grouped by Sprint)

### Sprint 2025-S06 (Mar 10 - Mar 21)

**Completed:**

- PROJ-1042: Polyspace CI integration → <https://jira.example.com/browse/PROJ-1659>
- PROJ-1048: CAN ISR stack overflow fix → <https://jira.example.com/browse/PROJ-38>
- PROJ-1060: MISRA deviation documentation → <https://jira.example.com/browse/PROJ-1406>

**In Progress:**

- PROJ-1055: NVM module test coverage (62% → 90% target)

**Blocked:**

- PROJ-1063: Watchdog config (waiting on HIS metrics) → <https://jira.example.com/browse/PROJ-1407>

## Tips

- Keep descriptions brief (1-2 lines max)
- Always include ticket URL for easy reference
- Update status if work gets blocked or resumed
- Optional: Group by sprint for better organization
- Don't duplicate ticket details - link to source of truth
- Clean out very old entries periodically (3+ months)
- Reference related entries in bugs.md or decisions.md where applicable
