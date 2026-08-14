# Capability Specification — Canonical Structure Template

A reusable structure for **reverse-engineered capability specs** (e.g. Velox-generated),
written for a **customer to review and approve as *ready for planning*** (WBS →
estimation → development). Proven on *Baggage File Lifecycle* and *Claims Investigation*.

## The one rule that governs everything

> **Sections 1–4 are CONTEXT. Section 5 (Requirements) is the IN-SCOPE, code-derived
> part of the project — it is what will actually be built.**

**What "source" means.** A reverse-engineered spec is built from two things: the
application **code**, and the **vendor specification documents** (the vendor's own PDFs —
e.g. WorldTracer *Tracing*, *Management*, *Glossary*, *Admin GUI*). §5 is **code-derived**.
Behaviour that appears **only in the vendor PDFs** — described there but not implemented
in the code — is *context*, not an in-scope requirement. ("Vendor/PDF" throughout this
document means exactly this: the vendor's specification PDFs, as opposed to the code.)

- All **deep detail** (rules, tables, error strings, edge cases, mechanisms) lives in
  **§5 Requirements**. Sections 1–4 give overview + vocabulary and **point down** to §5.
- **Never add a rule or scenario to §5 that is not derived from the source.** Context may
  describe **vendor-spec-only behaviour** (in the vendor PDFs but not in the code); it is
  not promoted into §5 unless the code implements it.
- When trimming duplication: a fact removed from context must already exist in its home
  (§5 or another context section). If it exists **only** in context, it **stays** in
  context — never inject it into §5.

## Sections are content-driven — never force or fabricate

- Sections **6 (Open Questions)**, **7 (Possible Known Issues)**, **8 (Supporting
  materials)**, and any **Appendices** are **OPTIONAL** — include them only when there is
  real content. No open questions → omit §6. No defects found → omit §7. No appendices →
  omit §8.
- This applies to **every** section and sub-section: if the source has no content for it,
  **leave it out or leave it empty — do NOT invent, pad, or hallucinate** content to fill
  a heading. A short honest "none identified" beats fabricated data.
- If you are unsure whether a section applies, **raise it as a question** for the owner
  (PO/BA) — do not guess.

## Section order & sub-sections

| # | Section | Role | Optional? | What goes here | What does NOT go here |
|---|---|---|---|---|---|
| 1 | **Purpose** | Context | Required | Why the capability exists; the trigger(s); a one-line "what it covers"; the core business outcome; the top-level states. ~1 short screen. | Detailed rules, tables, error strings, per-transaction behaviour. |
| 2 | **Scope** | Context | Required | The operational map: 60-second version; the N outcomes (overview); rules-on-every-outcome (short + pointers); quick/interim shortcuts; families/variants; set-up vs action; integrations/copies; **what is out of scope**. | Full mechanics / day-counts / worked examples (those are §5). |
| 3 | **Key Terms** | Context | Required | Grouped glossary tables: **term → meaning**. Vendor-PDF reference material with no §5 home. | Re-described rules/error strings already in §5. Write "Behaviour → §5" instead. |
| 4 | **Business Journey** | Context | Recommended | A lean narrative walk-through, one sub-section per lifecycle step (4.1…4.n) + a diagram each; an end-to-end overview. | "Read this as" restatements that only re-summarise. Deep rules → §5. |
| 5 | **Requirements** | **IN SCOPE** | Required | The binding, code-derived rules, grouped by functional sub-area (5.x); all detail/tables/mechanisms; testable scenarios. | Behaviour documented only in the vendor PDFs (not implemented in the code); rules invented while editing. |
| 6 | **Open Questions** | — | **Optional** | Every unresolved question the customer must answer, grouped A (changes what's built) / B (non-blocking) / Resolved. Omit if none. | Answers you invented. |
| 7 | **Possible Known Issues** | — | **Optional** | Defects, bugs, and divergences observed while reverse-engineering: code↔vendor-PDF mismatches, dead constants, documented-but-unenforced rules, risky/surprising behaviour — each traceable to a source line, for the dev team's awareness. Omit if none found. | Invented/speculative issues; items that are really requirements (→ §5) or business decisions (→ §6). |
| 8 | **Supporting materials** | — | **Optional** | Lettered appendices: source docs first, then reference tables / error catalog / operational notes. Omit if none. | — |

## §5 Requirements — canonical layout

```
## 5. Requirements
<confidence-marker legend: ✅ settled · ⚠️ confirmed-with-caveat · ❓ intent-unsettled>

### 5.x <Functional sub-area>                         ← group related requirements
#### Requirement: <assertion-style name> (REQ-<AREA>-###) <✅|⚠️|❓>
Confidence note (⚠️/❓)                                 ← only for ⚠️ and ❓
The system MUST …                                      ← the binding, code-derived rule
<detail: tables, error strings, config-dependence, mechanism, worked examples>
##### Scenario: <name> <✅|⚠️|❓>                        ← ≥1 per requirement; marker = that case's confidence
  - WHEN … / THEN … / AND …
**Read this as:** <plain-language aid>                 ← optional

#### <Detail block: element table / report layout / known defects>   ← non-requirement support inside a sub-area
```

Conventions:
- **Group** requirements under `### 5.x <sub-area>` (functional areas) — **this is a MUST,
  not optional**, even when the source is a flat list; see "Structure conformance" below
  for how to derive groups when none exist in the source.
- **Name** each requirement as a short **assertion** (e.g. "ABC is the single claim-form
  entry point"), followed by a stable `REQ-<AREA>-###` ID and a confidence marker. **Every
  requirement MUST have this ID** — assign one if the source doesn't have it (see
  "Structure conformance").
- Every requirement carries **≥1 `##### Scenario`** (WHEN / THEN / AND) as testable
  acceptance criteria.
- Stable IDs stay on every heading so cross-references survive edits.

## Confidence markers (on every requirement heading — and on every scenario)

| Marker | Meaning |
|---|---|
| ✅ | Settled — behaviour confirmed, no open question affects it. |
| ⚠️ | Confirmed behaviour **with a caveat** (config-dependent value, documented-but-unenforced rule, attribution/wording point). Carries a **Confidence note**. |
| ❓ | Behaviour known but **business intent unsettled** — the answer changes what is built. Carries a **Confidence note** + a linked Open Question. |

## §6 Open Questions — format (when present)

Group into **A. Changes what gets built** / **B. Needed but blocking nothing** /
**Resolved**. Each entry is an index entry for a caveat already in the body:

```
N. ❓ Q-### — <the question> (§<location in the body>)
   What the body says: "<verbatim quote from the body>"
   How it gets settled: <the query / owner / export that resolves it>
```

## Citation / marker policy

- Keep `⚠️` (caveats) and `❓` (open questions) wherever they carry meaning; put a
  `✅/⚠️/❓` confidence marker on every requirement heading **and on every scenario** (a
  scenario's marker shows the confidence of that specific case).
- Strip inline evidence citations (`✅ F-123`, "Evidence (for reviewers): …") from
  customer-facing prose; keep traceability in an internal notes file / appendix.
- Distinguish **internal** cross-references (`§5`, `§4.2`) from **external** vendor
  citations (`Tracing §8.11.1`, `Glossary §11`) — never renumber the external ones.

## Structure conformance — MUST apply (not optional)

Mechanical transforms every revised spec MUST end up with. These are the ones most often
skipped when a raw/exported spec is only lightly touched — apply them explicitly.

1. **Heading hygiene.** Exactly **one `#` H1** (the title); every section is `## N. Title`.
   **Strip** export cruft: pandoc `{#…}` anchors, escaped numbering (`## 5\.`), duplicate H1s.
2. **Scenario markers.** **Every** `##### Scenario` MUST carry a `✅/⚠️/❓` marker.
3. **Known issues → §7.** "Known defects"/bugs/divergences MUST sit in **§7 Possible Known
   Issues**, never inside §5.
4. **Appendices → §8.** Appendices MUST be wrapped under **`## 8. Supporting materials`**,
   **relettered A, B, C…** (drop vendor numbering such as "6A"), source docs first.
5. **Unified numbering 1–8.** Renumber sections and fix internal cross-refs; keep external
   vendor citations untouched.
6. **No non-canonical sections survive.** Sections outside 1–8 (e.g. **Actors**, **At a
   Glance**) MUST be **dissolved**, not relocated as a block — fold each piece into an
   **existing §5 requirement (preferred)** or a context section; never create a new
   requirement/scenario from them.
7. **§5 requirements grouped under `### 5.x <sub-area>` — even when the source is flat.**
   Keep and renumber existing grouping if present. If the source is a flat list, derive
   sub-area groups from the requirements' own subject matter (cluster by transaction
   family / functional outcome already implied by their content) and name each group
   descriptively. This is organisation only — no requirement or scenario is added,
   removed, or reworded by grouping them.
8. **Every requirement has a stable `REQ-<AREA>-###` ID.** Keep existing IDs unchanged.
   If the source has none, **assign** sequential 3-digit numbers in document order
   (continuing across sub-areas, not restarting per group), with `<AREA>` a short stable
   capability abbreviation (e.g. `CLM`, `BFL`). Record the assigned scheme in the notes
   file — an ID is a label, not a business fact, so assigning one is not fabrication, but
   the scheme must be applied consistently so re-runs converge on the same numbering.

**If the revised file is byte-identical to the input, the pass did not run.** Prove
conformance with the self-check in the skill before declaring done.

## Editing discipline (when revising an existing spec)

- **Reorganize / relocate / de-duplicate — do not rephrase** kept text; preserve wording,
  IDs, and error strings verbatim. Add tables/lists where they aid reading.
- **Nothing missing / nothing hallucinated / no outside-knowledge bias** (see checklist).
- **Never force or fabricate** content to fill a section — omit empty optional sections;
  leave silent what the source is silent on.
- **Raise decisions, don't guess.** Any section or sub-section not clearly accounted for —
  no obvious home, ambiguous placement, unclear context-vs-§5, or a fate the source does
  not settle — is raised as an explicit question for the owner (PO/BA), presented as a
  concrete choice. Record undecided items in the notes file.

## Verification checklist (run after any structural change)

1. **Inventory preserved:** every requirement ID, open-question ref, diagram, and
   error/system string still present (grep-diff against a pre-edit inventory).
2. **§5 substance unchanged:** requirement / scenario headings and MUST-statements match
   the source — no rule or scenario added or removed.
3. **Markers:** any `⚠️`/`❓` count drop is duplicate-removal only; every distinct caveat
   and open question still appears at least once.
4. **No fabrication:** every statement is defensible by a source line; no section was
   padded with invented content; empty sections were omitted, not filled.
5. **Renders:** rebuild the deliverable and confirm tables + diagrams intact.
