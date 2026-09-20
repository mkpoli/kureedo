#!/usr/bin/env python3
"""Build Kureedo from the pinned Klee One release.

Two targets come out of one source tree:

  fonts/Kureedo-Regular.ttf        the whole of Klee One with the historical
                                   glyphs and features added (desktop)
  fonts/KureedoKata-Regular.woff2  the kana subset for the web, plus a TTF
  fonts/KureedoKata-Regular.ttf    of the same subset

Historical forms are alternates. Default ネ and ヰ stay Klee's; `hist`, `ss01`
and the per-letter `cv01`/`cv02` switch to the 子-shaped ネ and 井-shaped ヰ.
Letters Klee One lacks are added at their code points; a digraph is also reachable
from its letters through `hlig`.
"""
import argparse
import hashlib
import json
import unicodedata
from pathlib import Path
from urllib.request import urlopen
from xml.etree import ElementTree

import math

import pathops
from fontTools import subset
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.perimeterPen import PerimeterPen
from fontTools.otlLib.builder import buildLigatureSubstSubtable, buildLookup, buildSingleSubstSubtable
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables

ROOT = Path(__file__).resolve().parent.parent
GLYPHS = ROOT / "sources/glyphs"
FONTS = ROOT / "fonts"
KLEE_COMMIT = "8b0532731b63ad8a445ca341d8d7d941079b83ab"
KLEE_URL = f"https://raw.githubusercontent.com/fontworks-fonts/Klee/{KLEE_COMMIT}/fonts/ttf/KleeOne-Regular.ttf"
KLEE_SHA256 = "74cb0a6523cc22b221ceaa7b78b56cea66512ec14b4145fd0102ffe27c30d084"
KLEE_PATH = ROOT / "sources/klee/KleeOne-Regular.ttf"

VERSION = (0, 4, 0)  # release tag v0.4.0; name ID 5 and head.fontRevision carry 0.400
COPYRIGHT = ("Copyright 2020 The Klee Project Authors (https://github.com/fontworks-fonts/Klee); "
             "historical glyphs Copyright 2026 The Kureedo Project Authors (https://github.com/mkpoli/kureedo)")
URL = "https://github.com/mkpoli/kureedo"
BASELINE = 880  # y of the em top in the SVG sources (1000-unit em, y down)

# Each historical form: the modern letter it is an alternate of, its own code point in
# Kana Extended-A (Unicode 18.0), the SVG source, and its character-variant feature.
HISTORICAL = [
    dict(code=0x30CD, historic=0x1B127, svg="ne.svg", cv="cv01", label="Katakana ne, 子-shaped"),
    dict(code=0x30F0, historic=0x1B128, svg="wi.svg", cv="cv02", label="Katakana wi, 井-shaped"),
]
# Letters Klee One lacks, each with its code point and SVG source; a digraph also names the
# letters it joins, and `hlig` forms it from them.
LETTERS = [
    dict(code=0x2A708, svg="tomo.svg", letters="トモ", label="Katakana tomo ligature"),
]
KATA_UNICODES = [0x20, *range(0x3000, 0x3040), *range(0x3099, 0x309D), *range(0x30A0, 0x3100), *range(0x31F0, 0x3200),
                 *(f["historic"] for f in HISTORICAL), *(l["code"] for l in LETTERS)]

# Ainu small kana follow Klee's own small-kana convention (ッ against ツ): 78% of the full-size
# letter, centred in the cell on the baseline, and shifted up and to the right in vertical text.
# `weight` is the stroke thickness the scaled glyph keeps, as a fraction of the full-size
# stroke; Klee's own small kana keep about 0.9, plain scaling would leave 0.78.
# The values were settled by blind comparison rounds (docs/methods.md).
SMALL = dict(scale=0.78, x=114, y=-25, vertTop=329, vertX=130, vertY=0, weight=0.9)
# Marks on a small base are scaled with the letter and set with their centre at
# (base.xMax + cx, base.yMax + cy): the direction Klee's プ uses for its handakuten, at
# プ's clearance from the stroke scaled to the small letter (19 units).
SMALL_MARK = dict(scale=0.78, cx=71, cy=39, weight=0.9)


