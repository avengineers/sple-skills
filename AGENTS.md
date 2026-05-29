# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Overview

Collection of agent skills for embedded software product line engineering. Skills follow the [Agent Skills specification](https://agentskills.io) and work across multiple AI coding agents (Copilot CLI, VS Code Copilot, Claude Code).

## Repository Structure

```
plugins/
  embedded-sple/           # Embedded software product line engineering plugin
    plugin.json
    skills/                # Individual skill directories
      shared/              # Cross-skill shared references
      <skill-name>/
        SKILL.md           # Skill definition (frontmatter + instructions)
        references/        # Optional reference material
        scripts/           # Optional automation scripts
.github/
  plugin/
    marketplace.json       # Copilot CLI / VS Code marketplace manifest
test/                      # Pytest-based skill tests
```

## Working with Skills

Each skill is a self-contained directory with a `SKILL.md` (frontmatter + instructions) and optional `references/` and `scripts/` subdirectories.

- **SKILL.md frontmatter** must have `name` and `description` fields
- **Internal references** use relative paths (`references/template.md`, not absolute paths)
- **Cross-skill references** within a plugin use `../sibling-skill/references/file.md`
- **Shared references** for content used by multiple skills live in `skills/shared/<topic>/` and are referenced via `../shared/<topic>/file.md`

### Shared References (`skills/shared/`)

When multiple skills share common workflow logic or documentation, extract it into `skills/shared/<topic-name>/`. This avoids duplication and keeps individual skills lean.

```
plugins/embedded-sple/skills/
  shared/
    review-common/          # Shared by code review skills
    roadmap-common/         # Shared by roadmap-based skills
  my-skill/
    SKILL.md                # References: ../shared/roadmap-common/file.md
```

Guidelines:
- Shared files contain **prose and framework rules**, not executable templates with placeholders
- Each consuming skill defines its own **domain-specific bindings** (paths, metrics, thresholds)
- Keep shared files focused on one concern (e.g., workflow engine, communication style)

## Git Workflow

- Use Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`)
- Branch naming: `feature/SPLE-XXXX-short-description` or `<number>-short-description`
- Keep commits small and logical
