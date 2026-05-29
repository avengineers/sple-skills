# 12 — PR Review Checklist (BARR‑C:2018)

**Purpose:** A structured, repeatable PR review checklist that applies BARR‑C:2018 rules with severity gating, minimal-diff expectations, and clear reviewer outcomes.
**Use this document when:** reviewing a pull request, preparing for release, or coaching contributors on “what good looks like” for Embedded C submissions.

---

## 0) Review Setup (30–60 seconds)

### Confirm scope

- [ ] Review scope is **changed lines/files** unless the PR explicitly includes “formatting sweep” or “full module compliance”.
- [ ] If the PR includes formatting changes, they are isolated in a **whitespace-only commit** (no logic changes mixed in).

### Identify context

- [ ] Target platform is known (MCU family, compiler, optimization level).
- [ ] Concurrency model is known (bare metal / RTOS / ISR nesting rules).
- [ ] Safety/security criticality known (do we need MISRA/CERT overlays?).

> If any of these are unknown and the PR touches interrupts/concurrency or data layout, request the missing context before approving.

---

## 1) Merge Gate Criteria (Stop-the-line rules)

Mark the PR **“Changes requested”** if any of the following occur:

### Blockers (must fix before merge)

- [ ] Missing braces on any `if/else/switch/while/do/for`.
- [ ] Assignment occurs inside `if` / `else if` test.
- [ ] ISR/thread-shared state is accessed without correct `volatile` and/or protection (atomicity/critical section).
- [ ] Signed/unsigned mixing in expressions/comparisons without explicit normalization.
- [ ] Potential use-before-init, null dereference, buffer overrun, or obvious undefined behavior.
- [ ] `switch` over state/enum without a `default`.
- [ ] `.c` file includes another `.c` file.
- [ ] Storage allocated in a header file.

### High severity (fix before merge unless explicitly deferred)

- [ ] Casts without range/assumption comment.
- [ ] Bitwise operations performed on signed data.
- [ ] Loop bounds contain magic numbers that are not tied to named constants / structure sizes.
- [ ] Intentional `switch` fall-through without an explanatory comment.
- [ ] Function-like macros used when a function/`inline` would work.

---

## 2) PR Review Flow (Recommended order)

### Step A — Build & scan hygiene

- [ ] Build passes with warnings treated as errors (if project policy).
- [ ] Cheap scan passes (tabs, long lines, forbidden tokens, `.c` includes).
- [ ] Static analysis results reviewed (if available) for new warnings only.

### Step B — API and module boundary sanity

- [ ] Public APIs are declared in the module header; private helpers are `static`.
- [ ] The `.c` includes its own header so prototype mismatches are caught.
- [ ] Headers expose only what is necessary; no internal-only macros/types leaked.

### Step C — Correctness and defect traps

- [ ] Control flow is explicit and brace-wrapped.
- [ ] Expression precedence is clarified with parentheses or extracted predicates.
- [ ] Error paths are deterministic and resource cleanup is correct.
- [ ] Concurrency and ISR patterns are safe and documented.

### Step D — Readability and maintainability

- [ ] Functions are reasonably sized (≈ one page / ≤100 lines preferred).
- [ ] Naming follows conventions and intent is obvious.
- [ ] Comments document *why*, assumptions, and hazards; Doxygen blocks exist where appropriate.
- [ ] No needless churn: changes are minimal and reviewable.

---

## 3) Detailed Checklist by Topic (BARR‑C-aligned)

### 3.1 General rules (C99 baseline, braces, parentheses, keywords)

- [ ] Code remains C99 compatible; extensions are localized and documented.
- [ ] Braces always used; brace placement consistent.
- [ ] `&&` / `||` operands parenthesized unless a single identifier/constant.
- [ ] No reliance on unclear precedence in non-trivial expressions.
- [ ] No `auto` or `register`. `goto/continue` avoided (or justified).

**Reviewer note:** If you see `goto`, ensure it’s forward-only and used strictly for cleanup clarity.

---

### 3.2 Comments (quality, no commented-out code, markers)

- [ ] No commented-out code (use `#if 0` or remove).
- [ ] Comments are complete sentences and don’t explain obvious syntax.
- [ ] Block comments precede logical steps; a blank line follows blocks.
- [ ] Assumptions are explicit (timing, atomicity, register semantics, layout).
- [ ] Uses `WARNING:`, `NOTE:`, `TODO:` appropriately.
- [ ] Public APIs and modules have Doxygen-ready comments where needed.

---

### 3.3 White space (spacing, alignment, tabs, file ending)

