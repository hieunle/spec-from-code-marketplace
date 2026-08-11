---
name: spec-review
description: Use when an existing spec section needs rewriting or restructuring — duplicated narrative, wrong shape, doc-sourced claims, deleted figures. Argument: the section .md file.
---

# spec-review — rewrite an existing section (core recipe 5b)

**REQUIRED BACKGROUND:** read the sibling `spec-from-code/SKILL.md` in full before
starting — it holds the method. This command pins recipe 5b:

1. Survey the heading map against the house shape (§1–7) — list what folds where
   before touching prose.
2. Mine prior verified artifacts; spot-re-verify a third of reused evidence.
3. Fan out parallel verify tracks (PDF terminology extractor + per-area code
   verifiers); rewrite only after both return.
4. Apply the dedup rule and the readability contract while writing — not as a
   cleanup pass afterwards.
5. Meaningful names over internal codes; appendices to the document end with
   section-number prefixes.
6. Re-draw deleted figures as mermaid at load-bearing points only.
7. Finish: `validate.py` + `term_check.py` + `dup_check.py` clean, then rebuild the
   paste deliverables (see `spec-publish`).
