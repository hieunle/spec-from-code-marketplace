---
name: publish
description: (spec-from-code) Use when a finished spec .md must go into the shared Google Doc — "make the paste HTML", "publish this section to Docs". Argument: the section .md file.
---

# publish — Google-Docs paste deliverables

**REQUIRED BACKGROUND:** read the sibling `spec-from-code/SKILL.md` in full before
starting — especially phase 7 INTEGRATE (mermaid→PNG pipeline, paste-target style
trap) and phase 8 VERIFY.

Flow:

1. Gate: `validate.py` + `term_check.py` + `dup_check.py` must pass first —
   publishing is never the place to discover structural issues.
2. Run `scripts/build_paste_html.py SPEC.md OUT_PREFIX [--split-at "HEADING"]`
   (needs `npx` for mermaid). Two files when appendices live at the document end.
3. Deliver paste instructions verbatim: open HTML in Chrome → Cmd+A, Cmd+C → paste
   into a **blank Doc** first (never onto a heading-styled paragraph, never
   Cmd+Shift+V) → check the outline → copy Docs→Docs.
4. Round-trip check: after the user pastes, have them download the Doc as `.md`
   and diff.