- [ ] No tabs anywhere.
- [ ] One statement per line; blank lines around natural blocks.
- [ ] Operators/commas/semicolons spaced consistently.
- [ ] Indentation is consistent (4-space multiples); `switch/case` formatted consistently.
- [ ] File ends with end-of-file marker and a trailing blank line.
- [ ] Lines ≤ 80 chars or wrapped cleanly.

---

### 3.4 Modules (headers, includes, coupling)

- [ ] `.c/.h` file pair exists with matching root name.
- [ ] Header guard present and correct.
- [ ] `.c` includes its own header (preferably first).
- [ ] No absolute include paths; no unused includes.
- [ ] No storage allocated in header; avoid `extern` in headers (prefer accessors).
- [ ] Public headers do not include private headers.

---

### 3.5 Data types (width, signedness, floats, struct layout, bool)

- [ ] Fixed-width integer types used when width matters; no `short`/`long`.
- [ ] `char` used only for strings; raw bytes use `uint8_t`.
- [ ] No mixing signed and unsigned in expressions/comparisons.
- [ ] No bitwise ops on signed data; no signed bitfields.
- [ ] Casts documented with range/assumptions.
- [ ] Floating point (if present): no equality tests; `f` suffix for float constants; finite checks if required.
- [ ] Structs/unions used for MMIO/bus/network have layout protections and size checks.
- [ ] Boolean variables use `bool`; non-boolean → bool via relational operator.

---

### 3.6 Procedures (function size, prototypes, macros, tasks, ISRs)

- [ ] Functions are reasonably small and cohesive; refactor if too long/complex.
- [ ] Public functions declared in header; private helpers are `static`.
- [ ] Parameter names are meaningful.
- [ ] Function-like macros avoided; prefer `static inline`.
- [ ] Task entry points named `_thread/_task/_process` and use `for (;;)` for infinite loops.
- [ ] ISRs:
  - marked with toolchain attribute/pragma/keyword
  - named `_isr`
  - minimal work, deterministic
  - clear/acknowledge interrupt source
  - safe default ISR exists (policy dependent)

---

### 3.7 Variables (naming, init, globals/pointers/boolean ints)

- [ ] Naming:
  - globals `g_`
  - pointers `p_`, pointer-to-pointer `pp_`
  - boolean-in-integer `b_` phrased as a question
  - handles `h_`
- [ ] Variables initialized before use; pointers `NULL` if unassigned.
- [ ] Locals declared near first use; file-scope globals grouped at top of `.c`.
- [ ] No variable names collide with keywords/stdlib; no leading underscore; no uppercase.

---

### 3.8 Statements (conditionals, switch, loops, jumps, comparisons)

- [ ] No comma operator in declarations.
- [ ] `if/else if` ends with `else`; nesting ≤ 2 levels (refactor otherwise).
- [ ] `switch` has `default`; fall-through is commented; `break` is obvious.
- [ ] Loops:
  - no magic bounds
  - no assignments in controlling expressions (except `for` init/increment)
  - `for (;;)` for infinite loops
  - empty loops have braces + explanatory comment
- [ ] No `abort/exit/setjmp/longjmp`.
- [ ] Constant on the left for comparisons to constants: `NULL == p`, `0u == x`.

---

## 4) Minimal “Reviewer Output” Template (for PR comments)

Copy/paste this structure into PR reviews:

- **Summary:** ✅ / ⚠️ / ❌ (one sentence)
- **Blockers:**
  - `file.c:line` — description — suggested fix
- **High:**
  - …
- **Medium/Low:**
  - …
- **Suggested patch:** (small diff or bullet steps)
- **Automation suggestion:** (which check would prevent this next time)

---

## 5) Minimal Diff Expectations (Reduce Review Noise)

- [ ] No large reformatting mixed with functional changes.
- [ ] If formatting changes are required:
  - do them first as a whitespace-only commit
  - then apply logic changes

---

## 6) Deviation Handling (Only if needed)

If a rule must be violated:

- [ ] Deviation comment present near the code, includes:
  - BARR‑C rule reference
  - reason, risk, mitigation
  - Approved-by, Date (or policy placeholders)
- [ ] Scope is minimal (line/function preferred over module).

**Deviation token recommendation:**

```c
/* DEVIATION (BARR-C X.Y):
 * Reason:
 * Risk:
 * Mitigation:
 * Approved-by:
 * Date:
 */
```

---

## Final decision checklist (Reviewer conclusion)

Approve **only if**:

- [ ] No Blockers remain.
- [ ] High severity items are fixed or explicitly tracked with a justified plan.
- [ ] PR is reviewable (minimal diffs, clear intent, adequate comments).
- [ ] Concurrency/layout changes are safe and documented.
