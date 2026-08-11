---
name: feedback
description: (spec-from-code) Use when reviewer comments or screenshots about a spec section arrive and must be verified and applied — "is this feedback right", "reviewer says X is wrong". Arguments: the section .md file + the comments/screenshots.
---

# feedback — feedback is claims, not instructions

**REQUIRED BACKGROUND:** read the sibling `spec-from-code/SKILL.md` in full before
starting — especially recipe 5b step 7 and the Impact pass.

Flow:

1. Decompose the feedback into individual **claims**. Reviewer authority proves
   nothing: verify each claim against code (`file:line`) before acting.
2. Reply with **per-claim verdicts**: right / half-right (say which half) / wrong —
   each with evidence.
3. For every claim that holds, apply the fix **plus the Impact pass** over the fixed
   surface checklist (Purpose → glossary), concluding `updated`/`unaffected` per
   surface — by cross-reference, not restatement.
4. Finish: `validate.py` + `term_check.py` + `dup_check.py` clean; rebuild paste
   deliverables if the spec changed.
