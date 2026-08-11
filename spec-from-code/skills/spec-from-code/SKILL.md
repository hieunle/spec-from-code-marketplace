---
name: spec-from-code
version: 2.0.0
description: Reverse-engineer a trustworthy feature specification from source code — locate a feature across every tier (UI/service/DAO/DB), verify what the code ACTUALLY does against the existing spec, and produce a code-verified requirements draft, a Google-Docs change request, and a handover report, every claim traced to file:line. Use this whenever someone needs to review, write, verify, or extend a feature spec against a real codebase, or asks "does the code match the spec / what does X actually do" — even if they never say the word "skill". Tuned for legacy Java/PL-SQL systems (SITA WorldTracer) but the method generalises to any codebase. Triggers: "review feature X", "spec for X", "verify the X section", "does the code agree with the spec", "document X from the code".
---

# spec-from-code

Turn what the code actually does into a specification you can trust — with every
claim traceable to `file:line`, contradictions against the existing spec flagged,
and issues routed to whoever must resolve them.

This skill was distilled from a full pass over the **Claims** feature (PL/SQL + Java
service/DAO/validator + 151 JSP + DDL + the 300-page vendor spec). Reuse it for the
remaining features.

## Invocation modes

The argument decides the flow — pick the narrowest mode that fits:

| Invocation | Flow |
|---|---|
| `new <feature>` | Full pipeline, phases 1–9 |
| `review <spec.md>` | Rewrite an existing section — recipe 5b |
| `verify <spec.md> [area]` | Verification only: audit every ✅ and S1-only claim, report verdicts, change nothing |
| `feedback <spec.md> + comments/screenshots` | Per-claim verdicts vs code, then sweep-patch the whole document (5b step 7) |
| `publish <spec.md>` | INTEGRATE only: `scripts/build_paste_html.py` → paste-ready HTML + instructions |

No diff/PR mode: the reviewed repo is a fixed snapshot — the code does not change
under the spec.

## Prerequisites (what a fresh checkout needs)

- **Run from the root of the repository you are reviewing** — the one holding the
  source (and optionally `.ua/` graphs). Paths in this skill are relative to that root.
- **python3** — for the two bundled scripts. No other packages needed.
- **The scripts live next to this SKILL.md.** Because the working directory is the repo
  being reviewed (not the skill folder), call them by their **full path**, e.g.
  `python3 "<this-skill-dir>/scripts/md2html.py" in.md out.html` — a bare
  `scripts/md2html.py` will not resolve. Find the skill dir from where this SKILL.md
  was loaded.
- **Reading the vendor spec PDF:** the `Read` tool opens PDFs directly (≤20 pages per
  call — use the `pages` arg for big specs). If `pdftotext` is installed, `pdftotext
  -layout spec.pdf out.txt` is faster for a 300-page document. Either works.
- **`understand-anything` plugin is OPTIONAL** (see the graph section). Everything here
  works without it — grep is the primary tool and a general-purpose subagent does the
  analysis. The plugin just makes graphs and analysis a bit richer if present.

## The one rule that changes everything

