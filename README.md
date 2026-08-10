# kms-spec-tools

A Claude Code plugin marketplace. Currently ships one plugin, **spec-from-code**:
review, write, or extend a feature specification directly from source code, with every
claim traceable to `file:line`.

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

See `spec-from-code/skills/spec-from-code/SKILL.md` for the full method and the six
principles it is built on.

## Contents

```
.claude-plugin/marketplace.json        # this marketplace
spec-from-code/
  .claude-plugin/plugin.json           # the plugin manifest
  skills/spec-from-code/
    SKILL.md                           # the method
    scripts/md2html.py                 # markdown → paste-ready Google-Docs HTML
    scripts/validate.py                # structural + anchor checks before shipping
    templates/                         # requirements / change-request / handover / analyzer-guide
```

## Updating

Bump `version` in `spec-from-code/.claude-plugin/plugin.json`, commit, push. Users
re-pull with `/plugin marketplace update kms-spec-tools`.
