
# Clang-Tidy Linter Bundle (Embedded C / BARR-C baseline)

This bundle installs into a project as:

- `.clang-tidy` -> repository root (clang-tidy discovers it automatically) [3](https://lindevs.com/generate-json-compilation-database-using-cmake)[4](https://developers.redhat.com/blog/2020/03/26/static-analysis-in-gcc-10)
- `tools/run-lint.sh` -> project `tools/`

## Requirements

- `clang-tidy` installed
- A compilation database `compile_commands.json` available.
  - clang-tidy locates it using `-p <build-dir>`. [5](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)[4](https://developers.redhat.com/blog/2020/03/26/static-analysis-in-gcc-10)

### CMake tip

Configure with compilation database export enabled to generate `compile_commands.json` in the build directory. [8](https://dotclaude.com/skills)

## Run

```bash
tools/run-lint.sh build
# export suggested fixes:
tools/run-lint.sh build --fixes clang-tidy-fixes.yaml
```

## Common tweaks

- Change roots scanned: `--roots "src include drivers"`
- Change which headers produce diagnostics by editing `HeaderFilterRegex` in `.clang-tidy`.
