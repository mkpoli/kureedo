"""Check edition boundaries, donor fidelity and preservation of Japanese shaping."""
from pathlib import Path
from statistics import median

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.O_S_2f_2 import calcCodePageRanges, intersectUnicodeRanges

from build import JAPANESE, KANA_UNICODES, stroke_thickness
from wenkai import (MIN_EROSION, erode_glyph, fetch_wenkai, is_ideograph,
                    normalizable_names, normalization_radius, private_use,
                    target_thickness, thickness_area, weight_model)

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"


def shape(font, text, direction, features=None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    buf.direction = direction
    hb.shape(font, buf, features or {})
    return [(g.codepoint, p.x_advance, p.y_advance, p.x_offset, p.y_offset)
            for g, p in zip(buf.glyph_infos, buf.glyph_positions)]


def check():
    families = ["Kureedo Full", "Kureedo Kana", "Kureedo Additions"]
    fonts = {}
    for family in families:
        stem = family.replace(" ", "") + "-Regular"
        font = fonts[family] = TTFont(FONTS / (stem + ".ttf"))
        web = TTFont(FONTS / (stem + ".woff2"))
        assert font.getBestCmap() == web.getBestCmap(), family
        assert font.getGlyphOrder() == web.getGlyphOrder(), family
        for edition in (font, web):
            assert edition["name"].getDebugName(1) == family
            assert edition["name"].getDebugName(6) == stem
            assert str(edition["name"].getName(1, 3, 1, 0x411)) == JAPANESE[family]
    base = TTFont(ROOT / "build/japanese-base.ttf")
    full = fonts["Kureedo Full"]
    donor = fetch_wenkai()
    klee = TTFont(ROOT / "sources/klee/KleeOne-Regular.ttf")
    before, after = base.getBestCmap(), full.getBestCmap()
    expected = set(before) | {cp for cp in donor.getBestCmap() if not private_use(cp)}
    assert set(after) == expected and len(after) == 46923
    assert len(before) == 10204
    assert len(full.getGlyphOrder()) == 52231 < 65536
    assert all(after[cp] == name for cp, name in before.items())
    assert full.getGlyphOrder()[:len(base.getGlyphOrder())] == base.getGlyphOrder()
    for name in base.getGlyphOrder():
        assert base["glyf"][name].compile(base["glyf"]) == full["glyf"][name].compile(full["glyf"]), name
        for tag in ("hmtx", "vmtx"):
            assert base[tag][name] == full[tag][name], (tag, name)
    model = weight_model(base)
    donor_set, base_set = donor.getGlyphSet(), base.getGlyphSet()
    full_set = full.getGlyphSet()
    imported = sorted(set(after) - set(before))
    ideographs = [cp for cp in imported if is_ideograph(cp)]
    subset_cps = {cp for cp in donor.getBestCmap() if cp not in before and not private_use(cp)}
    eligible = normalizable_names(donor, subset_cps)
    normalized = [cp for cp in ideographs if donor.getBestCmap()[cp] in eligible]
    for cp in imported:
        target, source = after[cp], donor.getBestCmap()[cp]
        assert full["hmtx"][target][0] == donor["hmtx"][source][0], (cp, "hmtx advance")
        assert full["vmtx"][target][0] == donor["vmtx"][source][0], (cp, "vmtx advance")
        if source in eligible:
            continue
        # A radical can reuse an ideograph as a component; that component's new
        # weight carries through. Its composite transform is unchanged.
        if full["glyf"][target].isComposite() or donor["glyf"][source].isComposite():
            assert full["glyf"][target].isComposite() and donor["glyf"][source].isComposite(), cp
            assert ([(c.x, c.y, c.flags) for c in full["glyf"][target].components]
                    == [(c.x, c.y, c.flags) for c in donor["glyf"][source].components]), cp
        else:
            assert (full["glyf"][target].getCoordinates(full["glyf"])
                    == donor["glyf"][source].getCoordinates(donor["glyf"])), f"WenKai outline U+{cp:04X}"
        for tag in ("hmtx", "vmtx"):
            assert full[tag][target] == donor[tag][source], (cp, tag)
    # Every sampled ideograph is the donor's outline eroded by the weight model.
    for cp in normalized[::97]:
        target, source = after[cp], donor.getBestCmap()[cp]
        radius = normalization_radius(donor_set, source, model)
        glyph = erode_glyph(donor, source, radius, donor_set) if radius >= MIN_EROSION else None
        if glyph is None:
            assert (full["glyf"][target].getCoordinates(full["glyf"])
                    == donor["glyf"][source].getCoordinates(donor["glyf"])), cp
            assert full["hmtx"][target] == donor["hmtx"][source], cp
            continue
        assert (full["glyf"][target].getCoordinates(full["glyf"])
                == glyph.getCoordinates(full["glyf"])), f"Normalized outline U+{cp:04X}"
        assert full["hmtx"][target][1] == glyph.xMin, (cp, "lsb")
        expected_top = donor["vmtx"][source][1] + donor["glyf"][source].yMax - glyph.yMax
        assert full["vmtx"][target] == (donor["vmtx"][source][0], expected_top), (cp, "vmtx")
    # The imported ideographs now follow Klee's thickness/density model.
    residuals, changed_residuals = [], []
    for cp in ideographs:
        source = donor.getBestCmap()[cp]
        measured = thickness_area(full_set, after[cp])
        donor_measured = thickness_area(donor_set, source)
        assert measured and donor_measured, cp
        residual = measured[0] / target_thickness(donor_measured[1], model)
        residuals.append(residual)
        radius = normalization_radius(donor_set, source, model)
        if source in eligible and radius >= MIN_EROSION:
            changed_residuals.append(residual)
    klee_residuals = []
    for cp, name in base.getBestCmap().items():
        if not is_ideograph(cp):
            continue
        measured = thickness_area(base_set, name)
        if measured:
            klee_residuals.append(measured[0] / target_thickness(measured[1], model))
    p90 = sorted(klee_residuals)[int(0.9 * (len(klee_residuals) - 1))]
    assert abs(median(changed_residuals) - 1.0) <= 0.02, (
        "Normalized weight residual", median(changed_residuals))
    assert sum(r > p90 for r in changed_residuals) / len(changed_residuals) <= 0.15, "Normalized weight tail"
    assert sum(r > 1.10 for r in residuals) / len(residuals) <= 0.01, "Uncorrected heavy glyphs"
    for tag, fields in {"hhea": ("ascent", "descent", "lineGap"),
                        "vhea": ("ascent", "descent", "lineGap"),
                        "OS/2": ("sTypoAscender", "sTypoDescender", "sTypoLineGap",
                                 "usWinAscent", "usWinDescent")}.items():
        assert all(getattr(base[tag], f) == getattr(full[tag], f) for f in fields), tag
    assert not any(t.format == 14 for t in full["cmap"].tables)
    # Coverage describes the merged repertoire, not one donor's summary.
    assert full["OS/2"].getUnicodeRanges() == intersectUnicodeRanges(after)
    assert full["OS/2"].getCodePageRanges() == calcCodePageRanges(after)
    assert "LXGW" in full["name"].getDebugName(0)
    assert "LXGW" not in base["name"].getDebugName(0)

    # WenKai's weight names differ from Klee's. Compare the same Han letters
    # so selecting WenKai Regular (based on Klee SemiBold) fails this check.
    calibration = set("一二三十人口大小上下左右中山川田土木本末未日月水火金天年時分文字日本語心骨辻辺世界和平学学校生命森雨雪風春夏秋冬花草竹林色白黒赤青石玉米耳目手足力休体住位信高長安家室宮京都海池湖河流清明星空雲電光国王主正村町市道通行来去入出東西南北好女子男父母兄弟姉妹友愛見聞言読書話食飲車馬門開閉")
    donor_set, klee_set = donor.getGlyphSet(), klee.getGlyphSet()
    ratios = [stroke_thickness(donor_set, donor.getBestCmap()[ord(c)]) /
              stroke_thickness(klee_set, klee.getBestCmap()[ord(c)])
              for c in calibration]
    # Area/perimeter estimates are affected by regional form differences;
    # require a close overall match rather than identical individual widths.
    assert 0.95 <= median(ratios) <= 1.12, ("Donor stroke-weight mismatch", median(ratios))

    assert set(fonts["Kureedo Kana"].getBestCmap()) == set(before) & set(KANA_UNICODES)
    additions = fonts["Kureedo Additions"]
    assert set(additions.getBestCmap()) == set(before) - set(klee.getBestCmap())
    assert len(additions.getBestCmap()) == 26
    assert 0x3042 in fonts["Kureedo Kana"].getBestCmap()
    assert 0x6F22 not in fonts["Kureedo Kana"].getBestCmap()

    base_hb = hb.Font(hb.Face((ROOT / "build/japanese-base.ttf").read_bytes()))
    full_hb = hb.Font(hb.Face((FONTS / "KureedoFull-Regular.ttf").read_bytes()))
    for cp in before:
        for direction in ("ltr", "ttb"):
            assert shape(base_hb, chr(cp), direction) == shape(full_hb, chr(cp), direction), (cp, direction)
    for text in ("𪜈", "トモ", "コト゚", "ネヰ", "ㇷ゚", "セ゚ツ゚ト゚", "カ゚キ゚ク゚ケ゚コ゚"):
        for direction in ("ltr", "ttb"):
            for features in ({}, {"hist": True}, {"hlig": True, "ss02": True}):
                assert shape(base_hb, text, direction, features) == shape(full_hb, text, direction, features), (text, direction, features)
    extra_hb = hb.Font(hb.Face((FONTS / "KureedoAdditions-Regular.ttf").read_bytes()))
    for direction in ("ltr", "ttb"):
        assert len(shape(extra_hb, "ㇷ゚", direction)) == 1
        assert shape(extra_hb, "𪜈", direction) != shape(extra_hb, "𪜈", direction, {"ss02": True})
    print("Edition checks passed: 46,923 characters, normalized imported weight, donor metrics, Japanese shaping, three TTF/WOFF2 families.")


if __name__ == "__main__":
    check()
