#!/usr/bin/env python3
"""md2html — convert a Markdown spec fragment to paste-ready HTML for Google Docs.

Google Docs turns pasted HTML into real headings and real tables. Pasting raw
Markdown instead leaves literal `|` and `**`. This converter exists so a section
can be dropped into Docs in ONE paste without formatting breaking.

Usage:  python md2html.py INPUT.md OUTPUT.html

Handles: ATX headings, pipe tables, fenced code, bullet lists, blockquotes,
inline `code` / **bold** / *italic*. Deliberately small — no external deps.
"""
import re, html, sys


def inline(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', t)
    return t


def convert(md: str) -> str:
    lines = md.split('\n')
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('```'):
            i += 1; buf = []
            while i < len(lines) and not lines[i].startswith('```'):
                buf.append(html.escape(lines[i])); i += 1
            i += 1
            out.append('<pre style="font-family:Consolas,monospace;font-size:9pt;'
                       'background:#f5f5f5;padding:8px;white-space:pre-wrap">'
                       + '\n'.join(buf) + '</pre>')
            continue
        if l.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s:\-|]+\|$', lines[i + 1].strip()):
            hdr = [c.strip() for c in l.strip().strip('|').split('|')]
            i += 2; rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            t = ['<table style="border-collapse:collapse;width:100%">']
            t.append('<tr>' + ''.join(
                f'<td style="border:1px solid #999;padding:5px;background:#efefef">'
                f'<strong>{inline(c)}</strong></td>' for c in hdr) + '</tr>')
            for r in rows:
                r += [''] * (len(hdr) - len(r))
                t.append('<tr>' + ''.join(
                    f'<td style="border:1px solid #999;padding:5px;vertical-align:top">'
                    f'{inline(c)}</td>' for c in r[:len(hdr)]) + '</tr>')
            t.append('</table>')
            out.append('\n'.join(t)); continue
        m = re.match(r'^(#{1,6})\s+(.*)$', l)
        if m:
            lvl = len(m.group(1))
            txt = re.sub(r'\s*\{#.*?\}\s*$', '', m.group(2)).replace('\\.', '.')
            out.append(f'<h{lvl}>{inline(txt)}</h{lvl}>'); i += 1; continue
        if re.match(r'^---+$', l.strip()):
            out.append('<hr>'); i += 1; continue
        if re.match(r'^\s*[-*]\s+', l):
            items = []
            while i < len(lines) and re.match(r'^\s*[-*]\s+', lines[i]):
                items.append('<li>' + inline(re.sub(r'^\s*[-*]\s+', '', lines[i])) + '</li>'); i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
            out.append('<ul>' + ''.join(items) + '</ul>'); continue
        if l.startswith('>'):
            buf = []
            while i < len(lines) and lines[i].startswith('>'):
                buf.append(re.sub(r'^>\s?', '', lines[i])); i += 1
            out.append('<blockquote style="border-left:3px solid #ccc;margin-left:0;'
                       'padding-left:12px">' + inline(' '.join(x for x in buf if x.strip()))
                       + '</blockquote>'); continue
        if l.strip():
            out.append('<p>' + inline(l) + '</p>')
        i += 1
    return '\n'.join(out)


def main():
    if len(sys.argv) != 3:
        sys.exit('usage: md2html.py INPUT.md OUTPUT.html')
    src, dst = sys.argv[1], sys.argv[2]
    body = convert(open(src, encoding='utf-8').read())
    open(dst, 'w', encoding='utf-8').write(
        '<!doctype html><meta charset="utf-8">'
        '<body style="font-family:Arial,sans-serif;font-size:11pt;line-height:1.45;'
        'max-width:1100px;margin:24px auto">' + body + '</body>')
    # self-check the caller can eyeball
    h = open(dst, encoding='utf-8').read()
    print(f'wrote {dst}: {h.count("<table")} tables, {h.count("<h2>")+h.count("<h3>")} headings, '
          f'{h.count("|")} stray pipes, {h.count("**")} stray markdown')


if __name__ == '__main__':
    main()
