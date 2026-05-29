# 10 — Automation & Enforcement Hooks (BARR‑C:2018 Enforcement Guidance)

**Purpose:** Turn BARR‑C rules into repeatable, low‑friction checks that catch defects early (preferably at build/CI time) and keep reviews focused on logic rather than style policing.
**Use this document when:** setting up CI gates, pre‑commit hooks, static analysis, formatting tools, or when you want a practical “enforcement plan” for BARR‑C compliance.

---

## Guiding Principles (How to Automate BARR‑C Effectively)

1. **Automate what you can; review what you must**
   - Prefer checks that run every build/CI.
   - Reserve human review for intent/architecture/algorithm correctness.

2. **Keep enforcement cheap and fast**
   - Use “fast scans” (grep + lightweight scripts) for obvious violations.
   - Use static analysis for semantic hazards (signed/unsigned mixing, use-before-init).

3. **Avoid noisy churn**
   - Separate **whitespace-only** commits from functional changes to preserve clean diffs.

4. **Make exceptions explicit**
   - Standardize deviation markers and enforce their metadata (Approved-by/Date).

---

## Recommended Enforcement Layers

### Layer 1 — Editor Configuration (Prevent issues at source)
**Goal:** prevent violations before they exist.

**Recommended settings**
- Insert spaces when pressing TAB (tabs forbidden).
- Configure line endings (prefer LF).
- Display a visible 80-column guideline.
- Enable “trim trailing whitespace on save”.

**Optional: shared repo config**
- `.editorconfig` can enforce indent style, end-of-line, charset, and trimming.
- `.gitattributes` can normalize line endings and prevent CRLF drift.

---

### Layer 2 — Pre-Commit Hooks (Reject obvious violations)
**Goal:** stop simple violations at commit time.

**What to block in pre-commit**
- tabs in source files
- trailing whitespace
- missing final newline
- lines > 80 chars (policy-dependent)
- forbidden keywords (`auto`, `register`; and optionally `short`, `long`)
- accidental `.c` file includes
- commented-out code (heuristic, review may still be needed)

#### Example: minimal git pre-commit hook (bash)
Save as `.git/hooks/pre-commit` (or managed via a hooks framework):

```bash
#!/usr/bin/env bash
set -euo pipefail

# Only scan staged C/C header files.
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(c|h)$' || true)
[ -z "${FILES}" ] && exit 0

fail() { echo "ERROR: $*" >&2; exit 1; }

# 1) Tabs forbidden
if git diff --cached -U0 -- ${FILES} | grep -n $'\t' >/dev/null; then
  fail "Tab character found in staged diff (tabs are forbidden)."
fi

# 2) Trailing whitespace
if git diff --cached -U0 -- ${FILES} | grep -nE '^[+].*[[:blank:]]+$' >/dev/null; then
  fail "Trailing whitespace found in staged diff."
fi

# 3) Forbidden keywords (project policy can expand this list)
if git diff --cached -U0 -- ${FILES} | grep -nE '^[+].*\b(auto|register)\b' >/dev/null; then
  fail "Forbidden keyword found in staged diff (auto/register)."
fi

# 4) short/long forbidden (BARR‑C)
if git diff --cached -U0 -- ${FILES} | grep -nE '^[+].*\b(short|long)\b' >/dev/null; then
  fail "Forbidden type keyword found in staged diff (short/long)."
fi

# 5) Line width check (80 columns) — check added lines only
if git diff --cached -U0 -- ${FILES} | grep -nE '^\+.{81,}$' >/dev/null; then
  fail "Line longer than 80 columns found in staged diff."
fi

# 6) Including .c files is forbidden
if git diff --cached -U0 -- ${FILES} | grep -nE '^\+.*#\s*include\s+".*\.c"' >/dev/null; then
  fail "Including a .c file is forbidden."
fi

echo "Pre-commit checks passed."
exit 0
```

**Notes**
- This scans *only staged changes* to minimize noise.
- Expand/relax checks based on your project’s reality and migration plan.

---

### Layer 3 — Build-Time “Fast Scan” (Cheap CI gate)
**Goal:** always-on checks in CI, similar to pre-commit, but authoritative.

**Recommended CI steps**
- Run the same grep/script checks across the full repository (or changed files).
- Enforce consistent LF endings if toolchain permits.
- Fail builds on newly introduced violations.

#### Example: fast scan script (bash)
```bash
#!/usr/bin/env bash
set -euo pipefail

SRC_FILES=$(git ls-files | grep -E '\.(c|h)$' || true)
[ -z "${SRC_FILES}" ] && exit 0

echo "[scan] Checking for tabs..."
grep -n $'\t' ${SRC_FILES} && { echo "Tabs found"; exit 1; } || true

echo "[scan] Checking for forbidden keywords (auto/register)..."
grep -nE '\b(auto|register)\b' ${SRC_FILES} && { echo "Forbidden keywords found"; exit 1; } || true

echo "[scan] Checking for forbidden type keywords (short/long)..."
grep -nE '\b(short|long)\b' ${SRC_FILES} && { echo "Forbidden type keywords found"; exit 1; } || true

echo "[scan] Checking for include of .c files..."
grep -nE '#\s*include\s+".*\.c"' ${SRC_FILES} && { echo "Found .c include"; exit 1; } || true

echo "[scan] Checking for long lines (>80)..."
# ignore lines that are expected to be long (optional), e.g., URLs, generated code markers
grep -nE '^.{81,}$' ${SRC_FILES} && { echo "Long lines found"; exit 1; } || true

echo "[scan] OK"
```

---

## Static Analysis (Semantic Defects You Can’t Grep Reliably)

