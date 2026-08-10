#!/usr/bin/env python3
"""validate — sanity-check a spec markdown fragment before it is pasted or shipped.

Catches the exact classes of error that bit us on the Claims section:
  - unbalanced pipe-table rows (a row missing its trailing `|`)
  - odd number of code fences (an unclosed ```)
  - leftover blockquote `>` prefixes (blockquote leaked into a paste)
  - empty headings (`##` with no text)
  - ⚠️ markers sitting on Requirement/Scenario headings (should be resolved)
  - optional: every `**Locate:**` anchor in a change-request actually exists in a target doc

Usage:
  python validate.py SECTION.md                 # structural checks
  python validate.py CHANGE_REQUEST.md TARGET.md # also verify Find anchors exist
"""
import re, sys


def check_structure(path: str):
    lines = open(path, encoding='utf-8').read().split('\n')
    issues = []
    fences = sum(1 for l in lines if l.startswith('```'))
    if fences % 2:
        issues.append(f'odd code-fence count ({fences}) — an unclosed ```')
    for n, l in enumerate(lines, 1):
        if l.startswith('|') and not l.rstrip().endswith('|'):
            issues.append(f'line {n}: table row missing trailing "|" → {l[:60]}')
        if l.lstrip().startswith('>'):
            issues.append(f'line {n}: leftover blockquote ">" → {l[:60]}')
        if l.strip() in ('#', '##', '###', '####'):
            issues.append(f'line {n}: empty heading')
        if l.startswith(('## Requirement', '### Scenario')) and '⚠️' in l:
            issues.append(f'line {n}: unresolved ⚠️ on a requirement/scenario → {l[:70]}')
    warn = sum(l.count('⚠️') for l in lines)
    ok = sum(l.count('✅') for l in lines)
    reqs = sum(1 for l in lines if l.startswith('## Requirement'))
    scns = sum(1 for l in lines if l.startswith('### Scenario'))
    print(f'{path}: {len(lines)} lines | {reqs} requirements | {scns} scenarios '
          f'| ✅ {ok} | ⚠️ {warn}')
    return issues


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
        sys.exit('usage: validate.py SECTION.md [TARGET.md]')
    issues = check_structure(sys.argv[1])
    if len(sys.argv) == 3:
        issues += check_anchors(sys.argv[1], sys.argv[2])
    if issues:
        print('\nISSUES:')
        for x in issues:
            print('  -', x)
        sys.exit(1)
    print('\nOK — no structural issues')


if __name__ == '__main__':
    main()
