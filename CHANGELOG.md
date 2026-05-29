# CHANGELOG


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
