#!/usr/bin/env python3
"""Check a spec .md against the shared term registry (GLOSSARY.md).

Reports:
  1. FORBIDDEN — occurrences of forbidden variants, with the canonical term to use.
  2. INFO — glossary terms that never appear in the spec (not an error; helps spot
     a section defining its own synonym instead of the registry term).
  3. INFO — acronyms used in the spec body that appear in NO given glossary file
     (undefined-acronym smell: a reviewer meets "BIR"/"BMAS" with no expansion).

Usage: python3 term_check.py SPEC.md GLOSSARY.md [CANONICAL_GLOSSARY.md ...]
Exit code 1 if any FORBIDDEN hit is found (INFO never fails the run).
"""
import pathlib, re, sys

# structural/markdown words that look like acronyms but never need a glossary entry
ACRONYM_WHITELIST = {
    "WHEN", "THEN", "AND", "MUST", "NOT", "GIVEN", "IF", "OR", "TODO", "NA",
    "HTML", "PDF", "CSV", "SQL", "URL", "API", "JSON", "PNG", "MD", "OK",
    "FAIL", "INFO", "ID", "IDS", "REQ", "II", "III", "IV",
}


def acronym_check(lines, gloss_texts, spec_path):
    """Acronyms (2-6 caps/digits, at least 2 caps) in prose that no glossary mentions."""
    seen = {}
    in_fence = False
    for n, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        prose = re.sub(r"`[^`]*`", " ", line)  # ignore inline code (file paths, SQL)
        for m in re.finditer(r"\b[A-Z][A-Z0-9]{1,5}\b", prose):
            a = m.group(0)
            if a in ACRONYM_WHITELIST or sum(c.isalpha() for c in a) < 2:
                continue
            seen.setdefault(a, []).append(n)
    blob = "\n".join(gloss_texts)
    unknown = {a: ls for a, ls in seen.items()
               if not re.search(r"(?<![\w-])" + re.escape(a) + r"(?![\w-])", blob)}
    if unknown:
        print(f"\nINFO — acronyms in {spec_path} not found in any given glossary "
              f"(define at first use or add to the glossary):")
        for a, ls in sorted(unknown.items()):
            print(f"  - {a} (x{len(ls)}, first at line {ls[0]})")

def parse_glossary(path):
    rows = []
    for line in pathlib.Path(path).read_text().splitlines():
        if not line.startswith("|") or set(line) <= {"|", " ", ":", "-"}:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0] in ("Term",):
            continue
        term = cells[0]
        variants = [v.strip() for v in cells[3].split(";") if v.strip() and v.strip() != "—"]
        rows.append((term, variants))
    return rows

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    spec_path, gloss_path = sys.argv[1], sys.argv[2]
    extra_glossaries = sys.argv[3:]
    lines = pathlib.Path(spec_path).read_text().splitlines()
    rows = parse_glossary(gloss_path)

    hits = 0
    for term, variants in rows:
        for v in variants:
            pat = re.compile(r"(?<![\w-])" + re.escape(v) + r"(?![\w-])", re.I)
            for n, line in enumerate(lines, 1):
                if pat.search(line):
                    # skip the line that *defines* the variant as forbidden (quotes it)
                    # and lines waived with an inline <!-- term-ok --> marker
                    if "Forbidden" in line or "forbidden" in line or "term-ok" in line:
                        continue
                    hits += 1
                    print(f"FORBIDDEN {spec_path}:{n}: “{v}” → use “{term}”")
                    print(f"    {line.strip()[:120]}")

    text = "\n".join(lines).lower()
    missing = []
    for term, _ in rows:
        # match on the head of the term (before any dash/paren qualifier)
        head = re.split(r"[—(/]", term)[0].strip()
        if head and head.lower() not in text:
            missing.append(term)
    if missing:
        print(f"\nINFO — glossary terms not found in {spec_path} (fine if out of scope):")
        for t in missing:
            print(f"  - {t}")

    gloss_texts = [pathlib.Path(gloss_path).read_text()]
    for p in extra_glossaries:
        gloss_texts.append(pathlib.Path(p).read_text())
    acronym_check(lines, gloss_texts, spec_path)

    print(f"\n{hits} forbidden-variant hit(s)")
    sys.exit(1 if hits else 0)

if __name__ == "__main__":
    main()