def stroke_thickness(glyph_set, name, scale=1.0):
    """Mean stroke thickness of a glyph: twice its area over its perimeter."""
    area, perimeter = AreaPen(glyph_set), PerimeterPen(glyph_set)
    for pen in (area, perimeter):
        glyph_set[name].draw(TransformPen(pen, (scale, 0, 0, scale, 0, 0)))
    return abs(area.value) * 2 / perimeter.value


def dilated(draw, radius, steps=12):
    """Union of the outline with copies shifted around a circle: a dilation by `radius`."""
    result = pathops.Path()
    for i in range(steps):
        angle = 2 * math.pi * i / steps
        part = pathops.Path()
        draw(TransformPen(part.getPen(), (1, 0, 0, 1, radius * math.cos(angle), radius * math.sin(angle))))
        result = pathops.op(result, part, pathops.PathOp.UNION) if i else part
    return pathops.simplify(result, fix_winding=True)


def scaled_glyph(glyph_set, name, scale, dx, dy, weight):
    """Scale a glyph and, when `weight` is set, thicken it back towards that stroke fraction."""
    radius = 0.0
    if weight:
        radius = max(0.0, (weight * stroke_thickness(glyph_set, name) - stroke_thickness(glyph_set, name, scale)) / 2)
    def draw(pen):
        glyph_set[name].draw(TransformPen(pen, (scale, 0, 0, scale, dx, dy)))
    tt = TTGlyphPen(None)
    if radius:
        path = dilated(draw, radius)
        path.draw(Cu2QuPen(tt, max_err=0.2, reverse_direction=not path.clockwise))
    else:
        draw(tt)
    return tt.glyph()


def fetch_klee():
    if not KLEE_PATH.exists():
        KLEE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(KLEE_URL, timeout=60) as response:
            KLEE_PATH.write_bytes(response.read())
    if hashlib.sha256(KLEE_PATH.read_bytes()).hexdigest() != KLEE_SHA256:
        raise ValueError("Klee One checksum mismatch")
    return TTFont(KLEE_PATH, recalcTimestamp=False)


def svg_glyph(path: Path):
    pen = TTGlyphPen(None)
    curves = Cu2QuPen(TransformPen(pen, (1, 0, 0, -1, 0, BASELINE)), max_err=0.2, reverse_direction=True)
    for element in ElementTree.parse(path).getroot().iter("{http://www.w3.org/2000/svg}path"):
        parse_path(element.attrib["d"], curves)
    return pen.glyph(dropImpliedOnCurves=True)


