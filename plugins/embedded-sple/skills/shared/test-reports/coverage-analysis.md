# Coverage Analysis for GTest Projects

Shared reference for extracting and presenting test coverage data from GTest/gcovr-based projects. Used by `c-unit-testing`, `c-integration-testing`, and `test-coverage-roadmap`.

## Report Locations

After building a `_unittests` or `_test` target with `buildKit=test, buildType=Debug`, the build system generates these artifacts:

| Artifact | Path | Description |
|----------|------|-------------|
| Coverage JSON | `build/<VARIANT>/test/Debug/<COMPONENT>/coverage.json` | Coverage data (gcovr format) |
| JUnit XML | `build/<VARIANT>/test/Debug/<COMPONENT>/junit.xml` | Test results |
| Coverage HTML | `build/<VARIANT>/test/Debug/<COMPONENT>/reports/coverage/` | Visual coverage report |

> **Important**: Coverage data is only generated in `Debug` builds. Always use `buildType=Debug`.

## Extracting Coverage from coverage.json

The `coverage.json` file uses gcovr format. This is the preferred method for automated extraction — more reliable than HTML scraping.

```powershell
$cov = Get-Content "build/<VARIANT>/test/Debug/<COMPONENT>/coverage.json" -Raw | ConvertFrom-Json

$totalLines = 0; $coveredLines = 0
$totalFuncs = 0; $coveredFuncs = 0
$totalBranches = 0; $coveredBranches = 0

foreach ($f in $cov.files) {
    foreach ($line in $f.lines) {
        $totalLines++
        if ($line.count -gt 0) { $coveredLines++ }
        if ($line.branches) {
            foreach ($b in $line.branches) {
                $totalBranches++
                if ($b.count -gt 0) { $coveredBranches++ }
            }
        }
    }
    foreach ($func in $f.functions) {
        $totalFuncs++
        if ($func.execution_count -gt 0) { $coveredFuncs++ }
    }
}

@"
              Exec    Total   Coverage
Lines:        $coveredLines`t$totalLines`t$([math]::Round($coveredLines / $totalLines * 100, 1))%
Functions:    $coveredFuncs`t$totalFuncs`t$([math]::Round($coveredFuncs / $totalFuncs * 100, 1))%
Branches:     $coveredBranches`t$totalBranches`t$([math]::Round($coveredBranches / $totalBranches * 100, 1))%
"@
```

Example output:

```text
              Exec    Total   Coverage
Lines:        722     1213    59.5%
Functions:    24      64      37.5%
Branches:     450     689     65.3%
```

## Extracting Test Results from JUnit XML

> **GTest quirk**: GTest JUnit output uses `<testsuite>` as the root element, not `<testsuites>`.
> Always access via `$junit.testsuite`, never `$junit.testsuites.testsuite`.

```powershell
[xml]$junit = Get-Content "build/<VARIANT>/test/Debug/<COMPONENT>/junit.xml"
$junit.testsuite | Select-Object name, tests, failures, errors, time
```

## Coverage Targets

These are general quality targets. Individual skills or roadmaps may define stricter thresholds.

| Metric | Target | Description |
|--------|--------|-------------|
| Line Coverage | ≥ 80% | Percentage of code lines executed |
| Branch Coverage | ≥ 70% | Percentage of decision branches taken |
| Function Coverage | 100% | All public API functions tested |

## Output Format

Use this format when presenting coverage results in reviews or reports:

```markdown
## Test Coverage Analysis

### Component: <COMPONENT_PATH>
### Variant: <VARIANT>

#### Test Execution
- **Status**: ✅ All tests passed / ❌ Failures detected
- **Test cases**: <N> passed, <N> failed
- **Duration**: ~<N>s

#### Coverage Summary (from coverage.json)
|                   | Exec | Total | Coverage | Target | Status |
|-------------------|------|-------|----------|--------|--------|
| Lines             | <N>  | <N>   | <NN>%    | ≥ 80%  | ✅/❌  |
| Functions         | <N>  | <N>   | <NN>%    | 100%   | ✅/❌  |
| Branches          | <N>  | <N>   | <NN>%    | ≥ 70%  | ✅/❌  |

#### Uncovered Functions
- `<function_name>()` - 0% coverage
```

## Variant to Component Mapping

| Component Type | Variant | Example Target |
|----------------|---------|----------------|
| Core components (`components/spled`, `components/light_controller`) | `Disco` | `components_spled_unittests` |
| Feature components (`components/auto_off`, `components/brightness_controller`) | `Spa` | `components_auto_off_unittests` |

### Listing Available Targets

```powershell
ninja -C build/<VARIANT>/test/Debug -t targets all 2>&1 | Select-String "_unittests"
```

### Listing Available Variants

```powershell
$tasks = Get-Content .vscode/tasks.json | ConvertFrom-Json
$tasks.inputs | Where-Object { $_.id -eq 'variant' } | Select-Object -ExpandProperty options
```
