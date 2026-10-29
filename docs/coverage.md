# Character coverage and editions

Kureedo retains Klee One's Japanese forms. The Full edition fills missing public
Unicode code points from LXGW WenKai Light 1.530. Existing Kureedo outlines,
horizontal and vertical metrics, default mappings and line spacing are retained.

The comparison uses merged Kureedo commit `d9b5243`, GenZui Serif 0.114, and the
WenKai releases available on 21 October 2026. Counts are encoded code points;
alternate glyphs and variation sequences are counted separately. Input hashes
and block-level results are in [coverage.json](coverage.json).

| Font | Encoded characters | Characters absent from Japanese base |
| --- | ---: | ---: |
| Japanese base | 10,204 | — |
| GenZui Serif 0.114 | 17,090 | 7,011 |
| LXGW WenKai 1.530 | 46,926 | 36,731 |
| LXGW WenKai GB 1.530 | 46,926 | 36,731 |
| LXGW WenKai TC 1.530 | 25,694 | 15,499 |
| LXGW WenKai KR 0.902 | 27,024 | 18,030 |
| Kureedo Full | 46,923 | 36,719 |

Kureedo and GenZui overlap imperfectly: Kureedo has 125 code points absent from
GenZui, so the coverage gap is larger than the difference between their totals.
GB, TC and KR offer no further code points beyond full WenKai. Their regional
glyph choices differ. The full WenKai edition is the sole donor.

The donor's 12 private-use entries, including its logo, are excluded. Nine
Kureedo code points are absent from WenKai, so the Full edition's total is
46,926 minus 12 plus nine: **46,923**.

## What Full supplies

The 36,719 imported code points include 22,773 CJK unified and compatibility
ideographs, 11,172 Hangul syllables, 50 Seal characters, 44 mahjong tiles,
six dice symbols, and additional letters, punctuation and symbols. The import
includes characters such as 汉、语、简、龙、爱、习、书、车、马、风、发、东、乐.
Kureedo's existing 心、骨、辻 and other shared forms remain Japanese.

All 6,763 ideographs in GB2312's ideograph rows are covered. The Japanese
base covers 3,780 of them. This measures a standard repertoire; it is not
a count of every simplified character in Unicode.

WenKai is a Klee One derivative and uses the same 1,000-unit em. The donor
subset retains layout dependencies and vertical forms. Kureedo's original
script fallback behavior and feature names are preserved across the merge.
The Full edition contains 52,233 glyphs: the reserved donor outlines add two glyph names.

WenKai Light is the donor weight. WenKai calls its Klee SemiBold-based weight
“Regular” ([upstream explanation](https://github.com/lxgw/LxgwWenKai#项目简介)).
On 138 shared Han characters, the median area/perimeter stroke-width estimate
relative to Klee Regular is 1.057 for WenKai Light and 1.282 for WenKai Regular.
Regional forms affect this estimate; it is a weight comparison, not a claim of
identical outlines. [Measurement details](weight-match.json) record the sample
and source hash. Light and Regular have identical encoded repertoires, so this
weight choice retains all 46,923 characters.

The added simplified glyphs were assembled from cut Klee SemiBold strokes, so
Light alone leaves them heavier than Klee's own drawings. Each imported
ideograph is therefore eroded to the thickness Klee's density model predicts
for its ink area; advances and vertical origins stay ([weight matching](weight.md)).
Kureedo's existing glyphs retain their original weight.

## Choosing an edition

| Family | Encoded characters | Scope |
| --- | ---: | --- |
| Kureedo Full | 46,923 | Japanese base, Kureedo additions and WenKai coverage |
| Kureedo Kana | 311 | Available hiragana, katakana, halfwidth kana, punctuation and historical forms from the Japanese base |
| Kureedo Additions | 26 | Code points absent from unmodified Klee One |

The Japanese base is an internal comparison build. Kata is folded into Kana.

Each edition has its own family and PostScript names and is built as TTF and
WOFF2. Full is a standalone font. Kana can be paired with
another font for kanji and Latin. Kana does not claim complete historical-kana coverage.

Additions contains 〱、〲、combining dakuten and handakuten, ゠、ヿ、ㇰ–ㇿ、𛀀、𛄧、𛄨
and 𪜈. It supports directly encoded characters, ㇷ゚ composition and the `ss02`
alternate of 𪜈. Select Kana for `hist` applied to ordinary ネ/ヰ,
`hlig` applied to トモ/コト, or combining marks on ordinary full-size kana.
These operations require the base letters and their substitutions in the
same font. A minimal additions-only fallback cannot provide them across fonts.

The three editions are also published, in release 0.5.0. Releases 0.4.3 and
earlier keep the Kureedo and Kureedo Kata packaging.

## Remaining kana coverage

GenZui covers all 763 code points identified by Unicode 18's Hiragana and
Katakana script properties and script extensions. The Japanese base covers 437;
Full covers 448. The narrower Kana edition deliberately excludes enclosed and
squared characters outside its documented blocks.

Full still lacks 346 code points found in GenZui: 255 in Kana Supplement, 39
in Kana Extended-A, 13 in Kana Extended-B, eight in Small Kana Extension, three
CJK-encoded kana ligatures, two CJK punctuation characters and 26 Okinawan
private-use characters. Klee-style historical kana and regional forms need a
separate design pass; copying GenZui's Mincho outlines would change their style.

## Variation sequences

The Japanese base and Full currently have no `cmap` format 14 mappings. GenZui
has 14,787 variation-sequence mappings. The WenKai donor has 41; they are
excluded from this character-coverage import.

Japanese IVD support needs a separate mapping audit against the
[Unicode Ideographic Variation Database](https://www.unicode.org/ivd/), beginning
with Adobe-Japan1 and the Japanese alternate outlines already present in Klee.
A sequence can reuse an existing glyph, so sequence totals do not measure how
many new outlines are required. WenKai's variation sequences do not establish
Japanese IVD coverage.

## Build and verification

```sh
.venv/bin/python scripts/build.py
.venv/bin/python scripts/check.py
.venv/bin/python scripts/check_editions.py
.venv/bin/python scripts/package.py
```

The build pins the donor URL and SHA-256. Checks compare every original glyph's
compiled outline and both advances, every imported ideograph's normalized
outline and metrics, every other imported glyph's donor outline and metrics apart from
composite radicals that reuse an ideograph component,
the imported weight distribution, default shaping at every original code point
in both directions, historical features, combining marks, names, donor stroke
weight and edition boundaries. TTF and WOFF2 repertoires must agree. The original
Japanese outlines and metrics are preserved in Full.

Packages under `build/packages/` contain TTF, WOFF2, a local stylesheet, usage
notes, license notices and checksums. Full includes the upstream WenKai notice
with its reserved font names. All editions remain under SIL OFL 1.1.

Upstream releases: [WenKai](https://github.com/lxgw/LxgwWenKai/releases/tag/v1.530),
[GB](https://github.com/lxgw/LxgwWenKaiGB/releases/tag/v1.530),
[TC](https://github.com/lxgw/LxgwWenKaiTC/releases/tag/v1.530),
[KR](https://github.com/lxgw/LxgwWenKaiKR/releases/tag/v0.902).
