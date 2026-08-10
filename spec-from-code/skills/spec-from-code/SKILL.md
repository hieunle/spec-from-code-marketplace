---
name: spec-from-code
description: Reverse-engineer a trustworthy feature specification from source code — locate a feature across every tier (UI/service/DAO/DB), verify what the code ACTUALLY does against the existing spec, and produce a code-verified requirements draft, a Google-Docs change request, and a handover report, every claim traced to file:line. Use this whenever someone needs to review, write, verify, or extend a feature spec against a real codebase, or asks "does the code match the spec / what does X actually do" — even if they never say the word "skill". Tuned for legacy Java/PL-SQL systems (SITA WorldTracer) but the method generalises to any codebase. Triggers: "review feature X", "spec for X", "verify the X section", "does the code agree with the spec", "document X from the code".
---

# spec-from-code

Turn what the code actually does into a specification you can trust — with every
claim traceable to `file:line`, contradictions against the existing spec flagged,
and issues routed to whoever must resolve them.

This skill was distilled from a full pass over the **Claims** feature (PL/SQL + Java
service/DAO/validator + 151 JSP + DDL + the 300-page vendor spec). Reuse it for the
remaining features.

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

Either is fine; picking blind is not. Confirm the shape with the section owner before
writing, not after — reshaping a pasted Google-Docs section is expensive.

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

## Markers (keep consistent with the existing spec)
`✅` = stated literally in code/DB, with `file:line`.
`⚠️` = genuinely unconfirmed — and the note must say *what* is unknown, not just hedge.
Never leave `⚠️` on a Requirement or Scenario heading; resolve it or move it into a note.

## Scope note
Default to reading **every tier including JSP**. The truth-lives-in-code rule and the
per-tier ownership table are the two things that most change the result — internalise
them before starting.
