#!/usr/bin/env python3
"""Check the built fonts: names, coverage, feature switches, mark composition, vertical metrics."""
import sys
from io import BytesIO
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import SMALL  # noqa: E402

SMALL_VERT_TOP, SMALL_VERT_X = SMALL["vertTop"], SMALL["vertX"]

ROOT = Path(__file__).resolve().parent.parent
KLEE = TTFont(ROOT / "sources/klee/KleeOne-Regular.ttf")


def shaper(font: TTFont):
    font.flavor = None
    buffer = BytesIO()
    font.save(buffer)
    hb_font = hb.Font(hb.Face(buffer.getvalue()))
    hb_font.scale = (1000, 1000)
    order = font.getGlyphOrder()

    def shape(text, direction="ltr", features=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        buf.direction = direction
        hb.shape(hb_font, buf, features or {})
        return [(order[i.codepoint], p.x_advance, p.y_advance) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]
    return shape


def check(path: Path, family: str, full: bool):
    font = TTFont(path)
    cmap = font.getBestCmap()
    shape = shaper(font)
    name = font["name"]
    assert name.getDebugName(1) == family, name.getDebugName(1)
    assert name.getDebugName(6) == family.replace(" ", "") + "-Regular"
    assert name.getDebugName(5) == "Version 0.400" and abs(font["head"].fontRevision - 0.4) < 1e-4
    assert "Klee Project Authors" in name.getDebugName(0) and name.getDebugName(13).startswith("This Font Software")
    assert all(c in cmap for c in [*range(0x30A1, 0x30FB), *range(0x31F0, 0x3200), 0x3099, 0x309A, 0x309B, 0x309C, 0x30F0, 0x30F1, 0x30F2, 0x30F4, 0x1B127, 0x1B128, 0x2A708])
    if not full:
        assert 0x5B50 not in cmap and 0x4E95 not in cmap

    # Default glyphs are Klee's; the historical forms sit behind the features.
    ne, wi = cmap[0x30CD], cmap[0x30F0]
    hist_ne, hist_wi = cmap[0x1B127], cmap[0x1B128]
    assert (hist_ne, hist_wi) == ("uni1B127", "uni1B128")
    # The Kana Extended-A letters and the historical alternates are the same glyph.
    assert shape("\U0001B127\U0001B128") == [(hist_ne, 1000, 0), (hist_wi, 1000, 0)]
    assert shape("\U0001B127", "ttb")[0][2] == -1000
    assert font["glyf"][ne].compile(font["glyf"]) == KLEE["glyf"][ne].compile(KLEE["glyf"])
    assert font["glyf"][wi].compile(font["glyf"]) == KLEE["glyf"][wi].compile(KLEE["glyf"])
    assert shape("ネヰ") == [(ne, 1000, 0), (wi, 1000, 0)]
    for features in ({"hist": True}, {"ss01": True}, {"cv01": True, "cv02": True}):
        assert [g for g, *_ in shape("ネヰ", features=features)] == [hist_ne, hist_wi], features
        assert [g for g, *_ in shape("ネヰ", "ttb", features=features)] == [hist_ne, hist_wi], features
        assert [g for g, *_ in shape("ネヰ", "ttb", features={**features, "vkna": True})] == [hist_ne, hist_wi]
    assert [g for g, *_ in shape("ネヰ", features={"cv01": True})] == [hist_ne, wi]
    assert [g for g, *_ in shape("ネヰ", features={"cv02": True})] == [ne, hist_wi]
    for glyph in (hist_ne, hist_wi):
        assert font["hmtx"][glyph][0] == 1000
        assert font["glyf"][glyph].yMax + font["vmtx"][glyph][1] == 880, glyph
        assert font["glyf"][glyph].xMin >= 0 and font["glyf"][glyph].xMax <= 1000

    # The tomo ligature has its own code point; `hlig` forms it from トモ and nothing else does.
    tomo = cmap[0x2A708]
    assert tomo == "uni2A708" and font["hmtx"][tomo][0] == 1000
    assert font["glyf"][tomo].yMax + font["vmtx"][tomo][1] == 880
    assert shape("\U0002A708") == [(tomo, 1000, 0)] and shape("\U0002A708", "ttb")[0][2] == -1000
    assert [g for g, *_ in shape("トモ")] == [cmap[0x30C8], cmap[0x30E2]]
    assert [g for g, *_ in shape("トモ", features={"hist": True})] == [cmap[0x30C8], cmap[0x30E2]]
    for direction in ("ltr", "ttb"):
        assert [g for g, *_ in shape("レトモ", direction, features={"hlig": True})] == [cmap[0x30EC], tomo], direction

    # Marked kana shape into one cell in both directions; precomposed and decomposed agree.
    for text in ["ツ゚", "ト゚", "セ゚", "ㇷ゚", "カ゚", "キ゚", "ク゚", "ケ゚", "コ゚", "パ", "ガ", "ヅ"]:
        for direction in ("ltr", "ttb"):
            glyphs = shape(text, direction)
            assert len(glyphs) == 1 and glyphs[0][0] != ".notdef", (text, direction, glyphs)
            assert glyphs[0][1:] == ((1000, 0) if direction == "ltr" else (0, -1000)), (text, direction, glyphs)
    for plain, decomposed in [("\u30D1", "\u30CF\u309A"), ("\u30AC", "\u30AB\u3099"), ("\u30C5", "\u30C4\u3099")]:
        assert shape(plain) == shape(decomposed) and shape(plain, "ttb") == shape(decomposed, "ttb")
    assert shape("ㇷ", "ttb")[0] != shape("ㇷ゚", "ttb")[0]
    # Small kana take a vertical variant that sits higher and to the right than the horizontal
    # glyph; the composite with a mark shares that variant's vertical origin.
    small, small_vert = cmap[0x31F7], shape("ㇷ", "ttb")[0][0]
    assert small_vert != small and font["vmtx"][small_vert][1] == SMALL_VERT_TOP
    assert font["glyf"][small_vert].xMin - font["glyf"][small].xMin == SMALL_VERT_X
    assert font["glyf"][shape("ㇷ゚", "ttb")[0][0]].yMax + font["vmtx"][shape("ㇷ゚", "ttb")[0][0]][1] == font["glyf"][small_vert].yMax + font["vmtx"][small_vert][1]
    # An unsupported base + mark sequence still takes one cell vertically: the mark has no vertical advance.
    for mark in (cmap[0x3099], cmap[0x309A]):
        assert font["vmtx"][mark][0] == 0 and font["hmtx"][mark][0] == 0
        assert font["GDEF"].table.GlyphClassDef.classDefs[mark] == 3
    assert [y for _, _, y in shape("ネ゙", "ttb")] == [-1000, 0]

    tags = [r.FeatureTag for r in font["GSUB"].table.FeatureList.FeatureRecord]
    assert tags == sorted(tags), tags
    for r in font["GSUB"].table.FeatureList.FeatureRecord:
        if r.FeatureTag == "aalt":
            for i in r.Feature.LookupListIndex:
                for st in font["GSUB"].table.LookupList.Lookup[i].SubTable:
                    if st.LookupType == 3:
                        assert hist_ne in st.alternates[ne] and hist_wi in st.alternates[wi]
    ja = {n.nameID: str(n) for n in name.names if n.langID == 0x411}
    assert ja[1] in ("クレード", "クレード カタ") and ja[4].endswith(" Regular"), ja

    # Feature UI names are present for the character variants and the stylistic set.
    labels = {name.getDebugName(i) for i in range(256, 300) if name.getDebugName(i)}
    assert {"Katakana ne, 子-shaped", "Katakana wi, 井-shaped", "Edo-period printed forms"} <= labels, labels

    if full:
        # Every glyph Klee One ships is still there and unchanged.
        klee_order = KLEE.getGlyphOrder()
        assert font.getGlyphOrder()[:len(klee_order)] == klee_order
        changed = [g for g in klee_order if font["glyf"][g].compile(font["glyf"]) != KLEE["glyf"][g].compile(KLEE["glyf"])]
        assert not changed, changed[:10]
        assert 0x3042 in cmap and 0x6F22 in cmap
        assert shape("漢字かな", features={"vert": True})[0][0] == cmap[0x6F22]
    return font


check(ROOT / "fonts/Kureedo-Regular.ttf", "Kureedo", full=True)
kata = check(ROOT / "fonts/KureedoKata-Regular.ttf", "Kureedo Kata", full=False)
woff = check(ROOT / "fonts/KureedoKata-Regular.woff2", "Kureedo Kata", full=False)
assert kata.getGlyphOrder() == woff.getGlyphOrder()
assert 0x3042 not in woff.getBestCmap()
print("Checks passed: names, coverage, hist/ss01/cv01/cv02 and hlig in both directions, marks, small kana, Klee glyphs intact.")
