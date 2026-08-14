---
name: review
description: Use when an existing spec section needs rewriting or restructuring — duplicated narrative, wrong shape, doc-sourced claims, deleted figures. Argument: the section .md file.
---

# review — rewrite an existing section (core recipe 5b)

**REQUIRED BACKGROUND:** read the sibling `spec-from-code/SKILL.md` in full before
starting — it holds the method. This command pins recipe 5b:

1. Survey the heading map against the canonical structure (§1–8 — see
   `../revise/reference/spec-structure-template.md`) — list what folds where
   before touching prose.
2. Mine prior verified artifacts; spot-re-verify a third of reused evidence.
3. Fan out parallel verify tracks (PDF terminology extractor + per-area code
   verifiers); rewrite only after both return.
4. Apply the dedup rule and the readability contract while writing — not as a
   cleanup pass afterwards.
5. Meaningful names over internal codes; appendices under §8 Supporting
   materials, relettered A, B, C….
6. Re-draw deleted figures as mermaid at load-bearing points only.
7. Finish: `validate.py` + `term_check.py` + `dup_check.py` clean, then rebuild the
   paste deliverables (see `spec-publish`).

Scope note: `review` re-verifies content against code while rewriting. For a pure
structural/readability pass on a finished spec (no re-verification, customer
deliverable), use `/spec-from-code:revise` instead.
