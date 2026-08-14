---
name: revise
description: >-
  Revise, restructure, de-duplicate, or clean up a capability/requirements
  specification for customer review — especially reverse-engineered or
  Velox-generated specs that are long, fragmented, repetitive, or have detail in
  the wrong place. Use when the user asks to tidy up / shorten / reorganize / make
  a spec readable, move detail into the right section, or prepare a spec for a
  customer (e.g. SITA) to approve as ready for planning. Not for writing a brand-new
  spec from scratch. Argument: the spec file (.md or .docx).
---

# revise — restructure a spec for customer approval

Restructure an existing spec into the canonical shape while **preserving every fact**.
This is an editing / reorganization task, **not authoring** — move facts to their correct
home; do not invent, and do not just shuffle blocks around.

**Where this sits in the pipeline.** This command is for specs **this pipeline did not
write**: Velox-generated output, hand-written team specs, legacy or exported documents
that arrive long, fragmented, or with detail in the wrong place. A spec produced by
`/spec-from-code:new` is already in the canonical shape, so running `revise` on it is a
no-op by design — if it is not, that is a bug in `new`, not work for this command.

It never re-verifies claims against code. If a claim looks wrong while revising, raise
it or hand it to `/spec-from-code:verify` — do not settle it here.

Its reference template (`reference/spec-structure-template.md`) is the plugin's **single
canonical spec structure**; `validate.py` in the sibling `spec-from-code/scripts/`
enforces most of it mechanically (see the self-check below).

## The governing rule (read first)

**Sections 1–4 are CONTEXT. Section 5 (Requirements) is the IN-SCOPE, code-derived part
of the project — what will actually be built.**

**"Source" = the two things the spec is reverse-engineered from:** the application
**code**, and the **vendor specification documents** (the vendor's own PDFs — e.g.
WorldTracer *Tracing*, *Management*, *Glossary*, *Admin GUI*). §5 is **code-derived**.
Behaviour found **only in the vendor PDFs** — described there but not implemented in the
code — is *context*, not an in-scope requirement.

- All deep detail (rules, tables, error strings, mechanisms, worked examples) lives in
  **§5 Requirements**; §1–§4 give overview + vocabulary and point down to §5.
- **Never add a rule or WHEN/THEN scenario to §5 that is not in the source.** Context may
  describe **vendor-spec-only behaviour** (documented in the vendor PDFs but not in the
  code); it is not promoted into §5 unless the code implements it.
- When removing duplication: a fact removed from context must already exist in its home.
  If it exists **only** in context, it **stays** in context — never inject it into §5.

The full target structure (sections, sub-sections, "what goes here / what does NOT", the
requirement block shape, confidence markers) is in
`reference/spec-structure-template.md` — read it before restructuring.

## Removing a non-canonical section (Actors, At a Glance, and anything not in 1–8)

A source section that is **not** one of the canonical 1–8 (most often **Actors** and
**At a Glance**, but any other too) is **DISSOLVED, not relocated as a block.** Take its
detail apart and redistribute each piece, in this priority order:

1. **DOWN into an EXISTING §5 requirement — PREFERRED.** If the detail elaborates a rule
   §5 already states, fold it in there as extra detail / a table / a caveat on that
   requirement. **Do NOT create a new requirement or a new scenario for it** (that would
   add scope not derived from code).
2. **UP into a context section** (Purpose / Scope / Key Terms / Business Journey) — only
   if it is overview / vocabulary / narrative, not a code rule.
3. If it fits neither, or you cannot tell — **raise it as a decision** for the owner.

Hard "don'ts": never keep the removed section as its own heading; never move it wholesale
into a new location as a labelled block; never let it become a new §5 rule/scenario. A
diagram from a dissolved section attaches to the **existing** requirement (or context
step) it illustrates, with a plain caption — no "relocated from…" note.

## Editing discipline

- **Reorganize / dissolve into the right home / de-duplicate — do NOT rephrase.** Keep
  wording, requirement IDs, and error strings verbatim. Moving content means folding it
  into its correct home (see "Removing a non-canonical section"), not shifting a labelled
  block to a new spot. The only allowed new words are plain captions on diagrams attached
  to an existing requirement, and minimal connective words when merging two source sentences.
