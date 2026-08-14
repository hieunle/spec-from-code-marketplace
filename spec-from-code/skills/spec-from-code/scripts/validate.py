#!/usr/bin/env python3
"""validate — sanity-check a spec markdown file before it is pasted or shipped.

Two layers of checks:

STRUCTURAL (every file) — the classes of error that bit us on the Claims section:
  - unbalanced pipe-table rows (a row missing its trailing `|`)
  - odd number of code fences (an unclosed ```)
  - leftover blockquote `>` prefixes (blockquote leaked into a paste)
  - empty headings (`##` with no text)
  - figure captions with no diagram nearby (invisible to Word/Docs readers)
  - WARN: normative content inside a lookup appendix (allocation rule) — skipped for
    appendices that declare themselves a normative export

CANONICAL CONFORMANCE (only when the file is a full spec — detected by a `## 5.`
Requirements section) — the §1–8 structure every capability spec must end up with:
  - exactly one H1; no pandoc `{#…}` export anchors
  - every Requirement heading carries a ✅/⚠️/❓ marker AND a REQ-<AREA>-### ID
  - every Scenario heading carries a ✅/⚠️/❓ marker
  - WARN: a ⚠️/❓ heading with no Confidence note beneath it
  - §5 requirements are grouped under `### 5.x`
  - no "Known defects/issues" heading left inside §5 (those belong in §7)
  - appendices live under `## 8. Supporting materials`
  - no non-canonical top-level section survives (Actors, At a Glance, …)

Note on markers: ⚠️ on a requirement means *confirmed behaviour with a caveat* and is
legitimate — it must carry a Confidence note saying exactly what the caveat is. Genuinely
unsettled business intent is ❓ with a linked §6 question. Behaviour only the vendor doc
claims never becomes a requirement at all.

Usage:
  python validate.py SPEC.md                     # structural + canonical checks
  python validate.py CHANGE_REQUEST.md TARGET.md # also verify Locate: anchors exist
"""
import re, sys

MARKER = '✅⚠❓'
RE_REQ = re.compile(r'^#{2,6}\s+Requirement\b')
RE_SCN = re.compile(r'^#{2,6}\s+Scenario\b')
RE_REQ_ID = re.compile(r'REQ-[A-Z0-9]+-\d+')


def has_marker(line: str) -> bool:
    return any(m in line for m in MARKER)


def fence_mask(lines):
    """True for every line inside a ``` fence (and for the fence lines themselves).

    Headings, anchors and tables inside a fence are illustrative examples, not the
    document's own structure — checking them reports the sample as if it were the spec.
    """
    mask, inside = [], False
    for l in lines:
        if l.startswith('```'):
            inside = not inside
            mask.append(True)
        else:
            mask.append(inside)
    return mask


def section_bounds(lines, number: str, fenced=None):
    """Line indices [start, end) of `## <number>. …` up to the next `## ` heading."""
    fenced = fenced or [False] * len(lines)
    start = next((i for i, l in enumerate(lines)
                  if not fenced[i] and re.match(rf'^##\s+{number}\\?\.\s', l)), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines))
                if not fenced[i] and re.match(r'^##\s', lines[i])), len(lines))
    return start, end


