# MISRA C:2012 Review Checklist

Focused checklist for MISRA C:2012 (with Amendment 2) compliance review.
This checklist covers the most impactful rules for safety-critical embedded C code.

> **Note**: Full MISRA C:2012 has 143 rules. This checklist focuses on rules frequently
> violated and those with highest safety impact. Static analysis tools (Polyspace, QAC)
> should verify the complete rule set.

## Mandatory Rules (Must Follow)

- [ ] **Rule 9.1**: Automatic variables initialized before use
- [ ] **Rule 12.2**: No shift operations exceeding bit width
- [ ] **Rule 13.6**: sizeof() operand has no side effects
- [ ] **Rule 17.3**: Functions declared before use (implicit declaration prohibited)
- [ ] **Rule 17.4**: Functions with no parameters use `void` in parameter list
- [ ] **Rule 17.6**: Array parameters not declared with `static` keyword
- [ ] **Rule 21.13**: ctype.h functions used correctly (signed char issue)
- [ ] **Rule 21.17-21.18**: String handling functions used safely
- [ ] **Rule 22.1**: Memory obtained from allocation freed once only
- [ ] **Rule 22.2**: Block of memory only freed if previously allocated
- [ ] **Rule 22.3**: File handles used after successful open only
- [ ] **Rule 22.4**: No write to read-only file
- [ ] **Rule 22.5-22.6**: FILE pointer not dereferenced or copied

## Required Rules (Safety Critical)

### Type Safety

- [ ] **Rule 10.1**: Operand type appropriate for operation
- [ ] **Rule 10.3**: No narrowing compound assignment (e.g., `u8 += u16`)
- [ ] **Rule 10.4**: Both operands of operator same essential type category
- [ ] **Rule 10.5**: No cast from non-Boolean to Boolean
- [ ] **Rule 10.6**: Composite expression not assigned to wider type
- [ ] **Rule 10.8**: Composite expression not cast to wider type
- [ ] **Rule 11.1**: No conversion between function pointer and other types
- [ ] **Rule 11.2**: No conversion between incomplete pointer types
- [ ] **Rule 11.3**: No cast between pointer and integer types
- [ ] **Rule 11.6**: No cast from `void *` to arithmetic type
- [ ] **Rule 11.8**: No cast removing const/volatile

### Control Flow

- [ ] **Rule 14.1**: No unreachable code
- [ ] **Rule 14.2**: For loop well-formed (single counter, proper increment)
- [ ] **Rule 14.3**: Controlling expressions not invariant
- [ ] **Rule 15.1**: goto not used
- [ ] **Rule 15.2**: goto jumps forward only (if used with deviation)
- [ ] **Rule 15.3**: goto labels in same block or enclosing block
- [ ] **Rule 15.4**: At most one break/goto per iteration statement
- [ ] **Rule 15.5**: Single exit point from function (one return)
- [ ] **Rule 15.6**: Iteration/selection bodies enclosed in braces
- [ ] **Rule 15.7**: All if...else if terminated with else

### Expressions

- [ ] **Rule 12.1**: Precedence of operators made explicit with parentheses
- [ ] **Rule 12.3**: No comma operator
- [ ] **Rule 12.4**: Evaluation of constant expressions same as runtime
- [ ] **Rule 13.1**: No side effects in initializer lists
- [ ] **Rule 13.2**: No dependence on order of evaluation
- [ ] **Rule 13.3**: Full expression has no side effects due to increment/decrement
- [ ] **Rule 13.4**: Assignment not used as sub-expression
- [ ] **Rule 13.5**: Logical AND/OR right operand has no persistent side effects

### Pointers

- [ ] **Rule 18.1**: Pointer arithmetic not applied to non-array pointer
- [ ] **Rule 18.2**: Pointer subtraction only on same array
- [ ] **Rule 18.3**: Relational operators not used on non-array pointers
- [ ] **Rule 18.4**: +/- operators not used with pointers
- [ ] **Rule 18.5**: Declarations not more than 2 levels of pointer indirection
- [ ] **Rule 18.6**: No addresses of automatic objects persist
- [ ] **Rule 18.7**: Flexible array members not used
- [ ] **Rule 18.8**: Variable-length arrays not used

### Memory & Resources

- [ ] **Rule 21.3**: Memory allocation functions (`malloc`, etc.) not used
- [ ] **Rule 22.7-22.10**: Macro handling of errno values correct

## Advisory Rules (Recommended)

- [ ] **Rule 2.7**: No unused parameters (use `(void)param` if intentional)
- [ ] **Rule 4.1**: Octal/hex escape sequences terminated properly
- [ ] **Rule 5.1**: External identifiers distinct within 31 characters
- [ ] **Rule 5.2**: Identifiers in same scope distinct within 31 characters
- [ ] **Rule 8.7**: Functions/objects with internal linkage declared `static`
- [ ] **Rule 8.9**: Objects with block scope declared at block scope
- [ ] **Rule 15.4**: Single entry/exit point per function
- [ ] **Rule 17.1**: stdarg.h features not used
- [ ] **Rule 17.2**: No recursive functions
- [ ] **Rule 20.1**: #include directives preceded only by preprocessor
- [ ] **Rule 20.2**: No ', " or \ in header names
- [ ] **Rule 21.1**: #define/#undef not on reserved identifiers
- [ ] **Rule 21.2**: Reserved identifiers not declared

## Deviation Process

When a rule deviation is necessary:

1. **Document justification** in code comment
2. **Reference deviation** in Polyspace/QAC
3. **Assess risk** and implement mitigations
4. **Obtain approval** per project process

```c
/* MISRA C:2012 Rule 11.3 deviation:
 * Justification: Hardware register access requires cast
 * Risk: Low - register address is hardware-defined constant
 * Mitigation: Verified by integration test
 */
volatile uint32_t *reg = (volatile uint32_t *)0x40000000U;
```
