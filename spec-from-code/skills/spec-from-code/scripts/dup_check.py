#!/usr/bin/env python3
"""dup_check — flag near-verbatim repeated sentences in a spec (the "document
repeats itself instead of cross-referencing" smell a BA review called out:
the same fact pasted 5-7 times across §1/§2/§3/§5/§6 by successive edit passes).

Rule of thumb enforced: a fact is stated fully ONCE in its canonical home;
everywhere else is a cross-reference ("see §3 Key Terms").

Usage:
  python3 dup_check.py SPEC.md [--min-words 8] [--fail-at 3]

Exit 1 when any normalized sentence of >= min-words appears >= fail-at times.
Sentences appearing exactly twice are listed as INFO (often legitimate:
summary row + requirement).
"""
import re, sys
from collections import Counter


def normalize(s: str) -> str:
    s = re.sub(r'`[^`]*`', ' ', s)              # inline code
    s = re.sub(r'\*\*|\*|__', '', s)            # emphasis
    s = re.sub(r'[✅⚠️❓→—–]', ' ', s)
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)  # links
    s = re.sub(r'[^0-9a-zA-ZÀ-ỹ ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip().lower()


def sentences(path: str):
    """Yield (normalized_sentence, line_no) for prose lines (fences, tables,
    headings and evidence/source lines excluded)."""
    in_fence = False
    for n, raw in enumerate(open(path, encoding='utf-8'), 1):
        line = raw.rstrip('\n')
        if line.lstrip().startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if (not stripped or stripped.startswith('#') or stripped.startswith('|')
                or stripped.startswith('<!--')):
            continue
        # evidence/source lines legitimately repeat file paths — skip them
        if re.match(r'\*{0,2}(Evidence|Source|Sources|Locate|Read this as)\b', stripped):
            continue
        for part in re.split(r'(?<=[.!?;])\s+', stripped):
            norm = normalize(part)
            if norm:
                yield norm, n


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 1:
        sys.exit('usage: dup_check.py SPEC.md [--min-words 8] [--fail-at 3]')
    opts = dict(a.lstrip('-').split('=') if '=' in a else (a.lstrip('-'), None)
                for a in sys.argv[1:] if a.startswith('--'))
    flags = sys.argv[1:]
    def flag(name, default):
        if f'--{name}' in flags:
            i = flags.index(f'--{name}')
            return int(flags[i + 1])
        return default
    min_words = flag('min-words', 8)
    fail_at = flag('fail-at', 3)

    occ = {}
    for norm, line_no in sentences(args[0]):
        if len(norm.split()) >= min_words:
            occ.setdefault(norm, []).append(line_no)

    fails = {s: ls for s, ls in occ.items() if len(ls) >= fail_at}
    infos = {s: ls for s, ls in occ.items() if len(ls) == 2}

    print(f'{args[0]}: {sum(len(v) for v in occ.values())} prose sentences '
          f'(>= {min_words} words) | repeated x2: {len(infos)} | repeated >= {fail_at}: {len(fails)}')
    if infos:
        print('\nINFO — stated twice (check one of them should be a cross-ref):')
        for s, ls in sorted(infos.items(), key=lambda kv: kv[1])[:10]:
            print(f'  lines {ls}: {s[:90]}')
        if len(infos) > 10:
            print(f'  ... and {len(infos) - 10} more')
    if fails:
        print(f'\nFAIL — stated {fail_at}+ times (collapse to one canonical home + cross-refs):')
        for s, ls in sorted(fails.items(), key=lambda kv: kv[1]):
            print(f'  lines {ls}: {s[:90]}')
        sys.exit(1)
    print('\nOK — no sentence repeated', fail_at, 'or more times')


if __name__ == '__main__':
    main()
