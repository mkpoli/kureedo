# Kureedo（クレード）

[![Kureedo](https://img.shields.io/github/v/release/mkpoli/kureedo?label=Kureedo&color=1f3b5b)](https://github.com/mkpoli/kureedo/releases/latest/download/Kureedo-Regular.ttf)
[![Kureedo Kata](https://img.shields.io/github/v/release/mkpoli/kureedo?label=Kureedo%20Kata&color=1f3b5b)](https://github.com/mkpoli/kureedo/releases/latest/download/KureedoKata-Regular.woff2)
[![Licence: OFL 1.1](https://img.shields.io/badge/licence-OFL%201.1-4c7a4c)](OFL.txt)
[![Unicode 18.0](https://img.shields.io/badge/Unicode-18.0-7a4c7a)](https://www.unicode.org/charts/PDF/Unicode-18.0/U180-1B100.pdf)
[![jsDelivr](https://img.shields.io/jsdelivr/gh/hm/mkpoli/kureedo?label=jsDelivr)](https://www.jsdelivr.com/package/gh/mkpoli/kureedo)
[![kureedo.mkpo.li](https://img.shields.io/website?url=https%3A%2F%2Fkureedo.mkpo.li&label=kureedo.mkpo.li)](https://kureedo.mkpo.li)

Klee One with the letterforms of Edo-period Japanese print, and the kana that Ainu needs. It covers two katakana that woodblock editions used and modern fonts lack: a ネ written like 子 and a ヰ written like 井. Unicode 18.0 encodes them as 𛄧 U+1B127 KATAKANA LETTER ALTERNATE NE and 𛄨 U+1B128 KATAKANA LETTER ALTERNATE WI, and the font covers those code points; the same glyphs are also OpenType alternates of ネ and ヰ, so a text encoded with the ordinary letters can show the historical forms through a feature. It also adds the small katakana ㇰ–ㇿ (U+31F0–31FF), the semi-voiced セ゚ ツ゚ ト゚ ㇷ゚ and the nasal カ゚–コ゚, which Klee One lacks.

Specimen, type tester and webfont CDN: https://kureedo.mkpo.li

![Unicode 18.0 encodes 𛄧 U+1B127 and 𛄨 U+1B128](docs/images/unicode18-card.png)

![ネ and ヰ: default, hist, cv01, cv02](docs/images/forms.png)

The same editions set トモ as one letter, 𪜈 U+2A708. The font covers that code point, and the `hlig` feature forms the ligature from トモ. It also covers 𛀀 U+1B000, the archaic katakana e, and the double hyphen ゠ U+30A0.

![トモ default, hlig, 𪜈 U+2A708, ss02](docs/images/tomo.png)

Two fonts come out of one build:

| Font | File | Use |
|---|---|---|
| Kureedo | `Kureedo-Regular.ttf` | Desktop. The whole of Klee One Regular plus the historical glyphs, the extended kana and the features (8.7 MB). |
| Kureedo Kata | `KureedoKata-Regular.woff2`, `.ttf` | Web. Kana, kana punctuation and marks only (24 KB as WOFF2). Pair it with Klee One or another Japanese font for kanji and Latin. |

Download both from the [releases page](https://github.com/mkpoli/kureedo/releases); each release also carries `OFL.txt` and `SHA256SUMS.txt`.

Related typeface: [GenZui Serif / 源萃明朝](https://genzui.mkpo.li/), a Noto Serif JP derivative with hentaigana and historical kana.

## Using the fonts

On the web, either self-host the WOFF2:

```css
@font-face {
  font-family: "Kureedo Kata";
  src: url("KureedoKata-Regular.woff2") format("woff2");
  font-display: swap;
  unicode-range: U+3000-303F, U+3099-309C, U+30A0-30FF, U+31F0-31FF, U+1B000, U+1B127-1B128, U+2A708, U+1B124;
}
.edition { font-family: "Kureedo Kata", "Klee One", serif; font-feature-settings: "hist"; }
```

or load it from kureedo.mkpo.li. `/kureedo.css` follows the latest release; `/vX.Y.Z/kureedo.css` and the WOFF2 beside it are pinned and immutable, served with CORS and a one-year cache. The GitHub tags also work through jsDelivr (`https://cdn.jsdelivr.net/gh/mkpoli/kureedo@v0.4.3/fonts/KureedoKata-Regular.woff2`).

```html
<link rel="stylesheet" href="https://kureedo.mkpo.li/kureedo.css">
<link rel="stylesheet" href="https://kureedo.mkpo.li/v0.4.3/kureedo.css">
```

On the desktop, install `Kureedo-Regular.ttf` and pick it as the font. The historical forms come from the OpenType feature panel (Word: Font dialog, Advanced; LibreOffice: append `:hist` to the font name) or by typing U+1B127 and U+1B128 directly. ㇷ (U+31F7) followed by the combining handakuten U+309A gives ㇷ゚; セ゚ ツ゚ ト゚ and カ゚–コ゚ work the same way.

### Historical forms

Text encoded with the Kana Extended-A letters needs no feature. For text encoded with ordinary ネ and ヰ — which keeps search, sorting and copying working in software that has never heard of U+1B127 — the features below select the same glyphs.

| Feature | Effect |
|---|---|
| `hist` | All historical forms. |
| `ss01` | Edo-period printed forms. In this release the same set as `hist`. |
| `cv01` | ネ only. |
| `cv02` | ヰ only. |
| `hlig` | The digraphs from their letters (トモ → 𪜈 and the rest of the table above). Off by default, since not every トモ in a text is the ligature. |
| `ss02` | Straight left stroke for 𪜈; the default curves like 丿. Works with the encoded letter and with `hlig`. |

![Running text with and without hist](docs/images/running.png)

![Vertical text with and without hist](docs/images/vertical.png)

Klee One's own `hkna`/`vkna` alternates of ネ and ヰ also become the historical forms when a historical feature is on. In the full font, `hwid` and `ruby` keep Klee One's shapes and `aalt` lists the historical forms; Kureedo Kata carries none of those three features. Word processors list the character variants under their feature names; the fonts carry English and Japanese names.

## Coverage of Kureedo Kata

The subset requests U+0020, U+3000–303F, U+3099–309C, U+30A0–30FF, U+31F0–31FF, U+1B000, U+1B127–1B128, U+2A708 and U+1B124; code points Klee One does not cover (for example U+3031–3032, U+30FF) stay absent. `fonttools ttx -t cmap` lists the exact set, and the site shows it block by block. Glyphs Klee One does not have and this font adds: 𛄧 𛄨 𪜈 𛀀 ゠; the Ainu small kana ㇰ–ㇿ (U+31F0–31FF), set the way Klee sets its own small kana (78% of the full-size letter, centred on the baseline, stroke weight brought back to 0.92 of the full-size stroke as Klee's own ッ and ァ keep it, shifted up and right in vertical text through `vert`); combining ゛ and ゜ with zero advance; and `ccmp` ligatures that set セ゚ ツ゚ ト゚ ㇷ゚ カ゚ キ゚ ク゚ ケ゚ コ゚ in one cell, horizontally and vertically. The handakuten of ㇷ゚ is scaled with the letter and sits where プ puts its own, at プ's clearance from the stroke; on the full-size bases it starts where Klee places the dakuten on the same letter and keeps that clearance (`scripts/mark_positions.py`, `docs/methods.md`).

![Ainu small kana and composed marks](docs/images/ainu.png)

![Extended kana: the Ainu small kana, the semi-voiced セ゚ ツ゚ ト゚ ㇷ゚ and the nasal カ゚–コ゚](docs/images/ainu-card.png)

## ゠ double hyphen

゠ U+30A0 uses two native Klee hyphen strokes rising 3°. Vertical text uses two straight uprights through `vert` or `vrt2`. The selected pair won seven of eight finalist comparisons; the complete ballot and decision are in `docs/votes/double-hyphen/`.

![゠ in horizontal and vertical text](docs/images/double-hyphen.png)

## 𛀀 archaic katakana e

𛀀 U+1B000 joins an upright head from Klee One’s リ to the lower stroke of ラ. The same outline serves horizontal and vertical text. It won five of six primary finalist comparisons and tied the sixth; the ballot and confirmed design are in `docs/votes/archaic-e/`.

![𛀀 beside リ, ラ and エ](docs/images/archaic-e.png)

## Sources of the forms

**ネ from 子.** The Edo-period printed katakana ネ keeps the shape of its source character 子: an angular upper turn, a sloping crossbar, an upright stem and a short curved hook. Reference specimen: 上原熊次郎『蝦夷方言藻汐草』(1792), volume 2, [image 81](https://dglb01.ninjal.ac.jp/iiif/ezomosio/002/tiff/ezmg002-081.tiff/full/1495,/0/default.jpg) (国立国語研究所, CC BY 4.0), with the [292 ネ samples](https://codh.rois.ac.jp/char-shape/unicode/U%2B30CD/) in CODH's kuzushiji index (日本古典籍くずし字データセット, 国文研ほか所蔵／CODH加工, doi:10.20676/00000340, CC BY-SA 4.0) as the wider comparison.

**ヰ from 井.** The printed ヰ of the same editions keeps the full 井 frame. Eiso Chan, *Proposal on two archaic Katakana letters*, [L2/25-151](https://www.unicode.org/L2/L2025/25151-katakana-ne-wi.pdf) (2025-05-23), page 1 and section 3, collects historical specimens of both letters; the UTC accepted it at meeting 184 and Unicode 18.0 encodes the two letters in [Kana Extended-A](https://www.unicode.org/charts/PDF/Unicode-18.0/U180-1B100.pdf) under the heading Historic Katakana. They are separate letters from 子 U+5B50 and 井 U+4E95, and have no decomposition to ネ or ヰ.

**𪜈 from ト and モ.** The default has a curved 丿-like left stroke joined to モ. Its upper and middle bars rise 9° and 8° respectively; their contours retain Klee One’s pen terminals. `ss02` uses a straight left stroke with the same モ. The proportions follow the Unicode code chart glyph for [U+2A708](https://www.unicode.org/charts/PDF/U2A700.pdf) (source JK-65004) and the printed instances in 池田霧渓『種痘弁義』(1858), [image 6](https://dl.ndl.go.jp/api/iiif/2539156/R0000006/full/full/0/default.jpg) (国立国会図書館, [doi:10.11501/2539156](https://doi.org/10.11501/2539156), public domain), located through the みんなで翻刻 transcription ([honkoku-data v3](https://github.com/yuta1984/honkoku-data), CC BY-SA 4.0). The print sets the left stroke no taller than the モ and joins the bars to it; the code chart leaves them apart. The selected font outline joins the middle bar to the left stroke.

**𛄤 from ト and キ.** ト's upright, shortened as in 𪜈, beside キ compressed to 0.72 of its width.

The 0.2 ヰ outline keeps Klee's uprights and stroke ends and sets the bars 50 units closer, the upper 30 and the lower 60 units longer; it beat the 0.1 outline and the other finalists in blind comparison. `docs/methods.md` describes how each form was chosen, including the small kana and the mark positions, and `docs/votes/` holds the comparison records.

## Building

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python scripts/check.py
```

The build downloads Klee One Regular from the pinned commit of [fontworks-fonts/Klee](https://github.com/fontworks-fonts/Klee) (`8b05327`) and verifies its SHA-256 before use. `sources/glyphs/` holds the historical outlines as SVG in a 1000-unit em, y down, em top at y=880. `check.py` shapes the built fonts with HarfBuzz: default glyphs, every feature in both writing directions, mark composition, small-kana vertical origins, and byte identity of every Klee One glyph in the full font. `specimen/index.html` shows the result. `site/` holds the specimen site and CDN at kureedo.mkpo.li; `site/README.md` describes how a release is published there.

## Licence

The fonts are licensed under the SIL Open Font License 1.1 (`OFL.txt`). Klee One is Copyright 2020 The Klee Project Authors; Klee is a trademark of Fontworks Inc., and Kureedo is an independent derivative with no connection to Fontworks. The historical outlines and the scripts in this repository are Copyright 2026 The Kureedo Project Authors; the scripts are released under the MIT License (`LICENSE-scripts.txt`).

## Author

まくぽり / mkpoli — https://mkpo.li
