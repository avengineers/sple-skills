# sple-skills

Agent skills for embedded software product line engineering. Skills follow the [Agent Skills specification](https://agentskills.io) and work across multiple AI coding agents (Copilot CLI, VS Code Copilot, Claude Code).

## Installation

### Copilot CLI

```
/plugin marketplace add https://github.com/avengineers/sple-skills.git
/plugin marketplace browse sple-skills
/plugin install embedded-sple@sple-skills
```

### Claude Code

```
/plugin marketplace add https://github.com/avengineers/sple-skills.git
/plugin install embedded-sple@sple-skills
```

### VS Code

Add to your `settings.json`:

```json
"chat.plugins.marketplaces": [
    "https://github.com/avengineers/sple-skills.git"
]
```

Then open Extensions view, search `@agentPlugins`, and install from the list.

## Available Skills

**Code Review & Quality:**

| Skill | Description |
|-------|-------------|
| **c-code-review-checklist** | CHK_Code review checklist for C components |
| **c-code-review-comprehensive** | Deep review using BARR-C:2018, MISRA C:2012, HIS Metrics |
| **c-architecture-review** | Component architecture, modularity, and coupling analysis |
| **his-metrics** | HIS (Herstellerinitiative Software) metrics calculation |

**Testing:**

| Skill | Description |
|-------|-------------|
| **c-unit-testing** | GTest/GMock unit testing with Arrange-Act-Assert |
| **c-integration-testing** | BDD-style integration tests for embedded C components |
| **test-coverage-roadmap** | Systematic plan to achieve 95%+ test coverage |

**Static Analysis:**

| Skill | Description |
|-------|-------------|
| **static-code-analysis** | Run Polyspace As You Code and analyze findings |
| **polyspace-baseline** | Download Polyspace baselines for comparison |
| **c-coding-standards** | BARR-C:2018 bug-reducing rules and MISRA best practices |

**Build & Dependencies:**

| Skill | Description |
|-------|-------------|
| **build-execution** | Centralized build execution for SPL repos |
| **install-dependencies** | Manage project dependencies using the bootstrap system |

**Development Workflows:**

| Skill | Description |
|-------|-------------|
| **conventional-commits** | Conventional commit messages with JIRA issue extraction |
| **retrospective** | Structured retrospectives after development phases |
| **project-knowledge-base** | Maintain project context with decisions, bugs, and issues |
| **modernization-roadmap** | Systematic legacy C component modernization |

## Contributing

Submit a pull request with your skill following the [Agent Skills specification](https://agentskills.io).

## License

MIT
