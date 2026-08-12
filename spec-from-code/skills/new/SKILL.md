---
name: new
description: Use when a feature has no spec section yet and one must be written from the codebase — "document X from the code", "write the spec for X". Argument: the feature name/area.
---

# new — full pipeline (phases 1–9)

**REQUIRED BACKGROUND:** read the sibling `spec-from-code/SKILL.md` in full before
starting — it holds the method (source hierarchy, per-tier truth ownership,
readability contract, glossary, scripts). This command only pins the flow.

Flow:

1. Confirm the **spec shape** with the owner first (core 5a): single capability
   (§1–7) or compound (split vs nest)?
2. Run phases 1–5 in one turn: LOCATE (grep-first) → HARVEST → ANALYZE (parallel
   subagents) → RECONCILE (three buckets + open-question discipline) → WRITE
   (readability contract applies from the first draft).
3. Human-in-the-loop follow-ups: REVIEW (5 lenses, incl. Redundancy) → INTEGRATE →
   VERIFY → HANDOVER.
4. Before any handover: `validate.py`, `term_check.py` (with the repo glossaries),
   `dup_check.py` — all clean.
