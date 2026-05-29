# CHK_Code Review Checklist

Complete 42-item code review checklist for C source files.

## Git/Version Control

- [ ] **#1** Pull request has minimum approvals (at least 1 senior engineer)
- [ ] **#2** All Pull Requests documented with IDs

## Formal Check

- [ ] **#3** Project-specific templates used (.c and .h file templates as defined by the project)
- [ ] **#4** No `<ToDo>` entries present (search for TODO keywords)
- [ ] **#5** No unnecessary commented code present
- [ ] **#6** Symbolic constants used instead of magic numbers
- [ ] **#7** No hard-coded text/strings used
- [ ] **#8** Function naming conventions correct (e.g., `var_c` for byte)
- [ ] **#9** Variable naming conventions correct

## Interfaces

- [ ] **#10** Received data checked for validity (ASSERT used for development)
- [ ] **#11** Inconsistent/invalid data identified and processed correctly (ASSERT used)

## Data and Variables

- [ ] **#12** Secondary/auxiliary usage of variables specified if used multiple times
- [ ] **#13** All variables initialized in start functions (→ `static-code-analysis` skill: NIV finding)
- [ ] **#14** Global variables with interrupt access specially marked (multitasking analysis)

## Calculations

- [ ] **#15** No divisions by zero (→ `static-code-analysis` skill: DIV finding)

## Other Points

- [ ] **#16** All static analysis findings documented and justified (→ `static-code-analysis` skill)
- [ ] **#17** High cyclomatic complexity addressed with re-design references
- [ ] **#18** Pointers checked for validity (!=NULL) before access
- [ ] **#19** Write memory access doesn't violate unallocated areas (array bounds checking)
- [ ] **#20** Data used multiple times defined as constant
- [ ] **#21** Dynamic interface validation (Div by Zero, bounds checking, arithmetic checks)

## Cybersecurity

- [ ] **#22** Static code analysis rules for cybersecurity active and run (→ `static-code-analysis` skill: no open security warnings)

## Functional Safety - Code Structure

- [ ] **#23** Code completely and correctly implements and traces to low-level design
- [ ] **#24** Data consistent with design and within specified range (data coupling)
- [ ] **#25** Operations invoked as defined in design (control coupling)
- [ ] **#26** No uncalled/unneeded operations or unreachable code (→ `static-code-analysis` skill: UNR finding)
- [ ] **#27** Reusable components/library functions used where possible
- [ ] **#28** Repeated code condensed into single procedures
- [ ] **#29** Complex modules restructured/split appropriately (code metrics review)
- [ ] **#30** All statements and structures verifiable without modification
- [ ] **#31** Keywords `static`, `volatile`, and `const` used appropriately

## Documentation

- [ ] **#32** All comments consistent with code

## Arithmetic Operations

- [ ] **#33** No floating-point equality comparisons

## Loops and Branches

- [ ] **#34** Loop-invariant statements moved outside loops where possible

## Defensive Programming

- [ ] **#35** Error handling included (e.g., file open checks)
- [ ] **#36** No overloading in numeric and pointer types (→ `static-code-analysis` skill)

## MISRA Compliance

- [ ] **#37** Remaining MISRA rules verified (→ `static-code-analysis` skill)

## Polyspace Integration

- [ ] **#38** All `#ifdef POLYSPACE` constructs used correctly for code modifications
- [ ] **#39** Measures/justifications added for all findings (→ `static-code-analysis` skill: Severity and Status set)
- [ ] **#40** Justification texts are technically substantive — no hollow phrases ("I know what I do", "justified", "not relevant", "legacy code", etc.). Each justification must explain *why the code is safe* despite the violation, not merely assert that it is.

## Consistency Checks

- [ ] **#41** Consistency between software requirements and software units (completeness and correctness)
- [ ] **#42** Consistency between architectural design, detailed design, and software units
