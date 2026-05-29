---
name: build-execution
description: Centralized build execution for SPL repos. Introspects build.ps1 via Get-Help once per session, caches parameters in SQL, constructs and executes builds with the correct PowerShell workaround. Use when any skill or task needs to build, compile, install dependencies, or run selftests. Invoke with "build component", "run tests", "install dependencies", or "compile".
---

# Build Wrapper Helper

Single source of truth for invoking `build.ps1` in any SPL repository.
Other skills reference this skill instead of hardcoding build commands.

> ⚠️ **CRITICAL — Read this first**: The Copilot CLI powershell tool starts shells
> with `-NoExit`, which means **any direct invocation of `.\build.ps1` will hang
> forever**. Every build command **must** be wrapped in a child process:
> ```powershell
> pwsh -NoProfile -Command "cd <repo_root>; .\build.ps1 <args>"
> ```
> This applies to all phases — discovery, builds, installs, selftests — everything.

## Why This Skill Exists

1. The Copilot CLI `powershell` tool starts shells with `-NoExit`, causing builds to appear hung
2. `build.ps1` parameters differ between SPL repositories
3. Multiple skills duplicate build command patterns — this centralizes them

## Workflow

Follow these 3 phases **in order** every time you need to build.

### Phase 1: Discovery (Once Per Session)

First, ensure the cache tables exist (safe to call every time):

```sql
CREATE TABLE IF NOT EXISTS build_params (
    name TEXT PRIMARY KEY,
    type TEXT,
    default_value TEXT,
    description TEXT,
    position INTEGER
);

CREATE TABLE IF NOT EXISTS build_cache (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

Then check if discovery has already been done this session:

```sql
SELECT value FROM build_cache WHERE key = 'discovery_done';
```

**If result exists** (discovery already done), skip to Phase 2.

**If no result** (first build this session), run discovery:

1. Determine the repository root (git root or cwd) and store it:

```sql
INSERT OR REPLACE INTO build_cache (key, value) VALUES ('repo_root', '<absolute path to repo root>');
```

2. Run `Get-Help` to introspect `build.ps1`:

```powershell
pwsh -NoProfile -Command "Get-Help <repo_root>/build.ps1 -Full"
```

3. Parse the output. For **each parameter**, extract:
   - **Name**: from the `-paramName` header (strip the leading `-`)
   - **Type**: `SwitchParameter` if `[<SwitchParameter>]` appears, otherwise the type in brackets (e.g., `String`, `String[]`)
   - **Default value**: from the `Default value` line (empty string if blank)
   - **Position**: from `Position?` line — use the number, or NULL if `named`

4. Also read the **param block** of `build.ps1` directly (first 50 lines) to extract `HelpMessage` strings for each parameter — these are more descriptive than `Get-Help` output.

5. Insert all parameters:

```sql
INSERT OR REPLACE INTO build_params (name, type, default_value, description, position)
VALUES
    ('install', 'SwitchParameter', 'False', 'Install all dependencies required to build.', NULL),
    ('build', 'SwitchParameter', 'False', 'Build the target.', NULL),
    -- ... one row per parameter discovered
