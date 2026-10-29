# 贝 from WenKai's frame and Klee's 丿

贝 U+8D1D is the simplified form of 貝. BabelStone IDS uses it as a leaf in 76
imported ideographs. WenKai's frame and right dot are already close to Klee's
drawing; the long left 丿 is the stroke that differs.

The design keeps WenKai's normalized frame and right dot and replaces only the
left 丿 with Klee's 丿 U+4E3F. The Klee stroke is fitted to the donor 丿's box:
0.916× across and 0.775× down, with the box edges aligned. The resulting glyph
measures 45.3 against Klee's model target of 45.6, a residual of 0.993.

![WenKai's 贝, Klee's 丿 and the designed 贝](images/bei.png)

The frame, the right dot and the 1,000-unit advance stay as WenKai normalized
them. The glyph replaces U+8D1D in Full only through `DESIGNED_IMPORTS`. The
retained radical U+2EC9 is a composite over 贝; its donor outline is preserved
under `u8D1D.donor` and the composite retargeted there, so only U+8D1D's resolved
outline changes. The Full font gains one glyph name; the encoded repertoire is
unchanged.

## Checks

`check_editions.py` compares the built glyph with the SVG, checks its weight,
and verifies the preserved U+2EE5 and U+2EC9 components and their resolved
composites.

## Sources

Klee One Regular and LXGW WenKai Light 1.530 as pinned in this repository.
BabelStone IDS, Andrew West, file date 2025-06-27, SHA-256
`cc2a0a97e6a51ed6ebe59870ef2af66e83f3c3c27387d79b4441bb2d791d78b1`.
