# Weight matching of imported ideographs

Kureedo keeps Klee One's ideographs and imports the code points Klee lacks from
LXGW WenKai Light 1.530. WenKai is based on Klee SemiBold, and its added
simplified glyphs were cut from SemiBold strokes, scaled and thickened or
thinned by hand. They land heavier than Klee's drawings: on 1,773
simplified/traditional pairs from OpenCC, the median area/perimeter stroke width
is 1.065× Klee's, and 94% are thicker. Complexity explains part of that. After
fitting thickness to ink area on Klee's own ideographs, the imported set still
sits 3.0% above the model, and 29% of it is above Klee's 90th percentile.

The Full edition therefore erodes each imported ideograph to the thickness
Klee's density model predicts before the merge.

## Method

For every imported unified or compatibility ideograph:

1. Measure mean stroke thickness as `2 × ink area / outline perimeter`, and ink
   area, with `fontTools` pens.
2. Fit Klee's thickness against ink area: a least-squares line through
   `log(thickness)` and `log(area)` on Klee's 8,147 ideographs. Thinner strokes
   go with fuller glyphs.
3. The target is `exp(intercept + slope × log(area))`.
4. The erosion radius is `(measured − target) / 2`, capped at 4 units. Below
   0.2 units the outline stays as the donor drew it.
5. Erode by subtracting a stroke of the outline at twice the radius from the
   filled shape (`skia-pathops`). The contour count must not grow, so counters
   and separate strokes survive.
6. Keep the horizontal advance and the vertical origin. Left side bearing and
   top side bearing follow the new bounds.

Glyphs shared with a non-ideograph code point are skipped. Simple Hangul,
Latin, punctuation and symbols stay exactly as the donor drew them; 23 of the
13,896 imported non-ideographs are composite radicals that reuse an ideograph
component, and they follow that component's new weight.

## Result

| Measurement | Before | After |
| --- | ---: | ---: |
| Changed ideographs, median thickness / model | 1.060 | 1.002 |
| Changed ideographs, 90th percentile / model | 1.126 | 1.019 |
| Paired simplified/traditional median | 1.065 | 1.023 |
| Full TTF | 31.4 MB | 35.1 MB |
| Full WOFF2 | 10.7 MB | 12.5 MB |

The paired measurement uses the same 1,773 OpenCC pairs before and after. It
does not reach 1.000 because Klee's density model asks simpler characters to
carry a little more weight than their fuller traditional counterparts; the model
residual is the direct target. The model figures are measured on the merged font
against the model fitted on the Japanese base.

## Limits

This pass changes weight only. It does not repair component proportions or
stiff joins in the assembled simplified glyphs; recomposition from Klee
components is the next pass. The 4-unit cap leaves the boldest outliers such as
书 bolder than the model. Light glyphs are not thickened. Erosion softens
corners slightly and adds outline points, which accounts for the larger files.

## Reproduce

```sh
.venv/bin/python scripts/build.py
.venv/bin/python scripts/check_editions.py
```

`check_editions.py` re-erodes sampled donor outlines and compares them with the
built font, then checks the changed ideographs' thickness distribution against
Klee's model.
