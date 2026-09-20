"""Rewrite the glyph-coverage section in public/index.html from the webfont's cmap: one grid
per Unicode block, in reading order, with the glyphs Kureedo adds to Klee One marked.

Run from the repository root with the project venv:
    .venv/bin/python site/scripts/glyphs.py
"""
import re
from pathlib import Path

from fontTools.ttLib import TTFont

SITE = Path(__file__).resolve().parent.parent
FONT = SITE / "public/fonts/KureedoKata-Regular.woff2"
KLEE = SITE.parent / "sources/klee/KleeOne-Regular.ttf"
HTML = SITE / "public/index.html"

# (title, subtitle, range) in the order shown.
GROUPS = [
    ("新しい文字", "Kana Extended-A · U+1B127–1B128 · Unicode 18.0", range(0x1B127, 0x1B129)),
    ("片仮名", "Katakana · U+30A0–30FF", range(0x30A0, 0x3100)),
    ("小書き片仮名（アイヌ語）", "Katakana Phonetic Extensions · U+31F0–31FF", range(0x31F0, 0x3200)),
    ("濁点・半濁点", "Voicing marks · U+3099–309C · combining and spacing", range(0x3099, 0x309D)),
    ("記号・句読点", "CJK Symbols and Punctuation · U+3000–303F", range(0x3000, 0x3040)),
    ("空白", "Space · U+0020", range(0x20, 0x21)),
]

cmap = TTFont(FONT).getBestCmap()
klee = TTFont(KLEE).getBestCmap()
covered = set()


def cell(cp: int) -> str:
    covered.add(cp)
    added = cp not in klee
    cls = ' class="added"' if added else ""
    title = f"U+{cp:04X}" + ("　Kureedoが追加　added by Kureedo" if added else "")
    ch = chr(cp)
    if cp == 0x20:
        return f'<button type="button" data-cp="U+0020" title="{title}" aria-label="U+0020 space"> </button>'
    if 0x300 <= cp < 0x370 or cp in (0x3099, 0x309A):
        ch = "◌" + ch  # dotted circle carries a combining mark
    return f'<button type="button"{cls} data-cp="U+{cp:04X}" title="{title}">{ch}</button>'


parts = []
for title, sub, rng in GROUPS:
    cps = [cp for cp in rng if cp in cmap]
    if not cps:
        continue
    added = sum(cp not in klee for cp in cps)
    note = f"　·　{added}字はKlee Oneにない" if added else ""
    parts.append(f'<h3 class="glyph-group"><span class="ja">{title}</span><span class="label">{sub} · {len(cps)}字{note}</span></h3>\n<div class="glyphs">\n'
                 + "\n".join(cell(cp) for cp in cps) + "\n</div>")
missing = sorted(set(cmap) - covered)
assert not missing, [f"U+{cp:04X}" for cp in missing]

block = "<!-- glyphs:start -->\n" + "\n".join(parts) + "\n<!-- glyphs:end -->"
src = HTML.read_text(encoding="utf-8")
new, n = re.subn(r"<!-- glyphs:start -->.*?<!-- glyphs:end -->", lambda _: block, src, flags=re.S)
assert n == 1, "glyph markers not found"
HTML.write_text(new, encoding="utf-8")
print(f"{len(covered)} code points in {len(parts)} groups written")
