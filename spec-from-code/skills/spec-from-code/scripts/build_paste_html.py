#!/usr/bin/env python3
"""Build paste-ready Google-Docs HTML from a spec .md that contains mermaid fences.

- Renders each ```mermaid fence to PNG via mermaid-cli (npx -y @mermaid-js/mermaid-cli)
  and embeds it as a base64 <img> so the paste carries the figures.
- Optionally splits the document at a heading (e.g. the appendix block) into two
  HTML files, so the section body and the appendices paste at different spots.

Usage:
  python3 build_paste_html.py SPEC.md OUT_PREFIX [--split-at "HEADING TEXT"] [--workdir DIR]

Produces OUT_PREFIX_SECTION_PASTE.html (and OUT_PREFIX_APPENDICES_PASTE.html when
--split-at matched). Requires node/npx; md2html.py must sit next to this script.

Paste flow: open the HTML in Chrome -> Cmd+A, Cmd+C -> paste into Google Docs.
Paste into a BLANK doc first if the target cursor may carry a heading style
(see SKILL.md, "Paste-target style trap").
"""
import argparse, base64, pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).parent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("out_prefix")
    ap.add_argument("--split-at", default=None,
                    help="heading text; content from its line onward goes to the APPENDICES file")
    ap.add_argument("--workdir", default=None, help="dir for .mmd/.png intermediates")
    a = ap.parse_args()

    src = pathlib.Path(a.spec)
    text = src.read_text()
    work = pathlib.Path(a.workdir) if a.workdir else pathlib.Path(tempfile.mkdtemp(prefix="paste-html-"))
    work.mkdir(parents=True, exist_ok=True)

    blocks = []
    def grab(m):
        blocks.append(m.group(1))
        return f"@@DIAGRAM{len(blocks)}@@"
    text = re.sub(r"```mermaid\n(.*?)\n```", grab, text, flags=re.S)
    print(f"{len(blocks)} mermaid blocks")

    imgs = []
    for i, b in enumerate(blocks, 1):
        mmd, png = work / f"fig{i}.mmd", work / f"fig{i}.png"
        mmd.write_text(b)
        r = subprocess.run(["npx", "-y", "@mermaid-js/mermaid-cli", "-i", str(mmd),
                            "-o", str(png), "-b", "white", "-s", "2"],
                           capture_output=True, text=True)
        if not png.exists():
            sys.exit(f"fig{i} render FAILED:\n{r.stdout}\n{r.stderr}")
        imgs.append(base64.b64encode(png.read_bytes()).decode())
        print(f"fig{i}.png ok ({png.stat().st_size // 1024} KB)")

    parts = {"SECTION": text}
    if a.split_at and a.split_at in text:
        idx = text.index(a.split_at)
        # back up to the start of the heading line
        idx = text.rfind("\n", 0, idx) + 1
        parts = {"SECTION": text[:idx], "APPENDICES": text[idx:]}
    elif a.split_at:
        print(f"WARNING: --split-at text not found; producing one file", file=sys.stderr)

    for name, md in parts.items():
        md_path = work / f"{name.lower()}.md"
        html_path = pathlib.Path(f"{a.out_prefix}_{name}_PASTE.html")
        md_path.write_text(md)
        subprocess.run([sys.executable, str(HERE / "md2html.py"), str(md_path), str(html_path)], check=True)
        html = html_path.read_text()
        for i, b64 in enumerate(imgs, 1):
            img = (f'<img src="data:image/png;base64,{b64}" '
                   f'style="max-width:620px;width:100%" alt="Figure {i}">')
            html = re.sub(rf"<p>@@DIAGRAM{i}@@</p>|@@DIAGRAM{i}@@", img, html)
        html_path.write_text(html)
        left = re.findall(r"@@DIAGRAM\d+@@", html)
        print(f"{html_path}: {len(html)//1024} KB, leftover placeholders: {left}")
        if left:
            sys.exit("ERROR: unreplaced diagram placeholders — check fence syntax")

if __name__ == "__main__":
    main()
