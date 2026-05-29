---
name: c-architecture-review
description: Analyze C component architecture — modularity, coupling, cohesion, and architectural smells. Use when evaluating structural quality, dependency direction, component integration, or identifying architectural risks. Invoke with "review architecture", "analyze structure", "check modularity", "evaluate coupling", or "dependency analysis". This skill owns all coupling, cohesion, and architectural smell analysis — other review skills delegate here instead of duplicating this work.
---

# C Architecture Review

Analyzes architectural quality of C components: modularity, coupling, cohesion, and integration patterns.

## Communication Style

Follow the guidelines in [shared communication style](../shared/review-common/communication-style.md).

## Review Dimensions

### 1. Modularity

- **File organization**: Logical grouping of functions and data
- **Header/source separation**: Clean public API in headers, implementation in sources
- **Single responsibility**: Each module handles one concern

### 2. Coupling (Dependencies)

- **Afferent coupling (Ca)**: Who depends on this module?
- **Efferent coupling (Ce)**: What does this module depend on?
- **Instability (I)**: Ce / (Ca + Ce) — higher = more unstable
- **Types of coupling** (worst to best):
  - Content coupling (directly accessing internals)
  - Common coupling (shared global data)
  - Control coupling (passing control flags)
  - Stamp coupling (passing whole structures when only part needed)
  - Data coupling (passing only needed data) ✅

### 3. Cohesion

- **Functional cohesion** (best): All elements contribute to single task
- **Sequential cohesion**: Output of one element is input to next
- **Communicational cohesion**: Elements operate on same data
- **Temporal cohesion**: Elements grouped by when they execute
- **Logical cohesion**: Elements grouped by category, not function
- **Coincidental cohesion** (worst): No meaningful relationship

### 4. Architectural Patterns

- **Layered architecture**: Clear separation of concerns
- **Component interfaces**: Well-defined public APIs
- **Dependency direction**: Dependencies flow one way (no cycles)

## Workflow

0. **Collect review context**: Follow [Review Context Workflow](../shared/review-common/review-context-workflow.md) — collect git metadata, populate protocol header, enumerate source files.

1. **Map component structure**: Identify files, modules, and their relationships
2. **Analyze dependencies**: Build dependency graph, identify coupling
3. **Evaluate cohesion**: Assess how well-grouped responsibilities are
4. **Identify anti-patterns**: Look for architectural smells
5. **Assess integration**: How does this fit in the larger system?
6. **Document findings**: Provide actionable improvement recommendations
7. **Record end time**: Follow the "Recording End Time" section in the [Review Context Workflow](../shared/review-common/review-context-workflow.md).

## Architectural Smells to Detect

| Smell                     | Description                         | Impact                             |
|---------------------------|-------------------------------------|------------------------------------|
| **God Module**            | One file does everything            | Hard to test, modify, understand   |
| **Shotgun Surgery**       | Change requires touching many files | High change risk                   |
| **Feature Envy**          | Module uses more of another's data  | Wrong responsibility placement     |
| **Circular Dependencies** | A→B→C→A                             | Build order issues, tight coupling |
| **Leaky Abstraction**     | Internal details exposed            | Fragile interfaces                 |
| **Dead Code**             | Unreachable or unused code          | Maintenance burden                 |
| **Copy-Paste Code**       | Duplicated logic                    | Inconsistent fixes                 |

## Usage

```text
"Review architecture of components/light_controller/"
"Analyze coupling and cohesion of auto_off module"
"Identify architectural risks in this component"
"Check for circular dependencies"
```

## Output Format

```markdown
## Architecture Review

### Component: StateMgr

#### Structure Overview
- **Files**: 3 source files, 2 headers
- **Lines of Code**: 4,880 total
- **Public Functions**: 12
- **Internal Functions**: 34

#### Coupling Analysis
| Dependency | Type | Direction | Assessment |
|------------|------|-----------|------------|
| StdTypes | Data | Inbound | ✅ Appropriate |
| auto_off | Common | Bidirectional | ⚠️ Circular |

#### Cohesion Assessment
- **StateMgr.c**: Functional cohesion (Good)
- **StateMgr_Internal.c**: Logical cohesion (Could improve)

#### Architectural Concerns
1. **Circular dependency with auto_off**
   - Impact: Build complexity, tight coupling
   - Recommendation: Extract shared functionality to common module

2. **File size exceeds maintainability limit (4,880 lines)**
   - Impact: Hard to navigate, test, and modify
   - Recommendation: Split by functional area
```

## Definition of Done (DoD)

An architecture review is considered **complete** when the following criteria are met:

| # | Criterion | Description |
|---|-----------|-------------|
| 0 | **Review Context Collected** | Git metadata (branch, commit hash, author, Jira ticket, branch type) read and filled into protocol header |
| 1 | **All Reviewed Files Listed** | Every individual `.c` and `.h` file that was opened and read is listed by full path in the protocol header |
| 2 | **Structure Mapped** | Files, modules, public/internal functions, and lines of code documented |
| 3 | **Coupling Analyzed** | Afferent/efferent coupling measured, instability calculated, coupling types classified |
| 4 | **Cohesion Assessed** | Cohesion level evaluated for each module |
| 5 | **Architectural Smells Checked** | All smells from the catalogue (God Module, Shotgun Surgery, etc.) evaluated |
| 6 | **Review Protocol Created** | Findings documented following [Report Naming Convention](../shared/review-common/report-naming-convention.md) using skill name `c-architecture-review` |
| 7 | **Recommendations Provided** | Each finding has actionable improvement recommendations |
| 8 | **Review Duration Documented** | Start time, end time, and total duration recorded in the protocol header |

## Save Report

Follow the [Report Naming Convention](../shared/review-common/report-naming-convention.md).

Skill name for filename: `c-architecture-review`

When invoked by `c-code-review-comprehensive`, results are embedded in the comprehensive report instead — do not save a separate file.

## Project Memory Integration

After completing an architecture review, document significant findings using the `project-knowledge-base` skill:

- **Architectural decisions made** → `doc/project_notes/decisions.md` (as ADRs)
- **Structural issues identified** → `doc/project_notes/bugs.md`

> **SKILL REFERENCE**: Use the `project-knowledge-base` skill to ensure findings persist across sessions.
