---
name: retrospective
description: Facilitate structured retrospectives after development phases, sprints, or milestones to capture learnings and drive improvement. Use when asked to "run retrospective", "reflect on this phase", "what did we learn", "sprint review", "lessons learned", or "what should we do differently". Also use when the user finishes a significant block of work and should reflect before moving on — especially after resolving hard bugs, completing refactoring, or hitting (or missing) targets.
---

# Retrospective Facilitator

## Context

This skill facilitates **solo developer retrospectives** — an individual reflecting on their own work with AI assistance. The tone is direct and practical, not a group workshop. Think of it as a structured debrief between you and the developer.

## Why Retrospectives Matter in Embedded

Embedded development has long feedback loops. A bug in interrupt priority ordering might not surface until integration testing weeks later. A toolchain upgrade that seemed fine breaks MISRA compliance in subtle ways. Without deliberate reflection, these learnings evaporate between sessions and developers repeat the same mistakes.

A good retrospective is not a checkbox exercise. It's the mechanism that turns individual experience into persistent knowledge. The output feeds into `doc/project_notes/` so future sessions — human or AI — benefit from what was learned.

## Starting the Conversation

Open with concrete questions to establish scope. Don't start with the template — start with curiosity:

- "Which phase or sprint are we looking back on? What were you trying to accomplish?"
- "How do you feel it went overall — before we dig into details?"
- "Were there any moments where things went sideways, or where you were surprised?"

These opening questions set the tone: this is a reflection, not a report. Let the developer's answers guide which dimensions deserve depth.

## Facilitation Process

The retrospective is a conversation, not a form to fill out. The steps below are a guide, not a checklist — skip or compress dimensions that have no substance, and spend extra time where there's real insight to uncover.

1. **Establish context** — What phase/work is being retrospected? What were the goals? What was actually accomplished?
2. **Explore dimensions** — Successes, challenges, learnings, and surprises. Not all are equally relevant every time. If the developer has nothing meaningful to say about "surprises," move on.
3. **Review metrics** — Look at quantitative data that tells a story (see embedded-relevant metrics below). Only if data is available or estimable.
4. **Identify patterns** — Compare against previous retrospectives. Are the same issues recurring?
5. **Define action items** — Concrete, specific, measurable next steps.
6. **Assess and close** — Confidence for next phase, key risks.

Aim for **5-10 focused questions** total. This should feel like a 5-15 minute reflection, not an exhaustive interview.

### Handling Shallow Responses

If the developer gives surface-level answers ("everything went fine", "nothing to improve"), probe deeper:

- "What took longer than you expected?"
- "If you had to redo this phase, what would you change on day one?"
- "Which part of the code are you least confident about?"
- "Was there anything you had to look up or figure out that you didn't expect?"

The point is not to force negativity — some phases genuinely go well. But even successful phases have learnings worth capturing. A retro that produces zero action items probably wasn't deep enough.

## Embedded-Relevant Metrics

Skip vanity metrics (LoC, commit count). Focus on what actually indicates embedded development health:

| Metric | What it tells you |
|--------|-------------------|
| **Test Coverage** (statement/branch) | How much code is exercised by automated tests |
| **MISRA Compliance Rate** | Violations reduced vs. previous phase |
| **HIS Metrics** (v(G), call depth, paths) | Complexity trend — are functions getting simpler? |
| **Stack/RAM Usage** | Resource headroom — are we approaching limits? |
| **Defect Escape Rate** | Bugs found on hardware vs. caught in CI/test |
| **Static Analysis Findings** | Polyspace/Cppcheck new vs. resolved findings |
| **Build Time** | CI pipeline health — has it gotten slower? |

Not all metrics apply to every retro. Pick 2-4 that are relevant to the completed work. The developer may not have exact numbers — estimates and trends ("coverage went up", "fewer Polyspace findings") are perfectly fine.

## Pattern Identification

This is where retrospectives compound in value. Before writing up action items:

1. **Read previous retrospectives** — Look for `doc/retrospectives/` or ask the developer where they store them. Read the last 3 (not all of them — recency matters most).
2. **Search for recurring themes** — Is the same type of issue appearing repeatedly? (e.g., "timing issues" in 3 of 5 retros means there's a systemic problem)
3. **Check action items from last retro** — Were they actually done? If not, why?
4. **Note improvements** — What's getting better over time? Acknowledge progress.

If no previous retros exist, note this as the baseline and mention it in the output. Future retros will compare against it.

## Action Items

Good action items are specific and bounded:

- ✅ "Create mock helper for CAN message builder to reduce test boilerplate by next sprint"
- ✅ "Add Polyspace check to PR pipeline so MISRA issues surface before code review"
- ✅ "Document watchdog timing constraints in `doc/project_notes/key_facts.md`"
- ❌ "Write better code" (vague — what specifically?)
- ❌ "Improve test coverage" (how much? which modules?)

Limit to 3-5 action items. More than that and nothing gets done.

## Output

**Save to:** `doc/retrospectives/YYYY-MM-DD_<phase-name>_retro.md`

If `doc/retrospectives/` doesn't exist, check whether the project uses a different location for documentation (e.g., `docs/`, `documentation/`). If unsure, ask the developer. Create the directory once confirmed.

Follow the structure in `references/retro_output_template.md`. The template sections are a menu, not a mandate — skip any section that produced no meaningful content during the conversation. An honest 4-section retro is better than a padded 8-section one.

## Project Memory Integration

After completing the retrospective, persist key learnings into the project's knowledge base (typically `doc/project_notes/`):

- **Bugs and solutions discovered** → `bugs.md`
- **Process or design decisions** → `decisions.md`
- **Completed phase/sprint work** → `issues.md`

Format for appended entries:

```markdown
## YYYY-MM-DD — [Brief title]

[1-3 sentences capturing the insight. Include enough context that someone reading this in 6 months understands what happened and why it matters.]
```

If the `project-knowledge-base` skill is available, defer to its conventions instead. If the knowledge base files don't exist yet, create them with a short header explaining their purpose.
