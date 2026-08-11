#!/usr/bin/env python3
"""Check a spec .md against the shared term registry (GLOSSARY.md).

Reports:
  1. FORBIDDEN — occurrences of forbidden variants, with the canonical term to use.
  2. INFO — glossary terms that never appear in the spec (not an error; helps spot
     a section defining its own synonym instead of the registry term).

Usage: python3 term_check.py SPEC.md GLOSSARY.md
Exit code 1 if any FORBIDDEN hit is found.
"""
import pathlib, re, sys

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
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    spec_path, gloss_path = sys.argv[1], sys.argv[2]
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

    print(f"\n{hits} forbidden-variant hit(s)")
    sys.exit(1 if hits else 0)

if __name__ == "__main__":
    main()
