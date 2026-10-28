"""Fill unencoded characters from LXGW WenKai, retaining Kureedo's glyphs."""
import hashlib
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from fontTools import subset
from fontTools.merge import Merger
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
# WenKai Regular is based on Klee SemiBold. Light is the closer match to
# Kureedo's Klee Regular base; weight names do not align across the families.
SOURCE = ROOT / "sources/wenkai/LXGWWenKai-Light.ttf"
URL = "https://github.com/lxgw/LxgwWenKai/releases/download/v1.530/LXGWWenKai-Light.ttf"
SHA256 = "9a50e3f0f51fad60d68152d5191bce1a495bfc4b9ceb1cee24833835511d1dca"


def private_use(cp):
    return (0xE000 <= cp <= 0xF8FF or 0xF0000 <= cp <= 0xFFFFD
            or 0x100000 <= cp <= 0x10FFFD)


def fetch_wenkai():
    if not SOURCE.exists():
        SOURCE.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(URL, timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != SHA256:
            raise ValueError("LXGW WenKai checksum mismatch")
        SOURCE.write_bytes(data)
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SHA256:
        raise ValueError("LXGW WenKai checksum mismatch")
    return TTFont(SOURCE, recalcTimestamp=False)


def font_buffer(font):
    data = BytesIO()
    font.save(data)
    data.seek(0)
    return data


def preserve_script_fallbacks(base, donor):
    """Keep DFLT behavior when a donor introduces a script or language system.

    For example, TOMO is Han. Introducing a hani script must not hide the
    Kureedo ss02 feature it previously reached through DFLT.
    """
    for tag in ("GSUB", "GPOS"):
        if tag not in base or tag not in donor:
            continue
        scripts = base[tag].table.ScriptList
        records = {r.ScriptTag: r for r in scripts.ScriptRecord}
        fallback = records.get("DFLT")
        if fallback is None:
            continue
        for incoming in donor[tag].table.ScriptList.ScriptRecord:
            if incoming.ScriptTag not in records:
                record = deepcopy(fallback)
                record.ScriptTag = incoming.ScriptTag
                records[record.ScriptTag] = record
            script = records[incoming.ScriptTag].Script
            languages = {r.LangSysTag for r in script.LangSysRecord}
            for language in incoming.Script.LangSysRecord:
                if language.LangSysTag not in languages and script.DefaultLangSys:
                    record = deepcopy(language)
                    record.LangSys = deepcopy(script.DefaultLangSys)
                    script.LangSysRecord.append(record)
            script.LangSysRecord.sort(key=lambda r: r.LangSysTag)
            script.LangSysCount = len(script.LangSysRecord)
        scripts.ScriptRecord = sorted(records.values(), key=lambda r: r.ScriptTag)
        scripts.ScriptCount = len(scripts.ScriptRecord)


def sort_features(font):
    """Restore the OpenType feature-tag ordering after merging script lists."""
    for tag in ("GSUB", "GPOS"):
        if tag not in font:
            continue
        table = font[tag].table
        records = table.FeatureList.FeatureRecord
        order = sorted(range(len(records)), key=lambda i: records[i].FeatureTag)
        remap = {old: new for new, old in enumerate(order)}
        table.FeatureList.FeatureRecord = [records[i] for i in order]
        for record in table.ScriptList.ScriptRecord:
            script = record.Script
            systems = ([script.DefaultLangSys] if script.DefaultLangSys else [])
            systems += [r.LangSys for r in script.LangSysRecord]
            for system in systems:
                system.FeatureIndex = sorted(remap[i] for i in system.FeatureIndex)
                if system.ReqFeatureIndex != 0xFFFF:
                    system.ReqFeatureIndex = remap[system.ReqFeatureIndex]


def extend_coverage(base):
    """Merge only missing public code points and their layout dependencies.

    Kureedo is first in the glyph order. The donor has no overlapping cmap
    entries, so the merger cannot introduce language-dependent replacements
    for Kureedo glyphs. Donor private-use conventions and UVS are excluded.
    """
    donor = fetch_wenkai()
    if donor["head"].unitsPerEm != base["head"].unitsPerEm:
        raise ValueError("WenKai and Kureedo must use the same units per em")
    base_points = set(base.getBestCmap())
    missing = {cp for cp in donor.getBestCmap()
               if cp not in base_points and not private_use(cp)}
    donor["cmap"].tables = [t for t in donor["cmap"].tables if t.format != 14]
    options = subset.Options()
    options.layout_features = ["*"]
    options.glyph_names = True
    options.hinting = False
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=missing)
    sub.subset(donor)
    prepared = TTFont(font_buffer(base), recalcTimestamp=False)
    preserve_script_fallbacks(prepared, donor)
    merged = Merger().merge([font_buffer(prepared), font_buffer(donor)])
    merged.recalcTimestamp = False
    # fontTools' layout merge drops FeatureParams; the name table is retained
    # from the first font, so its feature UI labels can be restored directly.
    params = {r.FeatureTag: r.Feature.FeatureParams
              for r in base["GSUB"].table.FeatureList.FeatureRecord
              if r.Feature.FeatureParams is not None}
    for record in merged["GSUB"].table.FeatureList.FeatureRecord:
        if record.FeatureTag in params:
            record.Feature.FeatureParams = deepcopy(params[record.FeatureTag])
    sort_features(merged)
    # Line spacing, identity and timestamps remain those of the Japanese base.
    # Bounds, repertoire flags and per-glyph metrics come from the merged font.
    retained = {
        "head": ("created", "modified", "fontRevision"),
        "hhea": ("ascent", "descent", "lineGap"),
        "vhea": ("ascent", "descent", "lineGap"),
        "OS/2": ("sTypoAscender", "sTypoDescender", "sTypoLineGap",
                 "usWinAscent", "usWinDescent", "sxHeight", "sCapHeight"),
    }
    for tag, fields in retained.items():
        for field in fields:
            setattr(merged[tag], field, getattr(base[tag], field))
    # Both donors describe their own repertoire incompletely; state the merged one.
    merged["OS/2"].recalcUnicodeRanges(merged)
    merged["OS/2"].recalcCodePageRanges(merged)
    if len(merged.getGlyphOrder()) > 65535:
        raise ValueError("Merged font exceeds the OpenType glyph limit")
    # Include the donor's copyright and reserved names in installable metadata.
    name = merged["name"]
    for record in name.names:
        if record.nameID == 0:
            record.string = (record.toUnicode() + "; " +
                             donor["name"].getDebugName(0)).encode(record.getEncoding())
        elif record.nameID == 9:
            record.string = (record.toUnicode() + "; LXGW").encode(record.getEncoding())
    return merged
