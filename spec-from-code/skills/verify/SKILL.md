---
name: verify
description: Use when a spec's claims must be audited against the code without changing the document — "does the code agree with the spec", "verify the X section". Arguments: the section .md file, optionally an area to focus on.
---

# verify — audit claims, change nothing

**REQUIRED BACKGROUND:** read the sibling `spec-from-code/SKILL.md` in full before
starting — especially the source-hierarchy contract and marker rules.

Flow — this mode is **read-only on the spec**:

1. Enumerate every ✅ claim and every S1-only statement in scope.
2. Fan out verify subagents per area; each claim gets a verdict:
   **confirmed** (`file:line`) / **divergence vs S1** (both cited) / **not located**.
3. Check the "configuration, not code" heuristic on every absolute the spec states.
4. Report the verdict table + suggested relabels (✅ → ⚠️ confirmed-with-caveat,
   ❓ intent-unsettled, or Divergence). Do NOT
   edit the spec — hand the verdicts to the owner (or to `spec-feedback` /
   `spec-review` if a rewrite is then requested).
