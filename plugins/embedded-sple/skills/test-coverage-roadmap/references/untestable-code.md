# Untestable Code — the NOT_TESTABLE Register

Detail behind the rule in `SKILL.md` → *Untestable Code (NOT_TESTABLE Register)*. Read this when
classifying a line, when writing an entry, or when a reviewer asks why the gap is allowed to stand.

## Why the register exists at all

Some uncovered lines cannot be reached by any test. A coverage target that treats them as work
leaves two ways out, and both are bad: write a test that only pretends to reach the line, or break
the rule that says the target must be met. The register is the third way — say which lines they
are, why, and with what evidence.

> **The reported coverage is never adjusted.** The raw value from `coverage.json` stays the number,
> so it remains comparable across sessions and against other components. The register sits beside
> it as the explanation, never inside the arithmetic.

## Exactly two reasons

| Reason | When it applies | Evidence required |
|--------|-----------------|-------------------|
| `DEFENSIVE_BY_DESIGN` | The branch exists because a checklist demands it — for example the `default:` case of an `enum` switch. Reaching it needs a state the type system rules out. | The checklist item that demands the branch (`c-code-review-comprehensive` → `checklists/defensive-programming-checklist.md`) |
| `UNREACHABLE_DEFECT` | The code is genuinely dead: a `static-code-analysis` UNR finding, or MISRA C:2012 Rule 14.1 (checklist item `#26`). | The finding ID or the rule number |

**Never invent a third reason.** If neither fits, the code is testable and belongs in a step. A
claim without the evidence above is not an entry — it is a guess, and a guess that lowers the bar.

## `UNREACHABLE_DEFECT` is a defect, not a result

Dead code gets removed, not documented forever. This skill does **not** remove it: it measures and
tests. Record the entry, state that removal is recommended, and hand the removal to the
`modernization-roadmap` skill.

Say the consequence plainly in the step documentation: until that happens, those lines stay in the
register **and the component keeps a defect**. An entry of this kind is a parking space, not a
resolution, and a register full of them means the component was never cleaned up.

## Approval

A candidate is found in Step 2.1a, enters the plan in Step 2.2 and is approved **together with the
plan** in Step 2.3 — the same mechanism the skill already uses for the A/B decision on a spec
conflict. No separate checkpoint: an extra one would buy nothing, because the human is reading the
plan anyway and the entry is part of it.

The register as a whole is confirmed once more in Phase 3, before `status: COMPLETED` is set. That
second look is deliberate. Entries accumulate one step at a time, each one reasonable on its own,
and the only moment anyone sees the whole list is when it is about to justify closing the roadmap.

## Worked example

A component reaches 84.2 % line coverage against a 90 % target. Two entries account for the rest:

| Location | Lines | Reason | Evidence | Approved |
|----------|-------|--------|----------|----------|
| `power_button.c:210` (`default:` case) | 3 | `DEFENSIVE_BY_DESIGN` | defensive-programming-checklist: enum values validated | 2026-05-04 |
| `power_button.c:415-419` | 5 | `UNREACHABLE_DEFECT` | UNR-118 — removal recommended, handed to `modernization-roadmap` | 2026-05-04 |

8 of the 139 lines in the component are in the register, which is 5.8 % — exactly the gap. The
roadmap may close, and it closes with a recorded defect that somebody still has to remove.