class Builder:
    def __init__(self, font: TTFont, small=None, small_mark=None, sources=None):
        self.small = {**SMALL, **(small or {})}
        self.small_mark = {**SMALL_MARK, **(small_mark or {})}
        self.sources = sources or {}  # SVG file name -> path replacing the one in sources/glyphs (candidate builds)
        self.vertical = {}  # glyph -> its vertical variant, registered under vert and vrt2
        self.font = font
        self.cmap = font.getBestCmap()
        self.order = list(font.getGlyphOrder())
        self.name_id = max(n.nameID for n in font["name"].names if n.nameID < 256) + 1
        self.name_id = max(self.name_id, 256)

    def source(self, svg):
        return svg_glyph(Path(self.sources.get(svg, GLYPHS / svg)))

    def put(self, name, glyph, advance=1000, origin=BASELINE, mark=False):
        glyph.recalcBounds(self.font["glyf"])
        self.font["glyf"][name] = glyph
        self.font["hmtx"][name] = (advance, glyph.xMin)
        self.font["vmtx"][name] = (0 if mark else 1000, origin - glyph.yMax)
        self.order.append(name)
        if mark:
            self.font["GDEF"].table.GlyphClassDef.classDefs[name] = 3

    def encode(self, code, name):
        for table in self.font["cmap"].tables:
            # Format 4 subtables hold the BMP only; supplementary code points go to format 12.
            if table.isUnicode() and (code <= 0xFFFF or table.format == 12):
                table.cmap[code] = name

    def add_name(self, text):
        self.font["name"].setName(text, self.name_id, 3, 1, 0x409)
        self.name_id += 1
        return self.name_id - 1

    def add_feature(self, tag, lookup, params=None):
        """Register one lookup under `tag` for every language system.

        A language system that already lists the tag gets the lookup appended to
        that feature; the others get a new feature record.
        """
        gsub = self.font["GSUB"].table
        gsub.LookupList.Lookup.append(lookup)
        gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)
        lookup_index = gsub.LookupList.LookupCount - 1
        records = gsub.FeatureList.FeatureRecord
        extended = set()
        new_index = None
        for script in gsub.ScriptList.ScriptRecord:
            systems = [script.Script.DefaultLangSys] if script.Script.DefaultLangSys else []
            systems += [r.LangSys for r in script.Script.LangSysRecord]
            for system in systems:
                existing = [i for i in system.FeatureIndex if records[i].FeatureTag == tag]
                if existing:
                    feature = records[existing[0]].Feature
                    if id(feature) not in extended:
                        feature.LookupListIndex.append(lookup_index)
                        feature.LookupCount = len(feature.LookupListIndex)
                        extended.add(id(feature))
                    continue
                if new_index is None:
                    record = otTables.FeatureRecord()
                    record.FeatureTag = tag
                    record.Feature = otTables.Feature()
                    record.Feature.FeatureParams = params
                    record.Feature.LookupListIndex = [lookup_index]
                    record.Feature.LookupCount = 1
                    records.append(record)
                    new_index = len(records) - 1
                system.FeatureIndex.append(new_index)
                system.FeatureCount = len(system.FeatureIndex)
        gsub.FeatureList.FeatureCount = len(records)

    def add_historical(self):
        """Add the historical outlines and the features that reach them."""
        all_forms = {}
        for form in HISTORICAL:
            base = self.cmap[form["code"]]
            # The letter has its own code point in Kana Extended-A; the same glyph is
            # also the modern letter's historical alternate.
            name = f"uni{form['historic']:04X}"
            self.put(name, self.source(form["svg"]))
            self.encode(form["historic"], name)
            self.cmap[form["historic"]] = name
            # Klee's own horizontal/vertical alternates of the letter also yield
            # the historical form, whatever order the features apply in.
            mapping = {base: name}
            for suffix in (".vert", ".hori"):
                if base + suffix in self.order:
                    mapping[base + suffix] = name
            all_forms.update(mapping)
            params = otTables.FeatureParamsCharacterVariants()
            params.Format = 0
            params.FeatUILabelNameID = self.add_name(form["label"])
            params.FeatUITooltipTextNameID = 0
            params.SampleTextNameID = self.add_name(chr(form["code"]))
            params.NumNamedParameters = 0
            params.FirstParamUILabelNameID = 0
            params.CharCount = 1
            params.Character = [form["code"]]
            self.add_feature(form["cv"], buildLookup([buildSingleSubstSubtable(mapping)]), params)
        historical = buildLookup([buildSingleSubstSubtable(all_forms)])
        self.add_feature("hist", historical)
        self.extend_aalt({self.cmap[form["code"]]: f'uni{form["historic"]:04X}' for form in HISTORICAL})
        params = otTables.FeatureParamsStylisticSet()
        params.Version = 0
        params.UINameID = self.add_name("Edo-period printed forms")
        self.add_feature("ss01", historical, params)

    def add_letters(self):
        """Add the missing letters at their code points, and `hlig` forming each digraph from its letters."""
        ligatures = {}
        for form in LETTERS:
            name = f"uni{form['code']:04X}"
            self.put(name, self.source(form["svg"]))
            self.encode(form["code"], name)
            self.cmap[form["code"]] = name
            if form["letters"]:
                ligatures[tuple(self.cmap[ord(c)] for c in form["letters"])] = name
        self.add_feature("hlig", buildLookup([buildLigatureSubstSubtable(ligatures)]))

    def add_marks(self):
        """Compose kana with combining dakuten and handakuten into one cell."""
        positions = json.loads((GLYPHS / "mark-positions.json").read_text())
        substitutions = {}
        for code in (0x309A, 0x3099):
            mark = f"kanaMark{code:04X}"
            self.put(mark, self.source(f"mark-{code:04x}.svg"), advance=0, mark=True)
            self.encode(code, mark)
            m = self.small_mark
            small_mark = mark
            if m["scale"] != 1 or m["weight"]:
                small_mark = mark + ".small"
                self.put(small_mark, scaled_glyph(self.font.getGlyphSet(), mark, m["scale"], 0, 0, m["weight"]), advance=0, mark=True)
            for base, base_name in self.cmap.items():
                if not (0x30A1 <= base <= 0x30FA or 0x31F0 <= base <= 0x31FF):
                    continue
                sequence = chr(base) + chr(code)
                nfc = unicodedata.normalize("NFC", sequence)
                if len(nfc) == 1 and ord(nfc) in self.cmap:
                    composed = self.cmap[ord(nfc)]
                elif sequence in positions:
                    composed = f"kanaComposite{base:04X}_{code:04X}"
                    dx, dy = positions[sequence]
                    pen = TTGlyphPen(self.font.getGlyphSet())
                    pen.addComponent(base_name, (1, 0, 0, 1, 0, 0))
                    if 0x31F0 <= base <= 0x31FF:
                        m = self.small_mark
                        box = self.font["glyf"][small_mark]
                        mx, my = (box.xMin + box.xMax) / 2, (box.yMin + box.yMax) / 2
                        b = self.font["glyf"][base_name]
                        tx, ty = b.xMax + m["cx"] - mx, b.yMax + m["cy"] - my
                        pen.addComponent(small_mark, (1, 0, 0, 1, round(tx), round(ty)))
                        if base_name in self.vertical:
                            vpen = TTGlyphPen(self.font.getGlyphSet())
                            vpen.addComponent(self.vertical[base_name], (1, 0, 0, 1, 0, 0))
                            vb = self.font["glyf"][self.vertical[base_name]]
                            vpen.addComponent(small_mark, (1, 0, 0, 1, round(tx + vb.xMax - b.xMax), round(ty + vb.yMax - b.yMax)))
                            self.put(composed + ".vert", vpen.glyph(), origin=vb.yMax + self.font["vmtx"][self.vertical[base_name]][1])
                            self.vertical[composed] = composed + ".vert"
                    else:
                        pen.addComponent(mark, (1, 0, 0, 1, dx, dy))
                    # Small kana sit lower than full-size kana in vertical text.
                    origin = self.font["glyf"][base_name].yMax + self.font["vmtx"][base_name][1]
                    self.put(composed, pen.glyph(), origin=origin)
                else:
                    continue
                substitutions[(base_name, mark)] = composed
        self.add_feature("ccmp", buildLookup([buildLigatureSubstSubtable(substitutions)]))
        if self.vertical:
            for tag in ("vert", "vrt2"):
                self.add_feature(tag, buildLookup([buildSingleSubstSubtable(dict(self.vertical))]))

    def add_small_kana(self):
        """Klee One lacks U+31F0–31FF. Scale its full-size kana to 65%, set at the lower right."""
        glyphs = self.font.getGlyphSet()
        sm = self.small
        for code, base in zip(range(0x31F0, 0x3200), "クシストヌハヒフヘホムラリルレロ"):
            name = f"uni{code:04X}"
            for suffix, dx, dy in (("", 0, 0), (".vert", sm["vertX"], sm["vertY"])):
                if suffix and not (dx or dy):
                    continue
                small = scaled_glyph(glyphs, self.cmap[ord(base)], sm["scale"], sm["x"] + dx, sm["y"] + dy, sm["weight"])
                small.recalcBounds(self.font["glyf"])
                self.font["glyf"][name + suffix] = small
                self.font["hmtx"][name + suffix] = (1000, small.xMin)
                self.font["vmtx"][name + suffix] = (1000, sm["vertTop"])
                self.order.append(name + suffix)
                if suffix:
                    self.vertical[name] = name + suffix
            self.encode(code, name)
            self.cmap[code] = name

    def sort_features(self):
        """Keep the feature list sorted by tag, as the layout specification asks."""
        gsub = self.font["GSUB"].table
        records = gsub.FeatureList.FeatureRecord
        ordered = sorted(range(len(records)), key=lambda i: (records[i].FeatureTag, i))
        remap = {old: new for new, old in enumerate(ordered)}
        gsub.FeatureList.FeatureRecord = [records[i] for i in ordered]
        for script in gsub.ScriptList.ScriptRecord:
            systems = [script.Script.DefaultLangSys] if script.Script.DefaultLangSys else []
            systems += [r.LangSys for r in script.Script.LangSysRecord]
            for system in systems:
                system.FeatureIndex = sorted(remap[i] for i in system.FeatureIndex)
                if system.ReqFeatureIndex != 0xFFFF:
                    system.ReqFeatureIndex = remap[system.ReqFeatureIndex]

    def extend_aalt(self, alternates):
        """Append the historical forms to Klee's `aalt` alternate sets."""
        gsub = self.font["GSUB"].table
        for record in gsub.FeatureList.FeatureRecord:
            if record.FeatureTag != "aalt":
                continue
            for index in record.Feature.LookupListIndex:
                for subtable in gsub.LookupList.Lookup[index].SubTable:
                    if subtable.LookupType == 3:
                        for base, name in alternates.items():
                            subtable.alternates.setdefault(base, []).append(name)

    def finish(self):
        self.sort_features()
        self.font.setGlyphOrder(self.order)


