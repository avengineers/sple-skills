# Project Memory Setup

Read this file only when the user asks to set up or initialize project memory. Propose the steps
below as one plan, and carry them out only after the user agrees. Never run them on your own.

## 1. Create the Memory Files

```text
doc/
└── project_notes/
    ├── bugs.md         # Bug log with solutions
    ├── decisions.md    # Architectural Decision Records (ADRs)
    ├── key_facts.md    # Hardware config, toolchain, interfaces
    └── issues.md       # Work log with ticket references
```

Use `doc/project_notes/` (not `memory/`) so it reads as standard engineering documentation that
human developers will maintain alongside AI tools.

Copy initial content from the templates next to this file:

- [bugs_template.md](bugs_template.md) → `bugs.md`
- [decisions_template.md](decisions_template.md) → `decisions.md`
- [key_facts_template.md](key_facts_template.md) → `key_facts.md`
- [issues_template.md](issues_template.md) → `issues.md`

## 2. Point the Instruction File at the Memory (optional)

With this plugin installed, the skill finds `doc/project_notes/` on its own. An agent or a
colleague without the plugin finds it only if the project's instruction file (`AGENTS.md`,
`CLAUDE.md`, or `.github/copilot-instructions.md`) points to it. That file is the developer's
agent contract, not this skill's.

1. Show the section below and name the file it would go into — whichever of the three exists.
2. Use `ask_user` to ask whether to add it, and wait for the answer.
3. Write it only after the user agrees. If they decline, leave the file untouched and do not ask
   again; the memory files work without it.

If none of the three files exists, do not create one. Say that the section needs a home and let the
user decide where it goes.

```markdown
## Project Memory System

This project maintains institutional knowledge in `doc/project_notes/`.

### Memory Files

- **bugs.md** — Bug log with dates, root causes, solutions, and prevention notes
- **decisions.md** — Architectural Decision Records (ADRs) with context and trade-offs
- **key_facts.md** — Hardware config, toolchain versions, pin assignments, memory layout
- **issues.md** — Work log with ticket IDs and URLs

### When to Consult Memory

- Before proposing architectural changes → check `decisions.md`
- When encountering errors or faults → search `bugs.md`
- When needing project configuration → read `key_facts.md`
- After completing work → update `issues.md`

### Style

- Bullet lists preferred; tables are OK for structured data (memory maps, pin assignments)
- Keep entries concise (1-3 lines)
- Always include dates
- Include ticket/doc URLs where available
```
