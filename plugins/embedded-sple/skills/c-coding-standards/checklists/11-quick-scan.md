# 11 — Quick Scan Checklist (BARR‑C:2018)

**Purpose:** A fast, high-signal review pass you can run in minutes to catch the most defect-prone BARR‑C violations before deeper review.
**Use this checklist when:** triaging a PR, doing a first-pass code review, preparing a release candidate, or validating “style + safety basics” on changed files.

> **Scope guidance:** Prefer scanning **only changed files/lines** unless the request explicitly asks for full-repo compliance.

---

## How to use (fast)
1. **Run the “Cheap Automated Checks”** (or eyeball them if tools aren’t available).
2. **Skim for “High-Risk Patterns”** (concurrency, casts, signed/unsigned mixing, missing braces).
3. **Stop early** if you find any **Blockers** and request fixes before continuing.

---

## Severity definitions (quick)
- **Blocker:** Likely bug, undefined behavior, race condition, portability break, or release risk.
- **High:** Easy-to-miss defect vector; should be fixed before merge.
- **Medium:** Readability/maintainability impact; fix if in touched code.
- **Low:** Cosmetic/style; fix opportunistically or via formatter.

---

## A) Cheap Automated Checks (minutes)

### A1 — Tabs and line endings (Blocker)
- [ ] **No tabs** (ASCII `0x09`) anywhere in `.c/.h`
  *Why:* tabs break alignment across tools and reviews.
- [ ] Files end with a **final newline** and include **end-of-file marker** comment.
  *Why:* avoids toolchain and diff edge cases.

### A2 — Line width (Medium → High)
- [ ] Lines are **≤ 80 chars** (wrap long conditions and calls).
  *Why:* improves review/diff readability.

### A3 — Forbidden / discouraged tokens (High)
- [ ] No `auto`, `register`.
- [ ] No `short`, `long`.
- [ ] No `#include "something.c"`.

### A4 — Suspicious conditionals (High)
- [ ] No assignments in `if` / `else if` tests.
  *Heuristic:* look for `if (` lines containing `=` not part of `==`.

---

## B) Control Flow Must-Haves (high defect leverage)

### B1 — Braces always (Blocker)
- [ ] Every `if/else/switch/while/do/for` body uses braces — even single statements and empty bodies.
  *Fix:* add braces and, for empty bodies, add a comment explaining intent.

### B2 — Parentheses clarity (High)
- [ ] Complex expressions don’t rely on precedence “remembering.”
- [ ] `&&` and `||` operands are parenthesized unless a single identifier/constant.
  *Fix:* add parentheses or split into named booleans.

### B3 — `if/else if` completeness (High)
- [ ] Any `if` chain with `else if` ends with a final `else`.
  *Fix:* add `else` and handle unexpected states with WARNING/NOTE as needed.

### B4 — `switch` completeness (High)
- [ ] Every `switch` has a `default` case.
- [ ] Any intentional fall-through is clearly commented.
- [ ] `break` placement makes missing breaks visually obvious.

---

## C) Data Types & Portability (common hidden bugs)

### C1 — Fixed-width integer usage (High)
- [ ] If width matters, uses `int8_t/uint8_t/...` etc.
- [ ] `char` used only for strings; raw bytes use `uint8_t`.

### C2 — Signed/unsigned mixing (Blocker → High)
- [ ] No signed + unsigned mixing in expressions/comparisons.
- [ ] Unsigned decimal constants use `u` suffix when appropriate.
  *Fix:* normalize to one type (`int32_t`/`uint32_t`) and cast once with rationale if required.

### C3 — Bitwise operations safety (High)
- [ ] Bitwise ops (`& | ^ ~ << >>`) are not applied to signed types.
  *Fix:* convert to unsigned type before bitwise operations.

### C4 — Cast discipline (High)
- [ ] Every cast has a comment describing range safety and assumptions.
  *Fix:* replace with helper conversion or add bounded checks + cast comment.

### C5 — Floating point (High when present)
- [ ] No float equality/inequality tests.
- [ ] Single-precision constants include `f`.
- [ ] `isfinite()` used where NaN/Inf can appear (project policy).

---

## D) Concurrency & Hardware Interaction (highest risk in embedded)

### D1 — `volatile` correctness (Blocker)
- [ ] Variables shared with ISRs/threads are `volatile` (or explicitly protected).
- [ ] MMIO register pointers are `volatile * const` and correctly typed.

### D2 — Atomicity / critical sections (Blocker)
- [ ] Multi-byte shared data reads/writes are protected when the target may not access atomically.
  *Fix:* use critical section around access or use safe atomic primitives per platform.

### D3 — ISR hygiene (High → Blocker)
- [ ] ISR is marked with the required compiler ISR attribute/pragma.
- [ ] ISR name ends with `_isr`.
- [ ] ISR does minimal work: capture/clear/notify; heavy work deferred.
- [ ] Stub/default handlers exist for unexpected interrupts (project policy).

---

## E) Naming & Initialization (maintenance defect prevention)

### E1 — Variable naming (Medium → High)
- [ ] Globals start with `g_`, pointers `p_`, pointer-to-pointer `pp_`.
- [ ] Boolean-in-integer values start with `b_` and read like a question.
- [ ] No leading underscores; no uppercase in variable/function names.

### E2 — Initialization (Blocker)
- [ ] All variables initialized before use.
- [ ] Pointers default to `NULL` if not immediately assigned.
- [ ] File-scope globals grouped at top of `.c`.

---

## F) Header/Module sanity (coupling and compile-time checks)

### F1 — Header guards and pairing (High)
- [ ] Exactly one `.h` per `.c` with same root name.
- [ ] Header has an include guard (`#ifndef/#define/#endif`).
- [ ] `.c` includes its own header (preferably first) so prototypes are checked.

### F2 — Header contents (High)
- [ ] No variable storage allocated in headers.
- [ ] Public headers do not include private headers.
- [ ] Avoid `extern` globals; prefer accessors.

---

## G) Deviation hygiene (only if needed)

### G1 — Deviations are explicit and complete (High)
- [ ] Any deviation includes:
  - BARR‑C rule reference
  - reason, risk, mitigation
  - Approved-by, Date (or placeholders per policy)
- [ ] Deviation is **narrow** (line/function preferred over module).

---

## Quick “Stop the line” Blockers (if any of these occur, pause review)
- [ ] Missing braces on any control structure
- [ ] Signed/unsigned mixing with non-trivial expressions
- [ ] ISR/thread-shared data without `volatile` or protection
- [ ] Use-before-init or null dereference risk
- [ ] Missing `default` in `switch` for enums/state machines
- [ ] Assignment inside conditional tests (`if (x = y)`)

---

## Optional: Micro-output template (for PR comments)
Use this structure for fast PR feedback:

- **Blockers:** (list)
- **High:** (list)
- **Medium/Low:** (list)
- **Suggested patch:** (diff or bullet steps)
- **Automation suggestion:** (which check would prevent this next time)