JAPANESE = {"Kureedo": "クレード", "Kureedo Kata": "クレード カタ"}


def set_names(font: TTFont, family: str):
    ps = family.replace(" ", "") + "-Regular"
    version = f"{VERSION[0]}.{VERSION[1]}{VERSION[2]:02d}"
    names = {0: COPYRIGHT, 1: family, 2: "Regular", 3: f"{version};KRDO;{ps}", 4: f"{family} Regular",
             5: f"Version {version}", 6: ps, 7: f"{family} is an independent derivative of Klee One; Klee is a trademark of Fontworks Inc.",
             8: "The Kureedo Project Authors", 9: "Fontworks Inc.; The Kureedo Project Authors", 11: URL, 12: URL}
    table = font["name"]
    table.names = [n for n in table.names if n.nameID not in names or (n.platformID, n.platEncID) == (3, 1)]
    for record in table.names:
        if record.nameID in names and record.langID == 0x409:
            record.string = names[record.nameID].encode(record.getEncoding())
    table.names = [n for n in table.names if n.langID != 0x411]
    ja = JAPANESE.get(family, family)
    table.setName(ja, 1, 3, 1, 0x411)
    table.setName("Regular", 2, 3, 1, 0x411)
    table.setName(ja + " Regular", 4, 3, 1, 0x411)
    font["head"].fontRevision = float(version)
    font["OS/2"].achVendID = "KRDO"