**Goal:** catch defects that require parsing/flow analysis.

### High-value checks aligned to BARR‑C intent
- **Use-before-initialization** (7.2)
- **Signed/unsigned mixing** and suspicious promotions (5.3)
- **Bitwise ops on signed types** (5.3)
- **Suspicious assignments in conditionals** (8.2)
- **Unreachable code** / missing returns (6.2)
- **Missing switch default** and incomplete enum handling (8.3)
- **Potential null dereference paths** (7.2)
- **Volatile misuse** (missing volatile on ISR/shared state; read-modify-write hazards)

### Tool strategy (tool-agnostic)
- Enable maximum compiler warnings in CI and treat as errors where feasible.
- Add a dedicated static analysis job (often slower than build).

**Compiler warnings to consider enabling**
- Warnings for suspicious assignments in conditionals (where supported)
- Conversion and sign-compare warnings
- Unused parameters/variables warnings (policy dependent)
- Missing prototypes, missing declarations, inconsistent prototypes

> **Policy note:** When turning on new warnings in a legacy codebase, consider:
> 1) enabling warnings but not failing builds initially (“report-only” phase)
> 2) then failing builds on *new* warnings only
> 3) then incrementally cleaning the backlog module-by-module

---

## Formatting Automation (Whitespace and Style Without Manual Policing)

**Goal:** keep formatting consistent while minimizing review noise.

### Recommended approach
1. **Pick one formatter** for indentation/spacing/braces (or a limited set).
2. Run formatter:
   - on save in editor (optional)
   - as a CI check (diff must be clean)
3. If you reformat legacy code:
   - do it in a **whitespace-only commit** (no logic changes).

### Formatter mode suggestions
- **Check mode:** CI verifies formatting is already correct (fails if changes would occur).
- **Fix mode:** local developer command re-writes files and then the changes are committed.

**Example: “format-check” workflow**
- `format` (local) updates files
- `format-check` (CI) verifies no changes would be made

---

## Rule-to-Check Mapping (Practical Targets)

### Common “easy wins” to automate
- **Tabs forbidden** (3.5): grep
- **Line width ≤ 80** (1.2): grep/script
- **Forbidden keywords** `auto/register` (1.7): grep
- **Forbidden `short/long`** (5.2): grep
- **No `.c` includes** (4.3): grep
- **No assignments inside `if` tests** (8.2): heuristic grep + static analysis
- **No commented-out code** (2.1): heuristic grep + review rule
- **End-of-file comment + trailing newline** (3.3): script/linter

---

## Recommended Grep Patterns (Heuristics + Caveats)

> Grep patterns are **heuristics**; use them to flag candidates for review, not as perfect parsers.

### Suspicious assignment in conditional (heuristic)
```text
if\s*\(.*=[^=]
```

### Commented-out code smell (heuristic)
Flags lines that look like code after `//`:
```text
^\s*//\s*([A-Za-z_]\w*\s*\(|[A-Za-z_]\w*\s*=|return\s+)
```

### Missing `default:` in switch (not reliable by grep)
- Prefer a parser/static analysis.
- Grep can only give a rough list of switches for review:
```text
^\s*switch\s*\(
```

### Find tabs
- literal tab character (`\t`) — use grep with actual tab insertion or tooling support.

---

## Deviation Enforcement (Make Exceptions Auditable)

### Required policy
- Any occurrence of `DEVIATION (BARR-C` must include:
  - `Approved-by:`
  - `Date:`

### CI check idea
- Fail if a deviation block is missing required metadata.

**Example grep checks**
```bash
# list deviations
grep -RIn 'DEVIATION \(BARR-C' .

# fail if missing Approved-by within next N lines (simple heuristic)
grep -RIn 'DEVIATION \(BARR-C' -n . | while read -r line; do
  file=$(echo "$line" | cut -d: -f1)
  lno=$(echo "$line" | cut -d: -f2)
  tail -n +"$lno" "$file" | head -n 12 | grep -q 'Approved-by:' || {
    echo "Missing Approved-by near deviation: $file:$lno"
    exit 1
  }
done
```

---

## CI Gate Strategy (Recommended Rollout Plan)

### Phase 1 — Report-only (no failures)
- Run checks but don’t fail builds.
- Produce a report artifact (counts + file/line lists).

### Phase 2 — Fail on new violations only
- Track baseline (existing violations).
- Fail only if new violations are introduced in a PR.

### Phase 3 — Full enforcement
- Fail builds on any violation.
- Keep legacy remediation as planned work with dedicated commits.

> This staged approach prevents “CI lockdown” and helps teams adopt BARR‑C smoothly.

---

## PR Review Integration (Make Humans Focus on What Tools Can’t)

### What automation should pre-filter
- formatting, tabs, long lines
- obvious forbidden tokens
- suspicious assignments in conditions
- missing includes / unused includes (tool supported)
- most “style only” issues

### What humans should focus on
- concurrency correctness (ISR/thread shared state, atomicity)
- algorithm correctness and boundary cases
- API design, module boundaries, coupling
- assumptions and documentation accuracy
- deviation justification quality

---

## Review Checklist (Copy/Paste)

- [ ] Pre-commit hooks reject tabs, trailing whitespace, `.c` includes, forbidden keywords, long lines
- [ ] CI runs a fast scan on changed files (or full repo) and fails on violations
- [ ] Static analysis job catches semantic issues (init, signed/unsigned, null paths, switch completeness)
- [ ] Formatter is standardized; whitespace-only refactors are isolated in separate commits
- [ ] Deviations are auditable: required metadata present; CI flags missing Approved-by/Date
- [ ] PR template/checklist pushes reviewers toward logic and safety (not formatting)
