---
name: project-knowledge-base
description: "Set up and maintain a structured project memory system in doc/project_notes/ that tracks bugs with solutions, architectural decisions, key project facts, and work history. Use when asked to 'set up project memory', 'log a bug fix', 'track decisions', or 'initialize memory system'. Also triggers proactively: before proposing architectural changes, when encountering errors that might have been seen before, or when hardware/toolchain configuration is needed. Any embedded project with recurring problems or institutional knowledge benefits from this."
---

# Project Memory

## Why This Matters

Embedded projects accumulate critical knowledge that lives nowhere in the source code: why a particular RTOS was chosen over bare-metal, what stack size caused a watchdog reset last month, which CAN node IDs are reserved. Without a structured place to record this, every new session (human or AI) starts from zero. This skill creates that institutional memory and — more importantly — teaches the agent to *consult it proactively* before making decisions or proposing changes.

The value is not in the file structure itself. The value is in the habit of checking before acting.

## Proactive Behavior — The Core Rule

The most important thing this skill teaches is *when to look things up without being asked*:

- **Before proposing any architectural or design change** → search `decisions.md` for prior ADRs on the topic
- **When encountering a build error, runtime fault, or hardware anomaly** → search `bugs.md` for similar symptoms
- **When needing hardware config, toolchain versions, pin assignments, or memory layout** → check `key_facts.md` instead of guessing
- **After completing a ticket or resolving a bug** → update `issues.md` or `bugs.md`

**If `doc/project_notes/` does not exist, this skill does nothing** — no offer, no question, no log. Other skills end with "document findings using `project-knowledge-base`"; in a project without memory that step is skipped silently. Only when the user asks you directly to record something in the project memory, say in one sentence that none exists. Setup happens only when the user asks for it (see Setup below).

This is not optional housekeeping. If `doc/project_notes/` exists, *always consult it* before suggesting solutions that might contradict documented decisions or re-introduce known bugs. The few seconds of reading save hours of rework.

**How to search:** For files under ~50 lines, read the full file. For larger files, use grep with relevant keywords (error messages, component names, peripheral identifiers) rather than loading the entire file into context.

## Boundary with Other Skills

This skill **owns the structure and format** of `doc/project_notes/`. Other skills *write into* these files:

- `retrospective` → appends to `bugs.md`, `decisions.md`, `issues.md` after sprint retrospectives
- `modernization-roadmap` / `test-coverage-roadmap` → write their own `*_lessons_learned.md` files into `doc/project_notes/`

The difference: this skill handles **setup, day-to-day updates, and proactive consult## Setup

When the user asks to set up or initialize project memory, read [references/setup.md](references/setup.md) and propose its steps. Never run them on your own.

## Updating Memory Files

Follow the format defined in the reference templates. Key rules:

- **Dates**: Always include (YYYY-MM-DD)
- **Conciseness**: 1-3 lines per entry. Full details live in Jira/Confluence.
- **URLs**: Link to tickets, documentation, dashboards
- **Append-only**: Add new entries at the top of each section (newest first). This minimizes Git merge conflicts when multiple contributors update the same file.
- **Security**: NEVER store passwords, API keys, JTAG keys, signing keys, or tokens in `key_facts.md`. These belong in secret managers or environment variables.

## Maintenance

- User is responsible for manual cleanup (no automation)
- Aim to keep each file under ~100 entries for fast parsing; archive older content to a dated file (e.g., `bugs_2024.md`) when a file grows beyond that
- Remove bug entries older than 24 months if the affected code no longer exists or the bug is unreproducible
- Archive completed work from `issues.md` after 3 months
- Keep all ADRs — they're lightweight and provide historical context
- When a decision is revisited, update the ADR entry with the new date and rationale

## Example Workflow

```text
User: "The watchdog keeps resetting during flash erase"
1. Search doc/project_notes/bugs.md for "watchdog" and "flash"
2. Find: "2025-03-18 - Flash write disables interrupts, blocking RTOS tick"
3. Apply documented solution (move flash ops to idle task)
4. If it's a new variant, add a new entry after resolving

User: "Let's switch from FreeRTOS to Zephyr"
1. Search doc/project_notes/decisions.md for "RTOS"
2. Find ADR-001: FreeRTOS chosen because Zephyr was "overkill for our MCU"
3. Acknowledge existing decision, ask whether circumstances changed
4. If user confirms change, update ADR-001 with revision date and new rationale
```

## References

- **references/setup.md** — Setup steps, read only when the user asks for setup

Templates with embedded-specific examples and formatting guidance:

- **references/bugs_template.md** — ISR stack overflows, linker errors, RTOS deadlocks
- **references/decisions_template.md** — RTOS selection, memory allocation strategy, MISRA deviations
- **references/key_facts_template.md** — MCU specs, toolchain config, CAN/UART parameters, memory map
- **references/issues_template.md** — Ticket log format with sprint grouping option

## Integration with Other Skills

- **c-code-review-***: Document recurring review findings as ADRs in `decisions.md`
- **static-code-analysis**: Log Polyspace/Cppcheck root causes in `bugs.md`
- **conventional-commits**: Reference ADR/bug IDs in commit messages for traceability
