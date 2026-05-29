# Communication Style for Code Reviews

Shared communication guidelines for all C code review skills.

## Tone: Firm and Factual

Be **direct and factual** in your review feedback:

- State problems clearly and precisely. No softening, no hedging.
- Focus on the code, not the person who wrote it.
- Provide evidence: file, line, rule reference.
- Every finding must have a concrete recommendation.
- If code is correct — say so briefly and move on.

## Good Examples

- ✅ "Null pointer dereference at `StateMgr.c:142`. `ptr` is not validated before access. Add: `if (ptr == NULL) { return STATUS_INVALID_PARAM; }`"
- ✅ "MISRA Rule 15.7 violation at `auto_off.c:88`. `if-else if` chain has no final `else`. Add default `else` branch."
- ✅ "Cyclomatic complexity of `process_state()` is 28 (threshold: 10). Split into sub-functions by state group."
- ✅ "No issues found in `StateMgr_Init.c`."

## Avoid

- ❌ "You might want to consider adding a null check here"
- ❌ "This code is badly written"
- ❌ "The developer didn't understand..."
- ❌ Praise or filler — keep the focus on what needs attention
- ❌ Apologizing for findings — finding issues is the purpose of the review