;
```

6. Mark discovery complete:

```sql
INSERT OR REPLACE INTO build_cache (key, value) VALUES ('discovery_done', 'true');
```

### Phase 2: Command Construction

1. Read the cached parameters:

```sql
SELECT name, type, default_value, description FROM build_params ORDER BY name;
```

2. Map the caller's intent to parameter values. Common mappings:

| Intent | Parameters |
|--------|-----------|
| Build unit tests for a component | `-build -buildKit test -buildType Debug -variants <V> -target <TARGET>_unittests` |
| Build all unit tests (run all) | `-build -buildKit test -buildType Debug -variants <V> -target unittests` |
| Build production | `-build -buildKit prod -variants <V>` |
| Build with reconfigure | add `-reconfigure` to any build command |
| Install dependencies | `-install` |
| Install optional deps | `-install -installOptional` |
| Run CI selftests | `-selftests` |
| Run filtered selftests | `-selftests -filter "<pattern>" -marker "<marker>"` |
| Clean build | `-clean` then re-run the build command |
| Run arbitrary command | `-command "<cmd>"` |

**Target naming convention**: CMake targets follow the filesystem path with `/` replaced by `_`.
The `<TARGET>` placeholder maps like this:

| Component path | `<TARGET>` value | Full `-target` flag |
|---------------|-----------------|-------------------|
| `components/spled` | `components_spled` | `-target components_spled_unittests` |
| `components/auto_off` | `components_auto_off` | `-target components_auto_off_unittests` |
| `components/light_controller` | `components_light_controller` | `-target components_light_controller_unittests` |

Use `-target unittests` (without a component prefix) to build and run **all** unit tests for a variant.
Use a component-specific target (e.g., `-target components_spled_unittests`) to build only that component's tests.

3. Validate: check that every parameter name used exists in `build_params`. If a parameter is unknown, **stop and report** — do not guess.

4. Construct the command string:

```
.\build.ps1 -param1 value1 -param2 value2
```

For `SwitchParameter` types, use just `-paramName` (no value).
For `String` types, use `-paramName "value"`.
For `String[]` types, use `-paramName "value1","value2"` or `-paramName "value"`.

### Phase 3: Execution

**CRITICAL**: Never run `.\build.ps1` directly in the powershell tool's shell.
The tool starts `pwsh.exe -NoExit` which never terminates.

**Always** spawn a child process:

```powershell
pwsh -NoProfile -Command "cd <repo_root>; .\build.ps1 <constructed args>"
```

**Execution parameters for the `powershell` tool:**
- `mode`: `"sync"`
- `initial_wait`: `300` (builds can take minutes, especially with `-reconfigure`)
- Give the shell a descriptive `shellId` like `"build-component-name"`

**After execution:**

- **Exit code 0** → Success. Report a one-line summary (e.g., "Build succeeded, all tests passed").
- **Exit code != 0** → Failure. Search the output for lines containing `error:`, `FAILED`, or `fatal`. Report the extracted error lines to the caller. If output is large, use `Select-String` to filter:

```powershell
Select-String -Path "<temp output file>" -Pattern "error:|FAILED|fatal" | Select-Object -First 10 -ExpandProperty Line
```

## PowerShell Workarounds

These are hard-won lessons — do NOT skip them:

1. **Always use `pwsh -NoProfile -Command "..."`** — the powershell tool's shell has `-NoExit` and will never terminate
2. **Use `initial_wait: 300`** — first builds with `-reconfigure` can take 5+ minutes (CMake configure + compile)
3. **Use `-reconfigure`** when `CMakeLists.txt` files have been modified (e.g., uncommenting `spl_add_test_source`)
4. **Check exit codes** — a build that produces output but exits with code 1 has failed
5. **Large output** — build output can exceed tool limits. When this happens, the output is saved to a temp file. Use `Select-String` to extract errors rather than reading the whole file.

## Cross-Skill Integration

Other skills should reference this skill with:

```markdown
> **BUILD**: When you need to build or compile, invoke the `build-execution` skill.
```

When you encounter this directive in another skill:
1. Load this skill (if not already loaded)
2. Run Phase 1 (discovery — skipped if cached)
3. Run Phase 2 (construct command from the calling skill's context)
4. Run Phase 3 (execute and report result)

## Quick Reference

After discovery, use this decision tree:

```
Need to build?
├── All unit tests:  -build -buildKit test -buildType Debug -variants <V> -target unittests
├── Component tests: -build -buildKit test -buildType Debug -variants <V> -target components_<path>_unittests
├── Integration:     -build -buildKit test -buildType Debug -variants <V> -target integration_<subsystem>_test
├── Production:      -build -buildKit prod -variants <V>
├── Reports:         -build -buildKit test -variants <V> -target components_<path>_report
├── All targets:     -build -buildKit <kit> -variants <V>
├── Clean + build:   -clean, then re-run build command
└── Reconfigure:     add -reconfigure to any build command (required after CMakeLists.txt changes)

Target naming: replace / with _ in the component path
  components/auto_off → components_auto_off_unittests

Need to install?
├── All deps:       -install
├── Optional deps:  -install -installOptional
└── VS Code:        -installVSCode

Need to test?
├── All CI tests:   -selftests
├── Filtered:       -selftests -filter "<pattern>"
└── By marker:      -selftests -marker "<marker>"
```

> **NOTE**: This quick reference is a convenience summary. The actual parameter names and
> defaults come from the discovery phase. If this repo's `build.ps1` has different parameters,
> discovery will detect that and the SQL cache will reflect the real parameters.
