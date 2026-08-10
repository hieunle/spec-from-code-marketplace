# <FEATURE> — Code-Verified Requirements

**Status:** Draft v1 · **Scope:** <feature / system identifier>
**Purpose:** a behaviour-complete spec of the existing feature, every claim traceable
to file:line, so a replacement can be built and validated without reading the source.

> **Shape check first.** This template assumes ONE capability (§7 gathers all
> requirements as the last section). If the feature is a cluster of sub-capabilities
> (module + engine + reporting…), don't append §8, §9… — either split into separate
> specs or nest them as `8.1`, `8.2` under one umbrella and rename §7. See the skill's
> "compound feature" note. Decide with the section owner before writing.

## 1. Sources
| # | Source | Provides | Confidence |
|---|---|---|---|
| S1 | <spec PDF, rev/date> | intent, documented position | vendor |
| S2 | <PL/SQL packages> | implemented behaviour | high — source |
| S3 | <DDL export> | real column definitions | high |
| S4 | <Java service/DAO/validator> | rules, storage, call map | high |
| S5 | <JSP screens> | screen↔field mapping, client limits | high |

**Coverage gaps (G-n):** <what was NOT read; each is a risk to completeness>

## 2. Business context
<what the feature is FOR — the outcome, not the mechanism. State the one distinction a
newcomer must internalise.>

## 3. Glossary
| Term | Meaning |
|---|---|

## 4. Data model
<tables with real columns from DDL; identity/keying rules (BR-ID-n); state model if any>

## 5. Functional requirements
### FR-1 — <group>
| ID | Requirement (MUST) | Source |
|---|---|---|
| FR-1.1 | The system MUST … | S2 §… |

## 6. Non-functional (NFR-n), 7. Data migration (DM-n), 8. Acceptance criteria (AC-n)
<verifiable criteria — e.g. "replay N historical records, reproduce recorded output exactly">

## 9. Divergences — spec vs implementation (the highest-value section)
| ID | Finding | Evidence | Impact |
|---|---|---|---|
| BUG-1 | … | file:line | … |

## 10. Modernization risks (R-n) · 11. Open questions (Q-n)
| # | Question | Who answers | Blocking |
|---|---|---|---|

## Appendix — requirement index (counts per prefix)
