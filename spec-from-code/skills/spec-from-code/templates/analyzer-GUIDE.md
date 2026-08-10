# Analyzer guide — <FEATURE> pass (fill in the angle-bracket parts)

Adapt this per feature, write it to the working dir, and hand its path to each
`file-analyzer` subagent along with that batch's file list.

## Project context
SITA WorldTracer. Struts 1 web (`wtr-core-admin`, JSP + `<bean:message key=...>`
labels in `ApplicationResources.properties`) → EJB facade → service → hand-written
JDBC DAO (`OracleCallableStatement`, no ORM) → Oracle PL/SQL. Claims/archive data in
the `PASTDATE` schema; live tracing in `OLTP`.

## Feature under review
<FEATURE> — <one line>. Transaction codes: <...>. Key packages/classes: <...>.

## Two required outputs (one JSON file at the path in your prompt)
`{"nodes":[...], "edges":[...], "findings":[...]}`

**Nodes/edges:** one `file:` node per file (no exceptions), `filePath/name/summary/
tags/complexity/language`. Summaries say WHAT the file does, not HTML/boilerplate.

**findings** — the important output:
```json
{"kind":"business-rule|validation|state-transition|integration|defect|config|dead-code",
 "statement":"one sentence as a requirement or observed behaviour",
 "evidence":"path/File:line-range — what the code actually does",
 "relatesTo":"<sub-area or 'screen-mapping'|'money'|'security'|'unknown'>",
 "confidence":"high|medium|low"}
```

## Priorities (reorder per feature)
1. **Validation rules** — mandatory/optional, formats, length & occurrence caps,
   rejection conditions, and the exact error text.
2. **Lifecycle** — create/amend/close/etc; how records are keyed and referenced.
3. **Cross-tier calls** — Java method → PL/SQL procedure, with param counts.
4. **Screen ↔ storage** (JSP batches) — which screen carries which named setting;
   client-side limits that cap a business value.
5. **Money / retention / notification** — conversion, thresholds, timing, delivery
   semantics (at-least-once vs best-effort).
6. **Defects & dead code** — commented-out logic, swallowed exceptions, hardcoded
   config, typos in property names, concurrency hazards.

Where the code **contradicts** the spec, say so and mark `kind:"defect"`.

## Reading strategy
Small files: read fully. 10k–25k-line files: grep for anchors first, read windows,
and note in the summary that coverage was targeted. `extract-structure.mjs` works for
Java but NOT for `.PSK/.PBK` (no grammar) — use the signatures index / grep there.

Resolve `<bean:message key="label.X"/>` against `ApplicationResources.properties` so
findings quote the real on-screen text.

All textual content in English.
