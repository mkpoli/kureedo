# Kureedo（クレード）

Klee One with the letterforms of Edo-period Japanese print. It covers two katakana that woodblock editions used and modern fonts lack: a ネ written like 子 and a ヰ written like 井. Unicode 18.0 encodes them as 𛄧 U+1B127 KATAKANA LETTER ALTERNATE NE and 𛄨 U+1B128 KATAKANA LETTER ALTERNATE WI, and the font covers those code points; the same glyphs are also OpenType alternates of ネ and ヰ, so a text encoded with the ordinary letters can show the historical forms through a feature.

![Unicode 18.0 encodes 𛄧 U+1B127 and 𛄨 U+1B128](docs/images/unicode18-card.png)

![ネ and ヰ: default, hist, cv01, cv02](docs/images/forms.png)

Two fonts come out of one build:

| Font | File | Use |
|---|---|---|
| Kureedo | `Kureedo-Regular.ttf` | Desktop. The whole of Klee One Regular plus the historical glyphs and features. |
| Kureedo Kata | `KureedoKata-Regular.woff2`, `.ttf` | Web. Kana, kana punctuation and marks only (about 22 KB). Pair it with Klee One or another Japanese font for kanji and Latin. |

Download both from the [releases page](https://github.com/mkpoli/kureedo/releases).

## Using the historical forms

```css
@font-face {
  font-family: "Kureedo Kata";
  src: url("KureedoKata-Regular.woff2") format("woff2");
  unicode-range: U+3000-303F, U+3099-309C, U+30A0-30FF, U+31F0-31FF;
}
.edition { font-family: "Kureedo Kata", "Klee One", serif; font-feature-settings: "hist"; }
```

Text encoded with the Kana Extended-A letters needs no feature. For text encoded with ordinary ネ and ヰ — which keeps search, sorting and copying working in software that has never heard of U+1B127 — the features below select the same glyphs.

| Feature | Effect |
|---|---|
| `hist` | All historical forms. |
| `ss01` | Edo-period printed forms. In this release the same set as `hist`. |
| `cv01` | ネ only. |
| `cv02` | ヰ only. |

![Running text with and without hist](docs/images/running.png)

![Vertical text with and without hist](docs/images/vertical.png)

Klee One's own `hkna`/`vkna` alternates of ネ and ヰ also become the historical forms when a historical feature is on. In the full font, `hwid` and `ruby` keep Klee One's shapes and `aalt` lists the historical forms; Kureedo Kata carries none of those three features. Word processors list the character variants under their feature names; the fonts carry English and Japanese names.

## Coverage of Kureedo Kata

The subset requests U+0020, U+3000–303F, U+3099–309C, U+30A0–30FF and U+31F0–31FF; code points Klee One does not cover (for example U+3031–3032, U+30A0, U+30FF) stay absent. `fonttools ttx -t cmap` lists the exact set. The two historical glyphs are unencoded alternates. Glyphs Klee One does not have and this font adds: the Ainu small kana ㇰ–ㇿ (U+31F0–31FF), set the way Klee sets its own small kana (78% of the full-size letter, centred on the baseline, stroke weight restored, shifted up and right in vertical text through `vert`); combining ゛ and ゜ with zero advance; and `ccmp` ligatures that set セ゚ ツ゚ ト゚ ㇷ゚ カ゚ キ゚ ク゚ ケ゚ コ゚ in one cell, horizontally and vertically. The handakuten of ㇷ゚ is scaled with the letter and sits where プ puts its own, at プ's clearance from the stroke; the placement was settled by comparison rounds (`docs/methods.md`).

![Ainu small kana and composed marks](docs/images/ainu.png)

## Sources of the forms

**ネ from 子.** The Edo-period printed katakana ネ keeps the shape of its source character 子: an angular upper turn, a sloping crossbar, an upright stem and a short curved hook. Reference specimen: 上原熊次郎『蝦夷方言藻汐草』(1792), volume 2, [image 81](https://dglb01.ninjal.ac.jp/iiif/ezomosio/002/tiff/ezmg002-081.tiff/full/1495,/0/default.jpg) (国立国語研究所, CC BY 4.0), with the [292 ネ samples](https://codh.rois.ac.jp/char-shape/unicode/U%2B30CD/) in CODH's kuzushiji index (日本古典籍くずし字データセット, 国文研ほか所蔵／CODH加工, doi:10.20676/00000340, CC BY-SA 4.0) as the wider comparison.

**ヰ from 井.** The printed ヰ of the same editions keeps the full 井 frame. Eiso Chan, *Proposal on two archaic Katakana letters*, [L2/25-151](https://www.unicode.org/L2/L2025/25151-katakana-ne-wi.pdf) (2025-05-23), page 1 and section 3, collects historical specimens of both letters; the UTC accepted it at meeting 184 and Unicode 18.0 encodes the two letters in [Kana Extended-A](https://www.unicode.org/charts/PDF/Unicode-18.0/U180-1B100.pdf) under the heading Historic Katakana. They are separate letters from 子 U+5B50 and 井 U+4E95, and have no decomposition to ネ or ヰ.

The 0.2 outline keeps Klee's uprights and stroke ends and sets the bars 50 units closer, the upper 30 and the lower 60 units longer; it beat the 0.1 outline and the other finalists in blind comparison. `docs/methods.md` describes how each form was chosen and `docs/votes/` holds the comparison records.

## Building

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python scripts/check.py
```

The build downloads Klee One Regular from the pinned commit of [fontworks-fonts/Klee](https://github.com/fontworks-fonts/Klee) (`8b05327`) and verifies its SHA-256 before use. `sources/glyphs/` holds the historical outlines as SVG in a 1000-unit em, y down, em top at y=880. `check.py` shapes the built fonts with HarfBuzz: default glyphs, every feature in both writing directions, mark composition, small-kana vertical origins, and byte identity of every Klee One glyph in the full font. `specimen/index.html` shows the result.

## Licence

The fonts are licensed under the SIL Open Font License 1.1 (`OFL.txt`). Klee One is Copyright 2020 The Klee Project Authors; Klee is a trademark of Fontworks Inc., and Kureedo is an independent derivative with no connection to Fontworks. The historical outlines and the scripts in this repository are Copyright 2026 The Kureedo Project Authors; the scripts are released under the MIT License (`LICENSE-scripts.txt`).
