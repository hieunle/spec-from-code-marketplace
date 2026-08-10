# Change Request — <SECTION> of <shared doc>

**Target:** <doc> §<n> · **Owner:** <you> · **Basis:** code-verified analysis (companion requirements doc)

## How to use
Google Docs takes no patch, so each edit is applied by hand.
- **Locate:** a unique phrase to Find (Ctrl/Cmd+F). Chosen to be unique in the doc.
- **Action:** REPLACE / INSERT AFTER / INSERT NEW SUBSECTION.
- **New text:** written in the doc's house style — paste as-is.
Order: corrections first, then ⚠️-resolutions, then new content, then hand-offs, then group decisions.
Marker convention: ✅ = stated in code (file:line); ⚠️ = genuinely unconfirmed.

## Part A — Corrections (wrong or imprecise statements)
### A-1. <title>  [🔴 if it would misdirect a reader]
**Locate:** `<unique phrase>`
**Action:** REPLACE
**Current:** > <text>
**Replace with:** > <text>
**Why:** <evidence file:line>

## Part B — Resolve ⚠️ that code now settles
### B-1. <title>
**Locate:** `<phrase>` · **Replace with:** > <text with ✅> · **Why:** <file:line>

## Part C — Missing content (new subsections / tables)
<for table-heavy blocks with no figures: generate HTML via md2html.py and paste once, don't paste raw markdown>

## Part D — For other section owners (do NOT edit yourself)
| # | Issue | Route to |
|---|---|---|

## Part E — Group decisions (not a technical question)
<scope calls that need the whole team>

## Appendix — evidence map (each item → companion doc §)
