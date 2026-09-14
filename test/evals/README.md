# Trigger evals

Does the right skill get picked for a prompt? That question cannot be answered by reading a skill,
because the deciding text is the `description` in its frontmatter, and a description that reads
better may trigger worse. These sets measure it.

```bash
python scripts/trigger_eval.py test/evals/test-coverage-roadmap.json --runs 3 --model sonnet
```

**Run by hand, never in the pipeline.** Every case costs one model call per run, so a set of six
cases at three runs is eighteen calls. The structural checks in `test/skills/` are the ones that
belong in CI; these cost money and are not deterministic.

## When to run one

- **Before changing a `description`.** Measure, change, measure again. A rewrite that stops a skill
  triggering is worse than the wording problem it fixed.
- **After a mix-up in daily use.** Add the prompt that went wrong as a case, with the expectation
  it should have met. The sets grow from real friction, not from imagination.

## Two rules that were learned the expensive way

**Change one description per measurement.** Three of these descriptions were rewritten together
once. One case looked like a clear win, 0/3 before against 2/3 after, and that number decided which
rewrite was kept. It was wrong: the case had been measured next to two other rewrites, and those
were reverted in the same commit. Measured again against the text it actually ships next to, the
new wording reached 3/7 and the old one 4/7 — the win did not exist. A skill's description competes
with its neighbours, so the tree under test has to be the tree that ships.

**Near the threshold, three runs decide nothing.** Not a rule of thumb — measured. The same case,
the same description, the same tree, an hour apart: **4/7 once and 0/3 the next time**. Both are
ordinary draws from a rate near 0.4; at that rate three runs come back empty about one time in five.
So a case in the middle carries an uncertainty of roughly ±30 points at three runs, which is wider
than any wording change this repo has ever produced.

What follows for the run count:

| What you want to know | Runs |
| --- | --- |
| Does it fire at all, or always? | 3 |
| Is one wording better than another? | 10 per wording, and expect to need more |
| Is a middling case really middling? | 10 |

Three runs over nine cases is a cheap screening pass and nothing more: it finds the cases worth a
real measurement. It cannot rank two descriptions, and a table of 3-run numbers must never be read
as a before/after comparison.

## Writing a set

A set names one skill and a list of cases. `should_trigger: false` matters as much as `true` — the
skills in this plugin overlap on purpose, and a negative case is what pins the boundary:

```json
{
  "skill": "test-coverage-roadmap",
  "cases": [
    { "query": "improve unit test coverage for components/auto_off to 90%", "should_trigger": true },
    { "query": "write a unit test for the function AutoOff_Init", "should_trigger": false }
  ]
}
```

`about` and `why` are free text for the reader and are ignored by the runner. Use them — a case
whose point nobody remembers gets deleted the first time it fails.

### A cluster of skills in one set

Where several skills compete, the question is not whether one fires but **which**. Name the winner
per case with `expect`, and a single run covers the whole cluster instead of one run per skill —
three times cheaper for the three review skills:

```json
{
  "skill": "c-code-review-checklist",
  "cases": [
    { "query": "review this PR", "expect": "c-code-review-checklist" },
    { "query": "assess the technical debt here", "expect": "c-code-review-comprehensive" },
    { "query": "check the coupling between these components", "expect": "c-architecture-review" }
  ]
}
```

`expect` implies the named skill should trigger, so `should_trigger` can be left out. A case still
needs one of the two.

## Where these sets stand today

`review-cluster.json` **does not pass, and is not meant to yet.** It is checked in red on purpose:
the cases record what the skills should reach, and four of them are open questions rather than
solved ones. Without this section a red run looks like a broken repository.

Measured 2026-09-14 on `sonnet`, against the descriptions in this tree:

| Case | Expected | Result | What the failure means |
| --- | --- | --- | --- |
| review the code in components/auto_off | checklist | 10/10 | — |
| run the CHK_Code checklist on power_button.c | checklist | 3/3 | — |
| do a comprehensive review of the diagnostics component | comprehensive | 3/3 | — |
| check the coupling between auto_off and power_button | architecture | 3/3 | — |
| analyze the dependency direction between the components | architecture | 1/3 – 3/3 | noisy, screening only |
| review this PR | checklist | 0/3 | `code-review` and `review-pr` from other plugins win. Probably correct — decide whether an embedded-C skill should own a plugin-agnostic request at all |
| we are about to refactor this module, assess its technical debt first | comprehensive | 0/10 | `modernization-roadmap` wins, and it *starts with a comprehensive review*. The expectation in the set may be the thing that is wrong |
| I am new to this component and need a full quality assessment | comprehensive | 0/10 | nothing wins it — no skill is invoked at all |
| is this component too tightly bound to the hardware layer | architecture | 0/3 – 4/7 | nothing wins it either |

The last two share one signature: the prompt describes a **situation** instead of naming a review,
and the agent answers in prose rather than routing. Suspect the harness before the descriptions —
a run denies the exploring tools, so a situational question does not have to go anywhere. Until
someone repeats those cases with `Read`, `Glob` and `Grep` allowed against real C components, it is
not known whether they are measurable at all.

Two rewrites of the descriptions have been tried against these cases and both moved nothing, at
about fifty model calls each. **Do not attempt a third before the experiment above.**

`test-coverage-roadmap.json` passed when it was last measured, but not since this tree changed.

## Reading the result

A case passes when the trigger rate reaches the threshold (`--threshold`, 0.5 by default); a
negative case passes when it stays below. The report also lists which *other* skills a query pulled
in, which is usually the more interesting half: it names the competitor.

## It measures this working tree, not the installed plugin

By default the CLI loads the plugin **installed for the account**, which is the released version.
Editing a description here would then change nothing the run can see, and a before/after comparison
would compare the released text with itself. That happened once and the result looked entirely
plausible — the two descriptions differed by exactly the sentence under test.

The runner therefore passes `--plugin-dir plugins/embedded-sple` and **verifies from the run's own
init event** that the plugin really came from there, aborting if it did not. Override with
`--plugin-dir` to measure a different checkout; there is no way to switch the check off, because a
silently wrong measurement is worse than none.

## What the number does not say

- **It is specific to one model.** Trigger behaviour differs between them, so a result from
  `--model haiku` says nothing about the model people actually use. The model is printed in the
  report for that reason.
- **It is specific to the environment it ran in.** The runner sees every plugin installed for the
  account, so unrelated skills appear among the competitors. For a measurement of this plugin
  alone, run it where only this plugin is installed.
- **It is a sample, not a proof.** Three runs on a borderline description can differ. Raise
  `--runs` before trusting a small difference.
- **The agent runs with its exploring tools denied**, so it either invokes a skill or answers in
  prose. That isolates the routing decision and keeps a run affordable, but it is not what a full
  session would do.
- **It stops at the routing decision.** Whether the agent then works the way the skill demands —
  reads the body, keeps the order of the steps, does not shortcut the checkpoints — is invisible
  here. Answering that needs a fixture repository and a judge; the method is in
  `superpowers:writing-skills` → `testing-skills-with-subagents.md`.

## A description that summarises the workflow

`writing-skills` warns against it, and the first reading of that warning was that such a
description makes the skill trigger **too often**. That was measured, and it is wrong: the long
descriptions in this plugin hold all their positive cases and all their negative ones, and the
review cluster fails the other way round — too little reach, not too much. The real risk in that
warning is the agent following the summary instead of reading the body, and no trigger eval can
see it. So there is no character limit and no "description shape" check in `test/skills/`; adding
one would measure a problem that was looked for and not found.
