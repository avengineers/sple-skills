# Architectural Decisions Template

This file demonstrates the format for logging architectural decisions (ADRs). Use bullet lists for clarity.

## Format

Each decision should include:

- Date and ADR number
- Context (why the decision was needed)
- Decision (what was chosen)
- Alternatives considered
- Consequences (trade-offs, implications)

## Example Entries

### ADR-001: Use FreeRTOS Instead of Bare-Metal Super Loop (2025-03-05)

**Context:**

- Application complexity growing beyond what a super loop can handle cleanly
- Need prioritized task scheduling for CAN message processing vs. background diagnostics
- Future features require concurrent timing-critical operations

**Decision:**

- Use FreeRTOS as the real-time operating system
- Configure with preemptive priority scheduling and 1 ms tick rate
- Allocate tasks with static memory (no heap allocation after init)

**Alternatives Considered:**

- Bare-metal super loop → Rejected: scheduling becomes unmanageable with 5+ time-critical activities
- Zephyr RTOS → Rejected: overkill for our MCU, larger memory footprint
- Custom cooperative scheduler → Rejected: maintenance burden, no community support

**Consequences:**

- ✅ Clean separation of concerns via tasks
- ✅ Priority-based preemption for time-critical CAN handling
- ✅ Well-documented, widely used in automotive
- ❌ Stack sizing requires careful analysis per task
- ❌ Potential priority inversion if mutexes are misused
- ❌ Additional ~8 KB ROM, ~2 KB RAM overhead

### ADR-002: Static Memory Allocation Only — No malloc After Init (2025-03-08)

**Context:**

- Target MCU has 64 KB RAM with no MMU
- Dynamic allocation causes fragmentation in long-running embedded systems
- MISRA C:2012 Rule 21.3 prohibits use of malloc/free in safety-relevant code

**Decision:**

- Use only static allocation (global/static arrays, statically allocated RTOS objects)
- All buffers sized at compile time via `_cfg.h` configuration headers
- Linker script verifies total RAM usage at build time

**Alternatives Considered:**

- Pool allocator (fixed-size blocks) → Acceptable for non-safety code, but adds complexity
- Standard malloc with watchdog → Rejected: fragmentation risk in 24/7 operation
- Memory Protection Unit regions → Rejected: MCU variant lacks MPU

**Consequences:**

- ✅ Deterministic memory usage — no fragmentation possible
- ✅ MISRA C:2012 Rule 21.3 compliance
- ✅ RAM usage fully visible in linker map file
- ❌ Buffer sizes must be known at design time
- ❌ Worst-case sizing may waste RAM for rarely-used features
- ❌ Adding new features requires re-evaluating memory budget

### ADR-003: MISRA Deviations Require Documented Rationale (2025-03-12)

**Context:**

- Project must comply with MISRA C:2012 per customer requirement
- Some rules are impractical to follow in all cases (e.g., Rule 11.3 for HW register casts)
- Need a process that allows deviations without undermining compliance

**Decision:**

- All MISRA deviations require a deviation record in `doc/quality/misra_deviations.md`
- Each deviation must include: rule number, rationale, scope (file/function), and reviewer sign-off
- Polyspace suppression comments must reference the deviation ID

**Alternatives Considered:**

- Blanket suppression per rule → Rejected: hides real violations
- No deviations allowed → Rejected: impractical for hardware register access patterns
- Per-file deviation lists → Rejected: harder to audit across project

**Consequences:**

- ✅ Full traceability of every suppressed finding
- ✅ Auditor-friendly — all deviations in one searchable document
- ✅ Forces developers to justify each deviation explicitly
- ❌ Administrative overhead for common patterns (e.g., register access)
- ❌ Deviation list grows over time — needs periodic review

## Tips

- Number decisions sequentially (ADR-001, ADR-002, etc.)
- Always include date for context
- Be honest about trade-offs (use ✅ and ❌)
- Keep alternatives brief but clear
- Update decisions if they're revisited/changed
- Focus on "why" not "how" (implementation details go elsewhere)
