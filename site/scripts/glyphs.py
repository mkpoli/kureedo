"""Rewrite the glyph-coverage grid in public/index.html from the webfont's cmap.

Run from the repository root with the project venv:
    .venv/bin/python site/scripts/glyphs.py
"""
import re
from pathlib import Path

from fontTools.ttLib import TTFont

SITE = Path(__file__).resolve().parent.parent
FONT = SITE / "public/fonts/KureedoKata-Regular.woff2"
HTML = SITE / "public/index.html"
FIRST = [0x1B127, 0x1B128]

cmap = TTFont(FONT).getBestCmap()
order = FIRST + [cp for cp in sorted(cmap) if cp not in FIRST]


def cell(cp: int) -> str:
    cls = ' class="new"' if cp in FIRST else ""
    ch = chr(cp)
    if cp == 0x20:
        return '<button type="button" data-cp="U+0020" aria-label="U+0020 space"> </button>'
    if 0x300 <= cp < 0x370 or cp in (0x3099, 0x309A):
        ch = "◌" + ch  # dotted circle carries a combining mark
    return f'<button type="button"{cls} data-cp="U+{cp:04X}">{ch}</button>'


cells = "\n".join(cell(cp) for cp in order)
block = f"<!-- glyphs:start -->\n{cells}\n<!-- glyphs:end -->"
src = HTML.read_text(encoding="utf-8")
new, n = re.subn(r"<!-- glyphs:start -->.*?<!-- glyphs:end -->", lambda _: block, src, flags=re.S)
assert n == 1, "glyph markers not found"
HTML.write_text(new, encoding="utf-8")
print(f"{len(order)} code points written")
