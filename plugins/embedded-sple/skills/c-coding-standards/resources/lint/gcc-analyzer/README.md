# GCC Analyzer Bundle (-fanalyzer)

This bundle installs into a project as:

- `tools/gcc-analyzer.flags`
- `tools/run-gcc-analyzer.sh`
- `tools/run-gcc-analyzer.ps1`

## What it does

Runs GCC’s integrated static analyzer by compiling each `.c` file with `-fanalyzer`.

## Requirements

- GCC with analyzer support (GCC 10+ typically, if built with analyzer enabled).

## Run (Bash)

```bash
tools/run-gcc-analyzer.sh .
# customize:
tools/run-gcc-analyzer.sh . --roots "src drivers" --out-dir build/gcc-analyzer
```

## Run (PowerShell)

```powershell
.\tools\run-gcc-analyzer.ps1 -SrcRoot . -Roots @("src","drivers") -OutDir build/gcc-analyzer
```

## Important: project include paths/defines

This bundle compiles each `.c` file individually. Most real projects need include paths and defines.
Add them by editing `tools/gcc-analyzer.flags`, e.g.:

- `-Iinclude`
- `-Idrivers/include`
- `-DMY_FEATURE=1`

## When to run

`-fanalyzer` is more expensive than normal warnings, so it’s often run in CI/nightly rather than every local build.
``
