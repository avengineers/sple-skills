# Retrospective Output Template

Use this template for the retrospective document. Save to `doc/retrospectives/` with naming convention `YYYY-MM-DD_<phase-name>_retro.md`.

Sections marked *(optional)* should be omitted if the conversation didn't produce meaningful content for them. An honest short retro is better than a padded long one.

---

## Retrospective: [Phase Name]

**Date**: YYYY-MM-DD
**Phase/Sprint**: [Phase number or sprint identifier]
**Scope**: [Brief description of what was worked on]

### What Went Well

- [Concrete success — what worked, and ideally why]
- [Another success with enough context to be useful months later]

### What Could Be Improved

- [Challenge or friction point]
  - **Root Cause**: [Why this happened — not just the symptom]
  - **Action**: [Specific step to address it]
- [Another challenge]
  - **Root Cause**: [...]
  - **Action**: [...]

### Learnings

- [Something you now understand that you didn't before]
- [A technique, tool behavior, or domain insight worth remembering]

### Surprises *(optional)*

- [Something unexpected — wrong assumptions, unforeseen issues, unexpectedly positive outcomes]

### Metrics *(optional — include only if data is available)*

Pick metrics relevant to this phase. Not all will apply every time.

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Test Coverage (branch) | X% | Y% | ✅/❌ |
| MISRA Violations | X (Δ from baseline) | ≤ Y | ✅/❌ |
| Static Analysis Findings | X new / Y resolved | net decrease | ✅/❌ |
| Stack Usage (worst task) | X bytes / Y available | < 80% | ✅/❌ |
| Defects Escaped to HW | X | 0 | ✅/❌ |

### Patterns *(optional — include from 2nd retro onwards)*

- [Recurring theme or trend observed across multiple phases]
- [Improvement trend worth acknowledging]
- [Previous action item status: done / not done / partially]

### Action Items for Next Phase

1. [Specific, bounded action item with clear definition of done]
2. [Another action item — max 5 total]
3. [...]

### Overall Assessment

**Confidence for next phase**: [High / Medium / Low] — [1-2 sentences explaining why]

[2-3 sentences: What defined this phase? What's the one thing to carry forward? What's the biggest risk going into the next phase?]

### Risks Going Forward *(optional)*

- [Known risk or concern heading into the next phase]
- [Dependency or blocker that could cause trouble]