def check_structure(path: str):
    lines = open(path, encoding='utf-8').read().split('\n')
    issues, warnings = [], []

    fences = sum(1 for l in lines if l.startswith('```'))
    if fences % 2:
        issues.append(f'odd code-fence count ({fences}) — an unclosed ```')
    fenced = fence_mask(lines)

    for n, l in enumerate(lines, 1):
        if fenced[n - 1]:
            continue
        if l.startswith('|') and not l.rstrip().endswith('|'):
            issues.append(f'line {n}: table row missing trailing "|" → {l[:60]}')
        if l.lstrip().startswith('>'):
            issues.append(f'line {n}: leftover blockquote ">" → {l[:60]}')
        if l.strip() in ('#', '##', '###', '####', '#####'):
            issues.append(f'line {n}: empty heading')
        # a figure caption with no actual diagram nearby = invisible to Word/Docs readers
        if re.match(r'\*{0,2}(Diagram|Figure|Hình)\b[\s\d:—–-]', l.strip()):
            window = lines[max(0, n - 6):min(len(lines), n + 5)]
            if not any(w.lstrip().startswith('```') or w.lstrip().startswith('![')
                       or '<img' in w for w in window):
                issues.append(f'line {n}: diagram/figure caption with no mermaid fence or '
                              f'image within 5 lines → {l[:60]}')

    # allocation rule: lookup appendices hold no normative content. An appendix that
    # declares itself a normative export (a config export whose values join the
    # requirements baseline) is exempt.
    appendix_at = next((i for i, l in enumerate(lines)
                        if not fenced[i] and re.match(r'#{1,4}\s.*\b(Appendix|Phụ lục)\b', l)), None)
    if appendix_at is not None:
        tail = '\n'.join(lines[appendix_at:])
        declares_normative = re.search(r'\*?Normative export', tail, re.I)
        if not declares_normative:
            for n, l in enumerate(lines[appendix_at:], appendix_at + 1):
                if fenced[n - 1]:
                    continue
                if RE_REQ.match(l) or RE_SCN.match(l) or re.search(r'\bMUST\b', l):
                    warnings.append(f'line {n}: normative content in a lookup appendix — '
                                    f'pull it in-place → {l.strip()[:60]}')

    reqs = [(n, l) for n, l in enumerate(lines, 1) if not fenced[n - 1] and RE_REQ.match(l)]
    scns = [(n, l) for n, l in enumerate(lines, 1) if not fenced[n - 1] and RE_SCN.match(l)]

    # ---- canonical conformance (full specs only) ----
    canonical = section_bounds(lines, '5', fenced) is not None and bool(reqs)
    if canonical:
        h1 = [n for n, l in enumerate(lines, 1) if not fenced[n - 1] and re.match(r'^#\s', l)]
        if len(h1) != 1:
            issues.append(f'expected exactly one H1 title, found {len(h1)} '
                          f'(lines {h1 or "—"})')
        for n, l in enumerate(lines, 1):
            if not fenced[n - 1] and '{#' in l:
                issues.append(f'line {n}: pandoc export anchor left in → {l.strip()[:60]}')

        for n, l in reqs:
            if not has_marker(l):
                issues.append(f'line {n}: requirement heading without a ✅/⚠️/❓ marker '
                              f'→ {l.strip()[:70]}')
            if not RE_REQ_ID.search(l):
                issues.append(f'line {n}: requirement heading without a REQ-<AREA>-### id '
                              f'→ {l.strip()[:70]}')
        for n, l in scns:
            if not has_marker(l):
                issues.append(f'line {n}: scenario heading without a ✅/⚠️/❓ marker '
                              f'→ {l.strip()[:70]}')

        # ⚠️/❓ must say what the caveat is
        for n, l in reqs:
            if ('⚠' in l or '❓' in l) and not any(
                    re.match(r'\**Confidence note', lines[i].lstrip())
                    for i in range(n, min(n + 8, len(lines)))):
                warnings.append(f'line {n}: ⚠️/❓ requirement with no "Confidence note:" '
                                f'beneath it — say exactly what is unsettled '
                                f'→ {l.strip()[:60]}')

        s5 = section_bounds(lines, '5', fenced)
        if s5:
            start, end = s5
            body = lines[start:end]
            if not any(re.match(r'^###\s+5\\?\.\d', l)
                       for i, l in enumerate(body, start) if not fenced[i]):
                issues.append('§5 requirements are not grouped under `### 5.x <sub-area>` '
                              '— grouping is required even when the source is a flat list')
            for i, l in enumerate(body, start + 1):
                if fenced[i - 1]:
                    continue
                if re.match(r'^#{2,6}\s.*\bKnown (defects|issues)\b', l, re.I):
                    issues.append(f'line {i}: "known defects/issues" heading inside §5 — '
                                  f'these belong in §7 Possible Known Issues')

        if appendix_at is not None and section_bounds(lines, '8', fenced) is None:
            issues.append('appendices present but no `## 8. Supporting materials` section '
                          '— appendices must be wrapped under §8 and relettered A, B, C…')

        for n, l in enumerate(lines, 1):
            if not fenced[n - 1] and re.match(r'^##\s', l):
                if re.search(r'\b(Actors|At a Glance)\b', l, re.I):
                    issues.append(f'line {n}: non-canonical section survived — dissolve it '
                                  f'into an existing §5 requirement or a context section '
                                  f'→ {l.strip()[:60]}')
                elif not re.match(r'^##\s+\d+\\?\.\s', l):
                    warnings.append(f'line {n}: top-level section outside the canonical '
                                    f'1–8 numbering → {l.strip()[:60]}')

    ok = sum(l.count('✅') for l in lines)
    warn = sum(l.count('⚠') for l in lines)
    q = sum(l.count('❓') for l in lines)
    print(f'{path}: {len(lines)} lines | {len(reqs)} requirements | {len(scns)} scenarios '
          f'| ✅ {ok} | ⚠️ {warn} | ❓ {q} | '
          f'{"canonical §1–8 checks applied" if canonical else "fragment — structural checks only"}')
    return issues, warnings


def check_anchors(cr_path: str, target_path: str):
    cr = open(cr_path, encoding='utf-8').read()
    tgt = open(target_path, encoding='utf-8').read()
    anchors = re.findall(r'\*\*Locate:\*\*\s*`([^`]+)`', cr)
    anchors += re.findall(r'\*\*TÌM:\*\*\s*`([^`]+)`', cr)  # Vietnamese "TÌM:"
    missing = []
    for a in anchors:
        norm = a.replace('\\', '')
        if norm not in tgt and norm.replace('"', '“') not in tgt and norm.replace('"', '”') not in tgt:
            missing.append(a)
    print(f'anchors: {len(anchors)} checked, {len(anchors) - len(missing)} found, {len(missing)} MISSING')
    return [f'anchor not found in target: {a[:70]}' for a in missing]


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit('usage: validate.py SPEC.md [TARGET.md]')
    issues, warnings = check_structure(sys.argv[1])
    if len(sys.argv) == 3:
        issues += check_anchors(sys.argv[1], sys.argv[2])
    if warnings:
        print('\nWARNINGS (non-fatal):')
        for x in warnings:
            print('  -', x)
    if issues:
        print('\nISSUES:')
        for x in issues:
            print('  -', x)
        sys.exit(1)
    print('\nOK — no structural issues')


if __name__ == '__main__':
    main()
