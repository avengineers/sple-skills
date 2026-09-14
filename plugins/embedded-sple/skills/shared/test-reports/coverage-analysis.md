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

## Per File and Per Function

The totals above answer "where does the component stand". A roadmap step needs the next question
answered too — *which* file and *which* function is uncovered. Both are in the same file:

- **Per file** — each entry of `files` carries its own `lines`.
- **Per function** — every entry of `lines` carries `function_name`. Group by it.

> The `functions` array is **not** the place to look. Its entries give `execution_count` (was the
> function entered at all) and `blocks_percent`, never the line coverage of the body. Reading only
> that array is what makes per-function coverage look unavailable.

```powershell
$cov = Get-Content "build/<VARIANT>/test/Debug/<COMPONENT>/coverage.json" -Raw | ConvertFrom-Json

function Get-LineStats($lines) {
    $total    = @($lines).Count
    $covered  = @($lines | Where-Object { $_.count -gt 0 }).Count
    $branches = @($lines | ForEach-Object { $_.branches } | Where-Object { $_ })
    [PSCustomObject]@{
        Lines         = $total
        LinesCovered  = $covered
        LinePercent   = if ($total) { [math]::Round($covered / $total * 100, 1) } else { 0 }
        Branches      = @($branches).Count
        BranchCovered = @($branches | Where-Object { $_.count -gt 0 }).Count
    }
}

"Per file"
foreach ($f in $cov.files) {
    $s = Get-LineStats $f.lines
    "  {0,-40} {1,4}/{2,-4} {3,5}%" -f $f.file, $s.LinesCovered, $s.Lines, $s.LinePercent
}

"`nPer function"
foreach ($f in $cov.files) {
    $f.lines |
        Group-Object { if ($_.function_name) { $_.function_name } else { "(file scope)" } } |
        Sort-Object Name |
        ForEach-Object {
            $s = Get-LineStats $_.Group
            "  {0,-30} lines {1,3}/{2,-3} {3,5}%   branches {4,2}/{5,-2}" -f `
                $_.Name, $s.LinesCovered, $s.Lines, $s.LinePercent, $s.BranchCovered, $s.Branches
        }
}
```

Example output:

```text
Per file
  src/component/src/component.c               5/8     62.5%

Per function
  (file scope)                   lines   2/3    66.7%   branches  0/0
  partiallyTested                lines   2/4      50%   branches  1/2
  someInterfaceOfComponent       lines   1/1     100%   branches  0/0
```

**`(file scope)` is not a defect.** gcovr omits `function_name` for lines that belong to no
function — an initialiser at file scope, for instance. The grouping expression above folds a
missing, null or empty name into that one bucket; grouping on the raw field splits them and reports
the same bucket twice.

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