**The real specification is not in any document. It is spread across code and the
database, and the running system is more current than a 2019 PDF.** Element rules
live in `WTR_TRANSACTION_ELEMENT`; the error catalogue lives in `WTRErrConstants.java`
(1,020 messages, not the spec's ~54); scoring weights live in `WTR_MATCHING_POINT`
with a plain-language description column. **Query code/DB first, read the spec second.**

Corollary — each tier knows something no other tier does:

| Tier | Owns |
|---|---|
| JSP (`wtr-core-admin`) | which **screen** shows which field; client-side limits (maxlength caps a business value) |
| Java service/validator | mandatory-element and money rules; what gets **stored** where |
| Java DAO | the Java→PL/SQL call map (`{ call pastdate.pk_match.p_… }`) |
| PL/SQL (`wto-core-database`) | the real business logic and the matching engine |
| DDL export | true column definitions |
| Spec PDF | intent, and 2019's documented position (to diff against, not to trust) |

Screen ≠ storage ≠ rule. Skipping a tier means getting that tier's facts wrong.
(We once "corrected" a screen from DUS 3 to DUS 5 by reasoning from the Java storage
group — reading the JSP proved DUS 3 was right. Do not conclude past your evidence.)

## Source hierarchy — the contract every claim must satisfy

Code (S2) and the production DDL (S3) are **authoritative**. The vendor PDF (S1) serves
**terminology and divergence-baseline only** — it never proves behaviour. The owner
confirmed this ordering explicitly; treat it as standing policy.

Every Requirement and Scenario is one of exactly three things:

| Label | Meaning | Earns |
|---|---|---|
| ✅ | verified in code/DDL, `file:line` recorded | a Requirement/Scenario |
| **Divergence vs S1** | code does X, S1 says Y — both cited | a Requirement stating X, with the S1 position noted |
| *"S1-stated, no code located"* | only the PDF says it; implementation not found | a ⚠️ note — **never** a ✅, never a bare Requirement |

**A Requirement without a Scenario is the tell that it was doc-sourced.** Every
Requirement carries at least one WHEN/THEN Scenario derived from what the code does;
if you cannot write one, you have not read the code path yet — go read it (fan out a
verify subagent per area rather than transcribing the PDF).

When we finally code-verified a section drafted from S1, the PDF was wrong in seven
places at once (token length ≥4 not ≥3; country equality exact-only, no equivalence
table; a gate commented out by a defect fix; a refusal removed; a look-back not
enforced; report column offsets; "mandatory" params no longer checked). Assume the
same rate everywhere: **transcribing S1 is drafting defects.**

## Behaviour that lives in configuration, not code

When S1 (or the current spec) states an absolute — "CRT-only", "generated on the 2nd",
"these 57 words", "maximum 999", "worth 10 points" — **grep for a config table before
writing it as code behaviour.** In this system the pattern recurred five times in one
section: channel access = `WTR_TRANSACTION.VALID_CRT/VALID_TTY` flags (generic gate,
error 531); error wording = `WTR_ERROR_CODE`; excluded match words =
`WTR_MATCHING_EXCLUDED_STR`; report generation day = `WTR_REPORT_PARAMETER.MONTHLY_DAY`;
scoring weights = `WTR_MATCHING_POINT`.

Spec wording for these: **"the mechanism is code ✅; the values are a production
export"** — and the export joins the requirements baseline. A replacement must preserve
the *table*, not hard-code today's values.

## The knowledge graph — helper, not oracle

An Understand-Anything graph (`.ua/knowledge-graph.json`) indexes files, tables and
their summaries. It is a **shortcut for two things**: looking up a table's real column
definitions (the PL/SQL graph has the production DDL embedded) and reading the summary
of a file already analysed. It is **not** where you scope a feature — see the warning.

**Check what exists and how complete it is** before trusting it:
```bash
python3 - <<'EOF'
import json
for p in ['.ua/knowledge-graph.json','wto-core-database/.ua/knowledge-graph.json']:
    try:
        g=json.load(open(p)); n=g['nodes']
        from collections import Counter
        print(p, '→', len(n), 'nodes', dict(Counter(x['type'] for x in n)))
    except FileNotFoundError: print(p, '→ MISSING')
EOF
```

**If a graph is missing**, you do NOT need one — grep the source instead (LOCATE works
fine without it). *If* the optional `understand-anything` plugin is installed you can
build one with its `understand` skill (`/understand <dir>`), but treat that as a
nice-to-have, never a blocker.

**Query it** (don't dump the whole file — it is large):
```bash
# a table's real columns (PL/SQL graph has DDL embedded)
python3 -c "import json;g=json.load(open('wto-core-database/.ua/knowledge-graph.json'));[print(n['summary'][:300]) for n in g['nodes'] if n['type']=='table' and 'WTR_CLM_MATCH' in n['id']]"
# files a feature keyword touches
python3 -c "import json;g=json.load(open('.ua/knowledge-graph.json'));[print(n['name']) for n in g['nodes'] if n['type']=='file' and 'claim' in json.dumps(n).lower()]"
```

**⚠️ The graph is often partial — do NOT scope a feature from it alone.** In this repo
the Java graph covers ~20% of files (665 of 3,350); the PL/SQL graph is complete. So
**grep the source is the primary tool for LOCATE**, and the graph is a supplement for
column definitions and existing summaries. A feature absent from the graph is not
absent from the code.

## The 9 phases

Phases 1–5 (LOCATE→WRITE) can run in a **single turn** by fanning out subagents.
Phases 6–9 (REVIEW→HANDOVER) are human-in-the-loop follow-ups.

### 1. LOCATE — scope the feature across all tiers
**Grep the source** by feature name, transaction codes, and package/class names —
this is the primary tool (the graph may be partial). Use the graph only to enrich what
grep finds (summaries, column definitions). Produce a file list grouped by tier. Gate:
if >~100 files, sample by relevance (name match + hit count), don't read blind.

### 2. HARVEST — plan reading batches
Group files into batches of ~6–13k lines. Keep each PL/SQL package's `.PSK`+`.PBK`
together. Include the JSP tier — it is the one most often skipped and most often
decisive.

### 3. ANALYZE — fan out subagents (this is what makes 1-turn possible)
Dispatch up to ~5 subagents **in parallel** (one message, multiple tool calls). Use the
**`general-purpose`** agent type — it exists in every Claude Code install. (If the
`understand-anything` plugin is present, its `understand-anything:file-analyzer` type
returns graph-shaped output for free; prefer it only when available.) Give each the
shared analyzer guide (`templates/analyzer-GUIDE.md`, adapted per feature) + its batch
file list. Each returns `{findings}` — optionally `{nodes, edges}` too — where every
finding is:

```json
{"kind":"business-rule|validation|state-transition|integration|defect|config|dead-code",
 "statement":"one sentence", "evidence":"path/File:120-155 — what the code does",
 "relatesTo":"<sub-area>", "confidence":"high|medium|low"}
```

For 10k–25k-line files, tell the agent to grep for anchors first, then read windows —
never read blind, and say in the summary that coverage was targeted.

### 4. RECONCILE — classify every finding
Cross-check code against the existing spec and produce three buckets:
- **✅ confirmed** — stated in code with `file:line`
- **⚠️ genuinely unknown** — name *exactly what* is unknown and *who* can answer
- **defect** — code contradicts the spec or is plainly unintended

Two independent sources agreeing (e.g. JSP + spec + Java on mandatory elements) is the
highest confidence you can assign.

### 5. WRITE — draft the requirements
Use `templates/requirements.md`. Requirements are `MUST` statements; each is followed
by `WHEN`/`THEN` scenarios and a `✅`/`⚠️` marker. Keep a running defect table. This is
where the turn ends: output the draft + a preliminary coverage/confidence read.

### 5a. Before you number sections — is this a compound feature?
Most features fit one shape: a short description (§1–6) then all Requirements +
Scenarios gathered in §7, which is the last section. That shape assumes **one**
capability.

Some features are a **cluster** — a desk module *plus* its own matching engine *plus*
reporting (Claims was three-in-one). Do not just keep numbering §8, §9, §10… onto the
end: that pushes Requirements *outside* §7 and silently breaks the convention every
other feature follows (reviewers will notice). Decide the shape up front:

- **Split** — give each sub-capability its own §1–7 spec. Cleanest when the parts are
  genuinely separate features. Needs owner sign-off because it renumbers the doc.
- **Nest** — keep one spec, but put the extra capabilities as sub-sections under one
  umbrella heading (`8.1`, `8.2`…), and rename §7 so its scope is clear (e.g. "Core
  requirements"). Each sub-section carries its own description + requirements together,
  which reads better than tearing requirements away from what they describe.
  **Heading levels when nesting:** the flat house style puts `Requirement:` at h2 and
  `Scenario:` at h3; once you add a `7.x` grouping layer (h3), demote them **two
  levels** (h4/h5) or the Google-Docs outline inverts — Requirements outrank their
  own parent group. `validate.py` counts them at any level.

Either is fine; picking blind is not. Confirm the shape with the section owner before
writing, not after — reshaping a pasted Google-Docs section is expensive.

### 5b. Reviewing an EXISTING spec section (rewrite mode)

When the input is a drafted section to improve — not a feature to document from
scratch — phases 1–5 compress into this recipe (one Claims rewrite start-to-finish):

1. **Survey the structure first.** Grep the heading map. Score it against the house
   shape (§1–7): narrative duplicated between Key Terms / At a Glance / Journeys;
   sections numbered past §7; appendices adrift; leaked junk content. List what folds
   where before touching prose.
2. **Reuse prior verified artifacts.** A requirements doc with `file:line`, a handover
   report, extracted CSVs — mine these before re-analysing code. Re-verify a third of
   reused evidence by spot-check.
3. **Fan out two verify tracks in parallel:** one subagent extracts canonical
   terminology + section map from the vendor PDF (terms only); the others verify the
   section's strong claims against code, area by area. Rewrite only after both return.
4. **Dedup rule:** a fact lives in exactly one place — Key Terms holds one-to-three-line
   definitions, Journeys hold behaviour once, Requirements hold the binding form.
   At a Glance holds only comparisons and invariants, never a third retelling.
5. **Meaningful names over internal codes.** Parameter codes (`5/2`, `50/3`) appear
   once, in a settings table beside their real screen labels; body text uses the name.
6. **Appendices go to the document end,** labelled with the section number prefix
   (`Appendix 6A…`) so sibling sections can add their own without collision; update
   the body cross-references in the same pass.
7. **Reviewer feedback is a set of claims, not instructions.** Verify each against
   code before acting: this round one comment was right (a DPR path the spec skipped),
   one was half-right (the capability existed in code, mislabelled in review), and
   acting on either blindly would have been wrong. Reply with per-claim verdicts.
   **When a claim holds, fix the whole document, not the pointed-at spot:** grep for
   every same-kind occurrence (the term, the transaction, the sibling sections —
   Purpose, Scope, figures, At a Glance) and patch them in one sweep. A local patch
   invites the follow-up "why is §1 still wrong?" — which is exactly what happened
   when a DPR fix landed in §6/§7 but Purpose and Figure 1 kept saying CAC-only.
8. **Deleted figures are re-drawn as mermaid** at load-bearing points only (decision
   flows, pipelines, state groupings) — not one per scenario.
9. Re-run `validate.py` **and** `term_check.py` (against the repo-root `GLOSSARY.md`);
   rebuild the paste deliverables (see §7).

### Shared glossary — one vocabulary across every section
`GLOSSARY.md` at the repo root is the term registry: canonical term, one-line
definition, source, and **forbidden variants**. A section's Key Terms table derives
from it; a new term is added to the registry (with its S1/code source) *before* being
used, never defined ad hoc in one section. `term_check.py` enforces the forbidden
variants mechanically — run it in WRITE and in every review pass. A deliberate mention
of a foreign term (e.g. glossing what a sibling section calls the same thing) is
waived inline with `<!-- term-ok -->`.

### 6. REVIEW — loop, one lens per pass
Run separate passes, in this order, because they catch different things:
1. **Completeness** vs the sources (what's missing?)
2. **Accuracy** — re-verify *every strong claim* against `file:line`; this is where
   over-conclusions get caught
3. **Usability** — a worked example, acceptance criteria, data-migration notes
4. **Consistency** — numbering, cross-refs, no two sentences disagreeing

### 7. INTEGRATE — get it into the shared Google-Docs spec safely
- Write a **change request** (`templates/change-request.md`): each edit has a unique
  `Locate:` anchor + the exact replacement text, in the doc's house style.
- **Never edit another owner's section** — route those as a hand-off list.
- Google Docs renders **canvas**, so its text is not in the DOM and cannot be diffed
  live. For new blocks with tables, generate HTML with `scripts/md2html.py` and paste
  once — do **not** paste raw Markdown (literal `|` and `**` result). Check that the
  block contains no figures before wholesale-replacing (image refs live elsewhere).
- **Mermaid diagrams → Google Docs:** render each fence to PNG with
  `npx -y @mermaid-js/mermaid-cli -i fig.mmd -o fig.png -b white -s 2`, replace the
  fence with a placeholder before md2html, then substitute
  `<img src="data:image/png;base64,…" style="max-width:620px;width:100%">` into the
  HTML. Open the HTML in Chrome → Cmd+A, Cmd+C → paste; Docs uploads the images.
  Build **two** HTML files when appendices live at the document end (section body vs
  appendix block) so each pastes at its own spot.
- **Paste-target style trap:** pasting while the cursor sits on a heading-styled
  paragraph (e.g. where the old section heading was just deleted) makes Docs apply
  that heading style to every unstyled paragraph — table cells flood the outline.
  Safest: paste into a **blank Doc** first, check the outline, then copy Docs→Docs.
  Never Cmd+Shift+V (drops tables and images).

### 8. VERIFY — round-trip
Run `scripts/validate.py` on every fragment before shipping. After the user pastes,
have them download the doc as `.md` and diff — the canvas tier gives no other check.

### 9. HANDOVER — `templates/handover-report.md`
Coverage % measured **two ways** (vs the section's declared scope, and vs the whole
feature — they differ, and the gap is usually an unmade scope decision), confidence by
area, and issues routed by owner: dev / DBA / operations / the group.

## Toolkit

Both live in this skill's `scripts/`. Call by **full path** (the CWD is the repo being
reviewed, not this folder) — `python3 "<this-skill-dir>/scripts/<name>"`.

| Script | Does |
|---|---|
| `scripts/md2html.py IN.md OUT.html` | Markdown → paste-ready Google-Docs HTML (real tables). Self-reports table count and stray `\|`/`**`. |
| `scripts/validate.py SECTION.md [TARGET.md]` | Structural checks (unbalanced tables, unclosed fences, leaked `>`, empty headings, ⚠️ on requirements); with a target, verifies every `Locate:` anchor exists. |
| `scripts/build_paste_html.py SPEC.md OUT_PREFIX [--split-at "HEADING"]` | Full publish pipeline: renders mermaid fences to PNG (needs `npx`), embeds them base64, runs md2html, optionally splits body/appendices into two paste files. |
| `scripts/term_check.py SPEC.md GLOSSARY.md` | Flags forbidden term variants (with the canonical replacement) against the shared registry; `<!-- term-ok -->` on a line waives a deliberate mention. Non-zero exit on hits. |

## Markers (keep consistent with the existing spec)
`✅` = verified in code/DDL, with `file:line` — **the vendor PDF alone never earns ✅**
(see Source hierarchy).
`⚠️` = genuinely unconfirmed — and the note must say *what* is unknown, not just hedge.
Never leave `⚠️` on a Requirement or Scenario heading; resolve it or move it into a note.
Separate **fact from arithmetic from unknown** in one note when they mix: "the year
digit is code fact ✅; the ten-year repeat is arithmetic; whether collisions occurred
is a DBA query ⚠️" survives review — a blended claim does not.

## Scope note
Default to reading **every tier including JSP**. The truth-lives-in-code rule and the
per-tier ownership table are the two things that most change the result — internalise
them before starting.

## Changelog

- **2.0.0** (2026-08-11) — distilled from the Claims Investigation rewrite round:
  source-hierarchy contract (code authoritative; vendor PDF = terms + divergence
  baseline; "S1-stated, no code located" label; a Requirement without a Scenario is
  the doc-sourcing tell); "configuration, not code" heuristic with the five known
  config tables; invocation modes (`new`/`review`/`verify`/`feedback`/`publish`);
  recipe 5b for reviewing an existing section (incl. reviewer-feedback-as-claims +
  whole-document sweep, appendix `NA` prefixing, term symmetry); heading-demotion
  rule when nesting `7.x` groups; Google-Docs publish pipeline
  (`build_paste_html.py`, mermaid→PNG, paste-target style trap); shared glossary
  mechanism (`GLOSSARY.md` + `term_check.py` with `<!-- term-ok -->` waivers);
  `validate.py` made heading-level-agnostic; fact/arithmetic/unknown separation in
  markers.
- **1.0.0** — original 9-phase pipeline from the first Claims pass.
