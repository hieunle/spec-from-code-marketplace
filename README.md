# kms-spec-tools

A Claude Code plugin marketplace. Currently ships one plugin, **spec-from-code**:
review, write, extend, or revise a feature specification directly from source code,
with every claim traceable to `file:line`, and reshape the finished spec into the
canonical §1–8 structure for customer approval.

## Install

```
/plugin marketplace add hieunle/spec-from-code-marketplace
/plugin install spec-from-code@kms-spec-tools
```

Replace `hieunle/spec-from-code-marketplace` with wherever this repo actually lives
(`owner/repo` on GitHub, or a full git URL). After installing, restart Claude Code or
run `/plugin` to confirm the `spec-from-code` skill is listed.

## Requirements

The skill is designed to run on a fresh checkout with almost nothing extra:

- **python3** (3.6+, standard library only — no `pip install`) for the two bundled scripts.
- **Run from the root of the repository you are reviewing.** The skill's paths are
  relative to that root; call the bundled scripts by their full path.
- **Optional:** the [`understand-anything`](https://github.com/Egonex-AI/Understand-Anything)
  plugin. If present it makes codebase graphs and the analysis subagent richer, but the
  skill works fully without it — it falls back to grep and the built-in `general-purpose`
  agent. Not a prerequisite.
- Reading a vendor spec PDF uses Claude's built-in `Read` tool; `pdftotext` is a faster
  option for very large PDFs if installed, but not required.

## What the skill does

Ask Claude to "review feature X" (or run `/spec-from-code`) inside a WorldTracer-style
Java/PL-SQL repo. It runs a 9-phase flow — locate the feature across every tier
(PL/SQL, Java, JSP, DDL, spec PDF), analyse it with fan-out subagents, reconcile code
against the existing spec, and produce a requirements draft, a Google-Docs change
request, and a handover report.

### The short flow

```
/spec-from-code:new <feature>       # → <feature>-spec.md (canonical §1–8) + <feature>-evidence.md
/spec-from-code:publish <spec.md>   # → paste-ready Google-Docs HTML
```

`new` writes directly in the canonical §1–8 shape, so two commands take you from an
undocumented feature to a customer-facing document. The other four are conditional:
`review` (rewrite an existing section against code), `verify` (audit claims, change
nothing), `feedback` (verify reviewer comments before acting on them), and `revise` —
a BA-authored restructuring pass, built after BA review of the team's specs, that
reshapes specs **this pipeline did not write** (Velox-generated, hand-written, legacy)
into the canonical structure, reorganizing and de-duplicating without ever authoring
new content.

See `spec-from-code/skills/spec-from-code/SKILL.md` for the full method and the six
principles it is built on, and
`spec-from-code/skills/revise/reference/spec-structure-template.md` for the canonical
spec structure.

## Contents

```
.claude-plugin/marketplace.json        # this marketplace
spec-from-code/
  .claude-plugin/plugin.json           # the plugin manifest
  skills/spec-from-code/
    SKILL.md                           # the method (shared core)
    scripts/md2html.py                 # markdown → paste-ready Google-Docs HTML
    scripts/validate.py                # structural + canonical §1–8 conformance + anchor checks
    templates/requirements.md          # the canonical §1–8 spec (customer-facing)
    templates/evidence-notes.md        # its companion: file:line per REQ ID (internal)
    templates/                         # change-request / handover / analyzer-guide
  skills/new|review|verify|feedback|publish/
    SKILL.md                           # thin command skills over the shared core
  skills/revise/
    SKILL.md                           # BA restructuring pass for customer approval
    reference/spec-structure-template.md   # the canonical §1–8 spec structure
```

## Updating

Bump `version` in `spec-from-code/.claude-plugin/plugin.json`, commit, push. Users
re-pull with `/plugin marketplace update kms-spec-tools`.
