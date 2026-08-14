# <FEATURE> — Evidence & Internal Notes

**Companion to** `<feature>-spec.md` · **Not for the customer.**

This file carries everything the spec deliberately keeps out of the customer's reading
flow: `file:line` traceability, coverage gaps, the ID scheme, and decisions still open.
It is what makes a claim auditable — the spec states the rule, this file proves it.

## 1. Evidence per requirement

One row per requirement and per scenario that needed its own proof. `Verdict` is the
source-hierarchy label: **confirmed** (code/DDL, cited) · **divergence vs S1** (both
cited) · **S1-stated, no code located** (never earns a ✅ in the spec).

| REQ ID | Claim | Evidence (`file:line`) | Verdict | Marker in spec |
|---|---|---|---|---|
| REQ-<AREA>-001 | <the MUST, abbreviated> | `path/File.java:120-155` — <what the code does> | confirmed | ✅ |

## 2. ID scheme

**`<AREA>` = `<XXX>`** (<expansion — e.g. CLM = Claims>). Numbers are sequential in
document order, three digits, continuing across `5.x` groups rather than restarting per
group. Record any ID retired or re-pointed here so re-runs converge on the same numbering.

## 3. Coverage gaps (G-n)

<What was NOT read, and why it matters. Each gap is a completeness risk the spec's
confidence markers do not express.>

| # | Not covered | Risk if wrong |
|---|---|---|
| G-1 | <tier / package / screen set> | <what could be missing or wrong> |

## 4. Divergences — detail

<The `file:line` backing for every §7 Possible Known Issue, plus the vendor-document
position it contradicts. §7 names the issue; this section proves it.>

| ISSUE ID | Code says | Evidence | Vendor doc says | Citation |
|---|---|---|---|---|

## 5. Open decisions for the owner

<Anything the source did not settle: content with no obvious home, ambiguous
context-vs-§5 placement, a section whose fate needs a PO/BA call. Each is a concrete
choice, not an open musing — and none is resolved by guessing.>

| # | The decision | Options | Owner | Status |
|---|---|---|---|---|

## 6. Change log

<What moved where, what was de-duplicated and which home survived — so a later reviewer
can tell an intended removal from an accidental drop.>