def build(out_dir: Path = FONTS, small=None, small_mark=None, family_suffix="", sources=None):
    font = fetch_klee()
    builder = Builder(font, small, small_mark, sources)
    builder.add_small_kana()
    builder.add_historical()
    builder.add_letters()
    builder.add_marks()
    builder.finish()
    out_dir.mkdir(parents=True, exist_ok=True)

    set_names(font, "Kureedo" + family_suffix)
    full = out_dir / f"Kureedo{family_suffix.replace(' ', '')}-Regular.ttf"
    font.save(full)
    print(f"Built {full} ({full.stat().st_size:,} bytes)")

    options = subset.Options()
    options.hinting = False
    options.name_IDs = "*"
    options.name_legacy = True
    options.name_languages = "*"
    options.layout_features += ["hist", "hlig", "ss01", "cv01", "cv02"]
    options.notdef_outline = True
    options.glyph_names = True
    kata = TTFont(full, recalcTimestamp=False)
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=KATA_UNICODES)
    sub.subset(kata)
    set_names(kata, "Kureedo Kata" + family_suffix)
    for flavor, suffix in ((None, ".ttf"), ("woff2", ".woff2")):
        kata.flavor = flavor
        out = out_dir / f"KureedoKata{family_suffix.replace(' ', '')}-Regular{suffix}"
        kata.save(out)
        print(f"Built {out} ({out.stat().st_size:,} bytes)")
    return full, out


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    build()
