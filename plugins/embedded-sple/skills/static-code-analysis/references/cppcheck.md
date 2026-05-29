# Cppcheck Workflow

Tool-specific workflow for running Cppcheck static analysis on C components.
Three invocation methods are supported — the agent must determine which is available and appropriate.

## Table of Contents

- [Prerequisites (all methods)](#prerequisites-all-methods)
- [Step C1: Determine Invocation Method](#step-c1-determine-invocation-method)
- [Method A: CLI (Direct Invocation)](#method-a-cli-direct-invocation)
- [Method B: VS Code Extension](#method-b-vs-code-extension)
- [Method C: SPL Extension](#method-c-spl-extension-sple-static-analysis-extension)
- [Common Cppcheck Check IDs](#common-cppcheck-check-ids)
- [Cppcheck Severity Levels](#cppcheck-severity-levels)
- [Suppression Comment Format](#suppression-comment-format)

## Prerequisites (all methods)

- Cppcheck installed and available on PATH: `scoop install cppcheck@2.15.0`
  - Supported versions: 2.15.0, 2.16.0, 2.18.0
- `compile_commands.json` available in the build directory
- Component source paths known

## Step C1: Determine Invocation Method

> **Recommendation**: If `cppcheck` is available on PATH (`Get-Command cppcheck`), prefer
> **Method A (CLI)** — it's the simplest, fastest, and requires no project-level configuration
> changes. Only use Method C if the user explicitly needs SPL Extension integration (e.g., for
> team-consistent reports or variant-specific component filtering).

Ask the user which method to use:

| Method | When to use | Prerequisites |
|--------|-------------|---------------|
| **A. CLI** ⭐ | Direct invocation, full control, CI/local dev | `cppcheck` on PATH |
| **B. VS Code Extension** | Inline diagnostics in editor, on-save analysis | Extension installed + configured |
| **C. SPL Extension** (`sple-static-analysis-extension`) | Integrated into SPL build system, per-variant config | Extension installed via pip, `static_analysis.json` configured, CMake setup |

---

## Method A: CLI (Direct Invocation)

### A1: Run Analysis

```powershell
cppcheck --project=./build/compile_commands.json `
    --enable=all `
    --xml `
    --output-file=./build/cppcheck_results.xml `
    components/<component>/src/
```

**Key flags:**

| Flag | Purpose |
|------|---------|
| `--project=<file>` | Use compilation database (compile_commands.json) |
| `--enable=all` | Enable all checks (warning, style, performance, portability, information) |
| `--xml` | XML output format (machine-readable) |
| `--output-file=<file>` | Write results to file |
| `--suppress=<id>` | Suppress specific check by ID |
| `--inline-suppr` | Respect inline suppression comments in source |
| `--std=c11` | Specify C standard (adjust to project) |
| `--force` | Check all configurations |
| `--rule-file=<file>` | Load custom rules (XML format) |
| `--addon=<name>` | Load addon (e.g., `misc.py`, `misra.json`) |

### A2: Retrieve Findings

```powershell
# Parse XML results
[xml]$results = Get-Content ./build/cppcheck_results.xml
$results.results.errors.error | Select-Object id, severity, msg, file, line
```

### A3: Generate HTML Report (optional)

```powershell
cppcheck-htmlreport --file=./build/cppcheck_results.xml `
    --report-dir=./build/reports/cppcheck/ `
    --source-dir=.
```

---

## Method B: VS Code Extension

> **Note**: This method has not been validated in our environment. The information below
> is based on general VS Code cppcheck extension behavior. Verify with the actual installed
> extension before relying on these instructions.

### Known Extensions

| Extension | ID | Notes |
|-----------|-----|-------|
| Cppcheck (matthewferreira) | `matthewferreira.cppcheck` | Lightweight CLI wrapper |
| C/C++ Advanced Lint | `jbenden.c-cpp-flylint` | Integrates cppcheck + clang-tidy |

### B1: Verify Configuration

Check `settings.json` for cppcheck extension settings (exact keys depend on installed extension):

```json
{
    "cppcheck.enable": true,
    "cppcheck.executablePath": "cppcheck",
    "cppcheck.args": ["--enable=all", "--std=c11"]
}
```

### B2: Trigger Analysis

- **Automatic**: Extensions typically analyze on file save
- **Manual**: Command Palette → search for "Cppcheck" or "Lint" commands
- Exact command IDs vary by extension (e.g., `cppcheck.runAnalysis` or `c-cpp-flylint.analyzeWorkspace`)

### B3: Retrieve Findings

Findings appear in the VS Code **Problems panel** as diagnostics:

```text
get_errors(filePaths: ["components/<component>/src/"])
```

> ⚠️ **Validation needed**: Before relying on this method, confirm:
> 1. Which extension is installed (`Extensions` panel → search "cppcheck")
> 2. That findings actually appear in Problems panel for your project
> 3. What command palette commands are available

---

## Method C: SPL Extension (`sple-static-analysis-extension`)

This method integrates cppcheck into the SPL build system via CMake targets.
It provides per-variant configuration, HTML reports, and consistent team-wide analysis.

### C1: Verify Extension is Installed

```powershell
# Check if sple_static_analysis.exe is available
Get-Command sple_static_analysis.exe
# Or check pip
pip show sple-static-analysis-extension
```

### C2: Configure `static_analysis.json`

The config file lives in the variant folder. Ensure `"tool": "cppcheck"` is set:

```json
{
    "tool": "cppcheck",
    "components": [
        "src_App_main",
        "src/App/<Component>"
    ],
    "paths": [
        "legacy/Customer/variant/App/someFolder",
        "legacy/Customer/variant/App/someFolder/*"
    ],
    "machine_readable_output": true,
    "cppcheck_settings": {
        "rule_files": [
            "path/to/cppcheck_rules.xml"
        ],
        "add_ons": [
            "misc.py"
        ]
    }
}
```

**Configuration fields:**

| Field | Type | Description |
|-------|------|-------------|
| `tool` | string | Must be `"cppcheck"` |
| `components` | list | CMake target names to analyze |
| `paths` | list | Source path patterns (glob/regex) to include |
| `machine_readable_output` | bool | Generate XML output alongside HTML |
| `cppcheck_settings.rule_files` | list | Custom rule XML files |
| `cppcheck_settings.add_ons` | list | Cppcheck addons (e.g., `misc.py`, MISRA addon JSON) |

### C3: Reconfigure CMake

After editing `static_analysis.json`, the user must reconfigure:

> **Ask the user:**
> 1. Open Command Palette → **"CMake: Delete Cache and Reconfigure"**
> 2. Wait for configuration to complete
> 3. Confirm when done

This regenerates CMake targets including the `static_analysis` build target.

### C4: Run Analysis via Build Target

> **Ask the user:**
> 1. In the VS Code **CMake status bar**, select the `static_analysis` build target
> 2. Click **Build** (or Command Palette → "CMake: Build")
> 3. Wait for the build/analysis to complete
> 4. Confirm when done

### C5: Retrieve Findings

**HTML report** (for browsing):
```
build/<variant>/<build_kit>/reports/static_analysis/cppcheck/index.html
```

**XML output** (for parsing, if `machine_readable_output: true`):
```powershell
# Find generated XML
Get-ChildItem -Path ./build/ -Filter "*.xml" -Recurse | Where-Object { $_.FullName -match "cppcheck" }
```

**CLI alternative** (if extension is installed but user prefers terminal):
```powershell
sple_static_analysis.exe run `
    --build-dir ./build `
    --compile-commands ./build/compile_commands.json `
    --tool cppcheck `
    --project-root-dir $PWD `
    --sca-json-file ./static_analysis.json `
    --component <COMPONENT> `
    --variant <VARIANT>
```

**Required parameters:**

| Parameter | Description |
|-----------|-------------|
| `--build-dir` | Build output directory |
| `--compile-commands` | Path to `compile_commands.json` |
| `--tool` | Analysis tool (`cppcheck` or `polyspace`) |
| `--project-root-dir` | Project root directory |
| `--sca-json-file` | Path to `static_analysis.json` configuration file |

**Optional parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--component` | None | Specific CMake target/component to analyze |
| `--variant` | None | Variant name for variant-specific analysis |

### C6: Revert `static_analysis.json`

If `static_analysis.json` was modified in Step C2 (e.g., changed `"tool"` from `"polyspace"` to `"cppcheck"`), **revert it to its original state** after analysis completes.

```powershell
# If git-tracked, restore original
git checkout -- <path/to/variant>/static_analysis.json
```

If the file is not git-tracked, the agent must:
1. **Back up** the original content before editing (store in memory or a temp variable)
2. **Restore** the original content after findings are retrieved in Step C5

> ⚠️ **Do NOT leave `static_analysis.json` modified.** The change was only needed to trigger
> cppcheck analysis. Leaving it altered may break subsequent Polyspace runs or confuse
> other team members.

---

## Common Cppcheck Check IDs

| ID | Category | Description |
|----|----------|-------------|
| `nullPointer` | Error | Null pointer dereference |
| `uninitvar` | Error | Uninitialized variable |
| `memleak` | Error | Memory leak |
| `bufferAccessOutOfBounds` | Error | Buffer overflow |
| `divisionByZero` | Error | Division by zero |
| `unusedFunction` | Style | Function never called |
| `unusedVariable` | Style | Variable never used |
| `redundantAssignment` | Style | Value overwritten before use |
| `constParameter` | Style | Parameter can be const |
| `knownConditionTrueFalse` | Style | Condition always true/false |

## Cppcheck Severity Levels

| Severity | Description |
|----------|-------------|
| `error` | Bug found (definite or very likely) |
| `warning` | Suggestion to prevent a bug |
| `style` | Code cleanup / stylistic issue |
| `performance` | Suggestion for performance improvement |
| `portability` | Portability issue |
| `information` | Informational message |

## Suppression Comment Format

```c
// cppcheck-suppress nullPointer
ptr->field = value;

// cppcheck-suppress [nullPointer, uninitvar]
// Multi-suppression on next line
```

**Suppression file** (`cppcheck_suppressions.txt`):
```
// Suppress by ID and location
nullPointer:components/module/src/file.c:42
// Suppress by ID globally
unusedFunction
```
