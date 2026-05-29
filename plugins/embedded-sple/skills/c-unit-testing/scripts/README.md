# GTest Unit Testing Scripts

Helper scripts for analyzing and testing embedded C components.

> **Building and running tests**: Use the `build-execution` skill instead of manual scripts.
> Provide: `buildKit=test, buildType=Debug, variants=<Variant>, target=components_<name>_unittests`

## Available Scripts

### [analyze_dependencies.py](analyze_dependencies.py)

Heuristic analyzer for C source files. Identifies external dependencies, global variables, static functions, and memory-mapped I/O — useful for planning which mocks and test strategies a component needs.

```powershell
python plugins/embedded-sple/skills/c-unit-testing/scripts/analyze_dependencies.py components/examples/adc/src/adc.c
```

The output includes:
- External function calls (candidates for hammocking)
- Global variable access (potential side effects)
- Static functions (internal logic, not directly testable)
- MMIO register access (needs `SPLE_UNIT_TESTING` guard pattern)
