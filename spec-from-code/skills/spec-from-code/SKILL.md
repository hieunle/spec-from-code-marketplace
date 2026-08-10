---
name: spec-from-code
description: Use when reviewing, writing, or extending a feature specification for the SITA WorldTracer system (or any legacy Java/PL-SQL codebase) by reading the actual source. Produces a code-verified requirements draft, a change request for the shared Google-Docs spec, and a handover report. Triggers on "review feature X", "spec for X", "verify the X section", "document X from the code".
---

# spec-from-code

Turn what the code actually does into a specification you can trust — with every
claim traceable to `file:line`, contradictions against the existing spec flagged,
and issues routed to whoever must resolve them.

This skill was distilled from a full pass over the **Claims** feature (PL/SQL + Java
service/DAO/validator + 151 JSP + DDL + the 300-page vendor spec). Reuse it for the
remaining features.

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

## Two knowledge graphs already exist — use them for LOCATE

- `.ua/knowledge-graph.json` — Java (763 files)
- `wto-core-database/.ua/knowledge-graph.json` — PL/SQL (162 packages, 310 tables with columns)

## The 9 phases

Phases 1–5 (LOCATE→WRITE) can run in a **single turn** by fanning out subagents.
Phases 6–9 (REVIEW→HANDOVER) are human-in-the-loop follow-ups.

### 1. LOCATE — scope the feature across all tiers
Grep by feature name, transaction codes, and package/class names across both graphs
and the source. Produce a file list grouped by tier. Gate: if >~100 files, sample by
relevance (name match + hit count), don't read blind.

### 2. HARVEST — plan reading batches
Group files into batches of ~6–13k lines. Keep each PL/SQL package's `.PSK`+`.PBK`
together. Include the JSP tier — it is the one most often skipped and most often
decisive.

### 3. ANALYZE — fan out subagents (this is what makes 1-turn possible)
Dispatch up to ~5 `understand-anything:file-analyzer` subagents **in parallel** (one
message, multiple tool calls). Give each the shared analyzer guide
(`templates/analyzer-GUIDE.md`, adapted per feature) + its batch file list. Each
returns `{nodes, edges, claimsFindings}` where every finding is:

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
