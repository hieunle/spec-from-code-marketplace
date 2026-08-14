# <FEATURE> — Capability Specification

**Status:** Draft v1 · **Owner:** <PO/BA> · **Capability:** <feature / system identifier>
**Audience:** the customer, to review and approve as *ready for planning* (WBS →
estimation → build).

> **This template writes TWO files.** This one is customer-facing: confidence markers
> stay, `file:line` evidence does not. Each requirement's evidence goes to the companion
> `<feature>-evidence.md` (`templates/evidence-notes.md`), keyed by REQ ID, so the dev
> team keeps full traceability while the customer reads a clean document. **Write both
> as you go** — reconstructing evidence afterwards costs a whole re-verification pass.
>
> **Shape: canonical §1–8** (`../../revise/reference/spec-structure-template.md` is the
> authority). §1–4 are context; **§5 is the in-scope, code-derived part — what actually
> gets built**. §6–8 are optional: include a section only when real content exists, and
> never pad a heading with invented material. A cluster of sub-capabilities nests as
> separate `5.x` groups, not as extra top-level sections.
>
> Delete this block and every `<…>` prompt before shipping.

## 1. Purpose

<Why the capability exists, what triggers it, a one-line "what it covers", the core
business outcome, the top-level states. About one short screen. Deep rules, tables and
error strings belong in §5 — point down to it instead of restating.>

## 2. Scope

<The operational map: the 60-second version; the N outcomes in overview; rules that apply
to every outcome (short, with pointers to §5); shortcuts and interim states; families and
variants; set-up vs action; integrations and copies.>

**Out of scope:** <what this capability deliberately does not cover — the boundary the
customer is approving.>

## 3. Key Terms

<Grouped glossary tables, term → meaning. Definitions come verbatim (or closely
paraphrased) from the project's canonical glossary. Behaviour does not live here —
write "Behaviour → §5.x" instead of re-describing a rule.>

| Term | Meaning |
|---|---|

## 4. Business Journey

<A lean narrative walk-through: one sub-section per lifecycle step, each with a diagram.
This is the story a business reader follows end to end. Deep rules stay in §5.>

### 4.1 <Step name>

<Narrative. Then the diagram — a mermaid fence, never a "Diagram: X" placeholder.>

## 5. Requirements

Confidence markers — **every requirement heading and every scenario carries one**:
✅ settled · ⚠️ confirmed with a caveat (carries a Confidence note) · ❓ behaviour known
but business intent unsettled (carries a Confidence note + a linked §6 question).

### 5.1 <Functional sub-area>

<Group related requirements by transaction family or functional outcome. Grouping is
organisation only — it never adds, removes, or rewords a requirement.>

#### Requirement: <short assertion-style name> (REQ-<AREA>-001) ✅

The system MUST <the binding, code-derived rule>.

<Supporting detail that IS the contract: tables, error strings, config-dependence,
mechanism, worked examples. A value that lives in a config table is stated as
"the mechanism is code; the values are a production export" — the export joins the
requirements baseline.>

##### Scenario: <name> ✅

- WHEN <precondition>
- THEN <observable outcome>
- AND <further outcome>

#### Requirement: <name> (REQ-<AREA>-002) ⚠️

**Confidence note:** <exactly what the caveat is — a config-dependent value, a
documented-but-unenforced rule, an attribution point. Never a bare hedge.>

The system MUST …

##### Scenario: <name> ⚠️

- WHEN … / THEN …

#### Data model — <entity>

<Real column definitions from the DDL, identity/keying rules, the state model. This sits
inside the sub-area whose requirements it underpins, not in an appendix: a reader needs
it to verify those requirements.>

## 6. Open Questions

*Optional — omit the section entirely if there are none.*

Grouped **A. Changes what gets built** / **B. Needed but blocking nothing** / **Resolved**.
Each entry indexes a caveat already in the body; the body references the ID only and never
restates the question.

**A. Changes what gets built**

1. ❓ Q-001 — <the question> (§<location in the body>)
   What the body says: "<verbatim quote>"
   How it gets settled: <the query / owner / export that resolves it>

## 7. Possible Known Issues

*Optional — omit if none found.*

<Defects, divergences and surprises observed while reverse-engineering: code↔vendor-doc
mismatches, dead constants, documented-but-unenforced rules. For the dev team's awareness.
Each traces to a source line recorded in the evidence file — the `file:line` itself stays
out of this table.>

| ID | Finding | Where | Impact |
|---|---|---|---|
| ISSUE-001 | … | §5.x / <component> | … |

## 8. Supporting materials

*Optional — omit if none. Appendices are lettered A, B, C… and hold **lookup material
only**; anything the reader needs to understand or verify a requirement belongs under
that requirement in §5. Each appendix declares its role in its first line.*

### Appendix A — Source documents

*Reference — lookup only.*

| # | Source | Provides |
|---|---|---|
| S1 | <vendor spec PDF, rev/date> | intent, documented position (not proof of behaviour) |
| S2 | <PL/SQL packages> | implemented behaviour |
| S3 | <DDL export> | real column definitions |
| S4 | <Java service/DAO/validator> | rules, storage, call map |
| S5 | <JSP screens> | screen↔field mapping, client limits |

### Appendix B — Replacement-project notes

*Informative — not part of the current capability's behaviour.*

<Non-functional constraints, data-migration considerations, and modernization risks.
These describe building the replacement, not what the existing system does, so they sit
here rather than in §5 where the customer approves in-scope behaviour.>

### Appendix C — <error catalogue / currency list / config export>

*Reference — lookup only.* — or — *Normative export — values join the requirements baseline.*
