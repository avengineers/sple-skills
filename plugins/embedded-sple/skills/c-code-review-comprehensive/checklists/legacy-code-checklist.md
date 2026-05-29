# Legacy Code Review Checklist

Based on "Working Effectively with Legacy Code" by Michael Feathers.
Focus on testability, refactoring safety, and managing technical debt.

## Definition

**Legacy Code** = Code without tests (Feathers' definition).
This checklist helps assess how testable code is and identifies barriers to safe refactoring.

## Testability Assessment

### Seam Identification

- [ ] **Object seams exist**: Can substitute dependencies
  - In C: Function pointers, weak symbols, hammocking
- [ ] **Preprocessor seams usable**: Can conditionally compile test code
  - `#ifdef TEST` blocks
- [ ] **Link seams available**: Can link against test doubles
  - Hammocking pattern works

### Dependency Analysis

- [ ] **Dependencies identifiable**: Clear what module depends on
  - Header includes show dependencies
  - Function calls to external modules documented

- [ ] **Dependencies mockable**: Can replace with test doubles
  - No direct hardware access in business logic
  - I/O separated from computation

- [ ] **Global state minimized**: Few global variables
  - Globals make testing difficult
  - If globals needed, can reset for each test

- [ ] **Singletons avoided**: No hidden global state
  - Or singletons have test reset mechanism

### Test Harness Compatibility

- [ ] **Functions callable from test**: Can invoke functions
  - Not buried in infinite loops
  - Reasonable execution time

- [ ] **Outputs observable**: Can verify results
  - Functions return values or have output parameters
  - State changes verifiable

- [ ] **Preconditions settable**: Can establish test conditions
  - State machine can be set to any state for testing
  - Input data can be constructed

## Refactoring Safety

### Change Risk Assessment

- [ ] **Change points identified**: Know where changes needed
  - Requirements traced to code
  - Impact of changes understood

- [ ] **Test coverage exists**: Tests protect against regressions
  - Unit tests for functions being modified
  - Integration tests for affected flows

- [ ] **Characterization tests possible**: Can capture current behavior
  - If no tests, can add tests documenting current behavior
  - Even if behavior is buggy, tests detect changes

### Coupling Analysis

- [ ] **Low coupling**: Changes don't cascade
  - Function changes don't require changes elsewhere
  - Module interfaces stable

- [ ] **High cohesion**: Related code together
  - Functions in same module serve same purpose
  - State and behavior co-located

- [ ] **No hidden dependencies**: All dependencies explicit
  - No reliance on call order
  - No temporal coupling

## Code Smells (Refactoring Candidates)

### Structural Smells

- [ ] **No God Class/Module**: No single file doing everything
  - Files < 1000 lines generally
  - Clear single responsibility

- [ ] **No Long Methods**: Functions manageable size
  - Functions < 50 lines
  - Can understand without scrolling

- [ ] **No Long Parameter Lists**: Reasonable parameter count
  - Max 5 parameters
  - Consider struct if more needed

- [ ] **No Duplicated Code**: DRY principle
  - Similar logic not copy-pasted
  - Common patterns extracted

### Complexity Smells

- [ ] **No Deep Nesting**: Control flow shallow
  - Max 4 levels of nesting
  - Guard clauses to reduce nesting

- [ ] **No Complex Conditionals**: Conditions understandable
  - Boolean expressions simple
  - Complex conditions extracted to named functions

- [ ] **No Feature Envy**: Functions use own module's data
  - Functions don't reach into other modules excessively

### Naming Smells

- [ ] **No Mysterious Names**: All names meaningful
  - No single-letter variables (except loop indices)
  - No abbreviations without definition

- [ ] **No Misleading Names**: Names match behavior
  - Function names describe what function does
  - Variable names describe content

## Refactoring Techniques Applicable

### Safe Refactorings (when tests exist)

- [ ] **Extract Function**: Can break up large functions
  - Identify cohesive blocks
  - Extract with clear interface

- [ ] **Extract Variable**: Can name complex expressions
  - Replace magic numbers with constants
  - Name intermediate calculations

- [ ] **Rename**: Can improve names
  - Tools support rename across codebase
  - Or can search-and-replace safely

### Adding Tests First

- [ ] **Sprout Method**: Add new code in tested function
  - New functionality in new function
  - New function fully tested
  - Old function calls new function

- [ ] **Wrap Method**: Add behavior around existing
  - Create wrapper function
  - Wrapper is tested
  - Original behavior preserved

- [ ] **Characterization Test**: Capture current behavior
  - Write test that passes with current behavior
  - Even if behavior seems wrong
  - Test detects any change

## Technical Debt Indicators

| Indicator                    | Status | Impact                  |
|------------------------------|--------|-------------------------|
| No unit tests                | ⬜     | Cannot refactor safely  |
| High complexity (CYCLO > 15) | ⬜     | Hard to understand/test |
| Deep dependencies            | ⬜     | Changes cascade         |
| Global state                 | ⬜     | Tests not isolated      |
| Mixed abstraction levels     | ⬜     | Hard to understand      |
| Duplicated code              | ⬜     | Inconsistent fixes      |
| Poor naming                  | ⬜     | Misunderstandings       |

## Recommendations Template

### For Untestable Code

```markdown
**Problem**: Function `calculate_output()` cannot be unit tested
**Reason**: Direct hardware register access in business logic
**Recommendation**: Extract hardware access to separate function, inject via function pointer
**Effort**: Medium (2-4 hours)
**Risk if not addressed**: Cannot safely modify calculation logic
```

### For High-Risk Changes

```markdown
**Problem**: Changing `state_machine()` affects 12 other modules
**Reason**: High afferent coupling, central state accessed globally
**Recommendation**: Add characterization tests before any changes
**Effort**: High (1-2 days for test coverage)
**Risk if not addressed**: Regression bugs in dependent modules
```

## Overall Assessment

| Category           | Status | Notes |
|--------------------|--------|-------|
| Testability        | ⬜     |       |
| Refactoring Safety | ⬜     |       |
| Code Smells        | ⬜     |       |
| Technical Debt     | ⬜     |       |
