---
name: new
description: Use when a feature has no spec section yet and one must be written from the codebase — "document X from the code", "write the spec for X". Produces a canonical §1–8 customer-facing spec plus its evidence file in one pass. Argument: the feature name/area.
---

# new — full pipeline (phases 1–9)

**REQUIRED BACKGROUND:** read the sibling `spec-from-code/SKILL.md` in full before
starting — it holds the method (source hierarchy, per-tier truth ownership, marker
semantics, readability contract, glossary, scripts). This command only pins the flow.

**What comes out:** a spec already in the canonical §1–8 shape — no restructuring pass
needed afterwards. `templates/requirements.md` is that shape; write into it from the
start rather than drafting loose and reshaping later.

Flow:

1. Confirm the **spec shape** with the owner first (core 5a): single capability, or a
   cluster to nest as separate `5.x` groups / split into separate specs?
2. Run phases 1–5 in one turn: LOCATE (grep-first) → HARVEST → ANALYZE (parallel
   subagents) → RECONCILE (four buckets → markers + sections) → WRITE.
3. WRITE produces **two files together**, never the spec alone:
   - `<feature>-spec.md` from `templates/requirements.md` — customer-facing, markers
     on every requirement and scenario, `REQ-<AREA>-###` IDs, no `file:line`.
   - `<feature>-evidence.md` from `templates/evidence-notes.md` — `file:line` per REQ
     ID, coverage gaps, the ID scheme, open decisions for the owner.
4. Human-in-the-loop follow-ups: REVIEW (5 lenses, incl. Redundancy) → INTEGRATE →
   VERIFY → HANDOVER.
5. Before any handover: `validate.py` (structural **+ canonical §1–8 conformance**),
   `term_check.py` (with the repo glossaries), `dup_check.py` — all clean.

Then `/spec-from-code:publish` when it is ready for the shared Google Doc. You should
not need `/spec-from-code:revise` on your own output — that command is for specs this
pipeline did not write.