- **No new terminology, no new requirements, no invented facts.** Where the source is
  silent, unclear, or contradictory, leave it — flag it, never fill it from your own
  domain knowledge.
- **Sections are content-driven — never force or fabricate.** §6 Open Questions, §7
  Possible Known Issues (defects/divergences observed in the code, each traceable to a
  source line), §8 Supporting materials, and appendices are **optional**: include a
  section only when real content exists. If the source has no content for a section or sub-section, **omit it or
  leave it empty — never invent, pad, or hallucinate** data/info to fill a heading. A
  short honest "none identified" beats fabricated content. When unsure whether a section
  applies, raise it as a question rather than guessing.
- Add tables/lists where they aid reading (layout may change; meaning may not).
- **Markers:** keep all `⚠️` (caveats) and `❓` (open questions); put a `✅/⚠️/❓`
  confidence marker on every requirement heading **and on every scenario** (the
  scenario's marker shows the confidence of that specific case). Strip inline evidence
  citations
  (`✅ F-123`, "Evidence (for reviewers): …") from customer-facing prose — move
  traceability to an internal notes file.
- **Cross-references:** distinguish internal (`§5`, `§4.2`) from external vendor
  citations (`Tracing §8.11.1`, `Glossary §11`). Renumber only internal ones.
- **Raise decisions, don't guess.** If any section or sub-section is not clearly
  accounted for — its content has no obvious home, its placement is ambiguous, it is
  unclear whether it is context or an in-scope (§5) requirement, or the source does not
  determine its fate — **stop and raise it as an explicit question for the owner (PO/BA)
  to decide.** Never resolve an unmentioned or ambiguous sub-section by guessing. Present
  each such item as a concrete choice (e.g. "keep in Scope / move to §5 / drop"), wait
  for the decision, then act. Collect any not-yet-decided items in the notes file so none
  is silently dropped or silently placed.

## Procedure

1. **Read source & convert.** `pandoc -t markdown source.docx -o work.md`. Extract
   images once (`unzip source.docx`, keep `word/media/`) for the eventual rebuild.
2. **Build an inventory** from the source for the completeness check: every requirement
   ID, every open-question ref, every error/system string, every image, every table.
3. **Map before cutting.** List every source section and classify it: **canonical**
   (maps to one of 1–8) or **to-dissolve** (Actors, At a Glance, anything else). For each
   to-dissolve section, decide each piece's home now — existing §5 requirement (preferred)
   / context section / raise-as-decision. Confirm what each dedup target already has a
   home for (grep the §5 region) before removing it from context.
4. **Restructure deterministically.** Prefer a small transform script over source
   (slice verbatim sections; author only the trimmed intros; insert relocations at
   unique anchors; renumber headings + internal refs last). This keeps tables verbatim
   and makes the whole file reproducible.
5. **Verify (see below).** Fix any finding, then rebuild.
6. **Rebuild the deliverable.** `pandoc work.md -o output.docx` run from the folder
   holding `media/` so image paths resolve. Render to PDF and eyeball if a renderer
   (LibreOffice/`soffice`) is available.
7. **Write an internal notes file** (`spec-review-notes.md`): a change-log (what moved
   where, what was de-duplicated and its single surviving home), the relocated evidence,
   and any homeless/unclear items flagged for the owner. Not for the customer.

## Structure conformance — MUST apply (not optional)

These are mechanical transforms that a revised spec MUST end up with. They are the ones
most often skipped — apply them explicitly, then prove them with the self-check below.

1. **Heading hygiene.** The file MUST have exactly **one `#` H1** (the title); every
   section MUST be `## N. Title`. **Strip** document-export cruft: pandoc `{#…}` anchors,
   escaped numbering (`## 5\.`), and any duplicate H1s.
2. **Scenario markers.** **Every** `##### Scenario` MUST carry a `✅/⚠️/❓` marker — not
   just the requirement headings.
3. **Known issues → §7.** Any "Known defects"/bugs/divergences MUST be lifted **out of
   §5** into the dedicated **§7 Possible Known Issues** (optional) section.
4. **Appendices → §8.** Loose appendices MUST be wrapped under **`## 8. Supporting
   materials`**, **relettered A, B, C…** (drop vendor numbering like "6A"), with source
   documents listed first.
5. **Unified numbering.** Sections MUST be renumbered to the canonical **1–8**; fix
   internal cross-references, keep external vendor citations (`Tracing §8.11.1`) untouched.
6. **No non-canonical sections survive.** No section outside 1–8 may remain as its own
   heading — Actors, At a Glance, and the like MUST be dissolved (detail folded into an
   existing §5 requirement, preferred, or into a context section).
7. **§5 requirements MUST be grouped under `### 5.x <sub-area>`** — even when the source
   is a flat list. If the source already groups them, keep and renumber that grouping.
   If the source is flat, **derive sub-area groups from the requirements' own subject
   matter** (cluster by transaction family / functional outcome already implied by their
   content — e.g. all create-related requirements together, all suspend/reinstate
   together) and name each group descriptively. This is **organisation only** — it moves
   requirements into groups, it does not add, remove, or reword any requirement/scenario.
8. **Every requirement MUST carry a stable `REQ-<AREA>-###` ID.** If the source already
   has IDs, keep them unchanged. If the source has **no** IDs, **assign them**: sequential
   3-digit numbers in document order (numbering continues across sub-areas, it does not
   restart per group), format `REQ-<AREA>-###` where `<AREA>` is a short, stable
   abbreviation of the capability (e.g. `CLM` for Claims, `BFL` for Baggage File
   Lifecycle). Record the assigned ID scheme in the internal notes file so the owner sees
   it — an ID is a label, not a business fact, so assigning one does not violate
   "no invented facts," but the scheme must be consistent so re-runs converge.

**If the output is byte-identical to the input, the pass did NOT run** — a
correctly-applied revision of a raw/exported spec always changes it.

### Self-check (run after transforming — every line MUST pass)

**Run the shared validator first** — it covers items 1, 2, 3, 4, 6, 7 and 8 above and
reports them with line numbers:

```bash
python3 "<spec-from-code-skill-dir>/scripts/validate.py" out.md
```

The greps below are the same checks without the dependency, useful when you only have a
shell or want to prove one item in isolation:

```bash
test "$(grep -c '{#' out.md)" -eq 0            # 0 = no export anchors left
test "$(grep -cE '^# ' out.md)" -eq 1          # exactly one H1
# every scenario carries a marker:
test "$(grep -cE '^#+ Scenario:' out.md)" \
   = "$(grep -E '^#+ Scenario:' out.md | grep -cE '✅|⚠️|❓')"
grep -q '## 8\. Supporting materials' out.md   # appendices wrapped
! grep -qiE '^#+ .*Known (defects|issues)' <(sed -n '/^## 5\./,/^## 6\./p' out.md)  # none left in §5
! grep -qiE '^## .*(Actors|At a Glance)' out.md   # non-canonical sections dissolved
grep -qE '^### 5\.[0-9]' out.md                # §5 requirements are grouped 5.x
# every requirement carries a stable ID:
test "$(grep -cE '^#+ Requirement:' out.md)" \
   = "$(grep -E '^#+ Requirement:' out.md | grep -cE 'REQ-[A-Z]+-[0-9]+')"
```

## Verification checklist — nothing missing / hallucinated / biased

1. **Inventory preserved:** grep-diff the refined file against the pre-edit inventory —
   every requirement ID, open-question ref, diagram, and error/system string still present.
   Any drop must be an intended de-dup, logged with its surviving home.
2. **§5 substance unchanged:** requirement / scenario headings and MUST-statements are
   byte-identical to the source — no rule or scenario added or removed
   (`diff` the `### Requirement` / `#### Scenario` headings).
3. **Markers:** any `⚠️`/`❓` count drop is duplicate-removal only; every distinct caveat
   and open question still appears at least once.
4. **Fidelity:** relocated text is verbatim; no new claim, number, error string, or
   requirement appears that is not traceable to a source line.
5. **No outside bias:** every statement is defensible by a source line; gaps stay gaps
   (flagged), never "completed" from general knowledge.
6. **No fabrication:** no section was padded with invented content; empty optional
   sections were omitted, not filled.
7. **Renders:** rebuilt deliverable opens with tables + diagrams intact.

## Deliverables

- The refined spec (`.md` for review/diff, then rebuilt `.docx`).
- `spec-review-notes.md` — internal change-log + verification results + flagged items.
