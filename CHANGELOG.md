# CHANGELOG


## v0.2.0 (2026-09-24)

### Bug Fixes

- Resolve the contradictions found in the PR review
  ([`cb7a19f`](https://github.com/avengineers/sple-skills/commit/cb7a19f0c01a30e6dc03dfa17e86bda20864967a))

The coverage path, the checklist item count and two section pointers contradicted each other or the
  build that produces the data. Three checks in the suite could not fail for the case they describe:
  step 2.1 collided with 2.10 by string prefix, and a YAML block scalar walked past the description
  length check. The eval harness raised a bare KeyError for a case without a query, and could not
  find a CLI installed as claude.cmd on PATH.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

### Features

- Generalize the skill set and make the roadmap rules consistent
  ([`5221e4a`](https://github.com/avengineers/sple-skills/commit/5221e4a54b3eda0c958612af63c048de86675f4b))

Two bodies of work on the skill documents themselves.

The harvest. Five skills learned from real use in an internal project were generalized into this
  public set, with every project-specific fact left behind: c-unit-testing (hammocking,
  parameterized tests, traceability),

test-coverage-roadmap (consult the specification, choose the test level), c-integration-testing
  (spec-first, reset discipline, subsystem testing), conventional-commits (type test-only changes as
  test:), and c-code-review-checklist (interface ownership). AGENTS.md now requires code examples to
  come from the SPLED demo project, so an example can be checked instead of believed.

The consistency pass over the roadmap skills. Their rules contradicted each other and their own
  workflow steps: the required-skills tables did not match the steps they described, three different
  test file naming conventions were in use, the branch coverage gate was invisible in the definition
  of done, and both roadmap skills asked the user for facts their own roadmap document already held.
  Coverage is now reported per file and per function, the target is configurable instead of
  hard-coded at 90%, and untestable code has a documented way out.

Everything that names a tool now describes the capability instead - the documents run under more
  than one agent harness, and one host's tool names do not exist in another.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

### Testing

- Add two layers of skill validation
  ([`e2b1d54`](https://github.com/avengineers/sple-skills/commit/e2b1d54e6e0770a0518a2d11881144af72cbd904))

A skill document cannot be verified by reading it, so this adds two instruments that answer
  different questions.

Layer 1, test/skills/ - mechanical consistency, 513 checks, no model calls, milliseconds. It runs in
  the pull-request pipeline on Linux and Windows and holds the skills to their own rules: the
  definition of done rows that no document may drop, required-skills tables that match the workflow
  steps, cross-document links and section references that resolve, frontmatter fields that exist in
  the specification, documented paths that are real, and no host-specific tool names. Every check
  was written red first and then verified against a deliberate regression - five passed their own
  sabotage and had to be sharpened.

Layer 2, scripts/trigger_eval.py and test/evals/ - which skill a prompt actually reaches. The
  description in the frontmatter decides whether a skill triggers at all, and a rewrite that reads
  better may trigger worse. The harness runs the CLI with the exploring tools denied, so the agent
  either invokes a skill or answers in prose, which isolates the routing decision. It loads the
  working tree and verifies from the run's own init event that it did, because a first version
  silently measured the plugin installed for the account and compared a released description with
  itself.

This layer costs one model call per case per run and is driven by hand, never in CI. What it can and
  cannot say is written down in test/evals/README.md, including two rules that each cost a wasted
  measurement round: change one description at a time, and never rank two wordings on three runs -
  the same case on the same tree gave 4/7 and 0/3 an hour apart.

uv.lock carries the dependencies this suite needs, resolved to the current patch levels: coverage
  7.16.1 and pygments 2.21.0. The 634 tests pass on them.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

- **ci**: Enforce coverage as a hard merge gate
  ([`19b486a`](https://github.com/avengineers/sple-skills/commit/19b486a9bb289afa64fbd23f4c6cf9e73caba449))

Add codecov.yml requiring 100% coverage of changed lines (patch) and forbidding the overall coverage
  from dropping below the base commit (project), both as hard failures (informational: false).
  Mirrors the spl-core setup so either repo can serve as a template. Tests run fully in-process, so
  no coverage gap.


## v0.1.6 (2026-06-18)

### Bug Fixes

- Make Claude Code plugin manifest pass schema validation
  ([`6edade8`](https://github.com/avengineers/sple-skills/commit/6edade8bdc94957c606af639bfaec59e73d8d4f3))

The .claude-plugin/plugin.json used "skills": "skills/", which Claude Code rejects with 'skills:
  Invalid input' — the field must be a "./"-prefixed path or array, and the conventional skills/
  directory is auto-discovered anyway. Drop the field so the manifest validates; skills are still
  picked up from skills/ at the plugin root.

Also bump the copy to 0.1.5 and teach sync_version.py to keep the .claude-plugin/plugin.json version
  in lockstep with the root plugin.json, so the two manifests stop drifting on each release.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>


## v0.1.5 (2026-06-18)

### Bug Fixes

- Add plugin manifest at .claude-plugin/plugin.json for Claude Code
  ([`207dd3d`](https://github.com/avengineers/sple-skills/commit/207dd3de2b0833c45daaee1423311a01f4f63e7a))

Claude Code resolves a plugin's manifest at <source>/.claude-plugin/plugin.json, whereas the
  existing manifest only lived at <source>/plugin.json (the location Copilot CLI / the Agent Skills
  spec expect). The missing path caused a manifest error on '/plugin install
  avengineers-embedded-sple@avengineers-sple-skills'.

Keep the root plugin.json for Copilot/VS Code and add a copy under .claude-plugin/.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>


## v0.1.4 (2026-06-01)

### Bug Fixes

- Quote YAML frontmatter description in project-knowledge-base skill
  ([`5310adc`](https://github.com/avengineers/sple-skills/commit/5310adcfdef8d9b6645e2a0a1007e607424eb5b5))

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

### Documentation

- Update README install commands to use new marketplace names
  ([#1](https://github.com/avengineers/sple-skills/pull/1),
  [`2b47d69`](https://github.com/avengineers/sple-skills/commit/2b47d69b8bb7df53431ab3ef9a145ca8af95655d))

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>


## v0.1.3 (2026-05-29)

### Bug Fixes

- Rename marketplace from sple-skills to avengineers-sple-skills
  ([#1](https://github.com/avengineers/sple-skills/pull/1),
  [`0156b6b`](https://github.com/avengineers/sple-skills/commit/0156b6bc6f8717b6a45cbab0c228ab0dae4dfc7e))

Avoids name collision with internal marketplace.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>


## v0.1.2 (2026-05-29)

### Bug Fixes

- Git-add JSON manifests during version sync for semantic-release
  ([#1](https://github.com/avengineers/sple-skills/pull/1),
  [`8bc44b4`](https://github.com/avengineers/sple-skills/commit/8bc44b4b011b1df4b88cf156e489154099ed15c8))

The build_command script now stages updated JSON files so they are included in the release commit by
  python-semantic-release.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>


## v0.1.1 (2026-05-29)

### Bug Fixes

- Add tests for sync_version script and improve coverage
  ([#1](https://github.com/avengineers/sple-skills/pull/1),
  [`52a0cbf`](https://github.com/avengineers/sple-skills/commit/52a0cbf703253edfd04f611c591262494b9fc303))

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>


## v0.1.0 (2026-05-29)

### Bug Fixes

- Configure develop as release branch and add manual RC workflow
  ([#1](https://github.com/avengineers/sple-skills/pull/1),
  [`3976549`](https://github.com/avengineers/sple-skills/commit/397654942e5b189ededdf71b2589b7177d4a464c))

- Set develop as the primary release branch (full versions) - Add release-rc job for manual
  prerelease via workflow_dispatch - Reset version to 0.1.0 (remove erroneous rc.1 suffix) - Remove
  outdated junitxml path from pytest addopts

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>


## v0.1.0-rc.1 (2026-05-29)

### Bug Fixes

- Trigger CI on develop branch instead of main
  ([#1](https://github.com/avengineers/sple-skills/pull/1),
  [`8bbb165`](https://github.com/avengineers/sple-skills/commit/8bbb165bd3f2ab3e270fad5d52ef5abbd63f8850))

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

### Documentation

- Add CI, license, python and coverage badges to README
  ([#1](https://github.com/avengineers/sple-skills/pull/1),
  [`af1bd2a`](https://github.com/avengineers/sple-skills/commit/af1bd2a5674fbd20e97e09e7d623f1d6f2d107b5))

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

### Features

- Add embedded SPLE skills collection ([#1](https://github.com/avengineers/sple-skills/pull/1),
  [`7d4b4c5`](https://github.com/avengineers/sple-skills/commit/7d4b4c59b00b28c7031e007e8d05c5e51b4dd74d))

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

- Add initial repository structure and marketplace manifests
  ([#1](https://github.com/avengineers/sple-skills/pull/1),
  [`a26c737`](https://github.com/avengineers/sple-skills/commit/a26c73702a6839c83bc36154c83000c60cf0d8cd))

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

### Testing

- Add skill unit tests ([#1](https://github.com/avengineers/sple-skills/pull/1),
  [`c2ac784`](https://github.com/avengineers/sple-skills/commit/c2ac78440aa17c6da01254eb49eaa92cd6f2b4bd))

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
