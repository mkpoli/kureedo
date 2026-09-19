# How the forms were chosen

Since Unicode 18.0 the two letters have their own code points, 𛄧 U+1B127 and 𛄨 U+1B128 in Kana Extended-A. The font covers them and keeps the same glyphs reachable from ネ and ヰ through `hist`; which encoding a text uses is the text's decision, not the font's.


Each historical glyph is drawn from Klee One's own strokes so that it sits beside Klee's kana at reading size, then chosen among candidates by blind pairwise comparison. The comparisons say which candidate one reader prefers in running text; the historical sources named in the README say what the letter looked like. The two kinds of evidence are kept apart.

## Comparison protocol

- Candidates are built as separate fonts differing only in the glyph under study. Each carries a random identifier; the designer's construction notes are sealed until a round ends.
- A comparison shows two candidates side by side in the same passage of Moshiogusa transcription, horizontal and vertical text together, at 24 px. The options are A, B, tie, and neither. Sides and passages are shuffled; some pairs repeat with sides reversed.
- One judge (the project owner) records every vote. The records in `votes/` are that judge's ballots; they measure one reader's preference, not agreement among readers.
- Ranking counts one point per win and half a point per tie, excluding repeat judgments.
- From the fifth ネ round on, a regularized preference model (a Davidson model with a separate "neither" outcome, fitted to rasterized outlines) screened weak candidates before a round and proposed the next pairs. Its predictions were never shown while voting, and the final choice in every round rests on the recorded votes, not on the model.

## ネ

Six rounds. The first fixed stroke weight against Klee's own kana; the middle rounds varied the length ratio of the horizontals, the height of the crossbar, the centre of gravity, the shape and length of the hook, and the central white space. Very small variations were hard to judge and forms that changed the basic shape were rejected; the productive range kept the shape and curvature and exchanged native stroke parts and their positions.

The final round (`votes/ne/arena6-judgments-71.json`, 16 candidates, 71 judgments) ended with candidate `ffcd7b08b3cea47d5`: seven wins, one loss and two ties in ten non-repeat finalist comparisons (`votes/ne/arena6-decision.json`). Its outline is `sources/glyphs/ne.svg`; the other fifteen are in `votes/ne/arena6-candidates.svg`.

## ヰ

Eleven rounds. The first four built and screened the frame (records below); the released 0.1 glyph was the leader of round 4. Rounds 5–11 refined it on the same four strokes, varying only the geometry of the two bars and, briefly, the frame.

1. Ten forms assembled from Klee stroke components on the 井 frame. Set aside after a printed proof: the printed sources suggested starting from Klee's own ヰ instead.
2. Ten forms starting from Klee's own ヰ, varying only the left stroke. Rejected: the two horizontal bars sat too far apart.
3. Spacing study: eight forms that close the gap between the bars by increasing amounts, everything else fixed (`votes/wi/spacing-study-31.json`, `votes/wi/spacing-candidates.svg`).
4. Component study: 24 forms varying bar length, vertical placement, horizontal offsets and upright spacing (`votes/wi/component-screening-54.json`, `votes/wi/component-candidates.svg`, `votes/wi/shortlist-batch-29.json`). Its leader (bars 60 units closer than Klee's, lower bar 110 units longer) shipped as 0.1.
5. Compression towards the printed proportions — shorter uprights, level bars, tighter gap. Rejected outright: 37 of 42 judgments "neither", the five decisive ones all for the unchanged 0.1 outline (`round5-*`).
6. The two bars alone, 18 forms (`round6-*`): forms whose bars differ less in length than 0.1's led; opposite horizontal offsets lost every comparison.
7. A directed block of 14 named contrasts (`round7-*`): the bars' native length difference beat both a smaller and a larger one; moderate combined length beat long; a wider gap (30 closer than Klee) beat 60 closer, which beat 90.
8. Gap bracket (`round8-*`): Klee's own spacing lost twice; 30 and 60 closer were not separable; raising the bars was rejected.
9. Set aside unjudged.
10. A Latin-hypercube sample of 24 forms over the eight parameters plus two anchors, 58 judgments (`round10-*`). A Davidson preference model with a separate rejection term, fitted on rounds 6–8 and 10 (106 judgments, five folds grouped by pair), predicted the preferred side in 44 of 65 held-out decisive choices; it favoured raised bars, a moderate gap and a shorter lower bar (`parameter-model.json`).
11. Confirmation (`round11-*`): the model's optimum with its bars raised lost to 0.1, while the same form unraised beat 0.1 and tied or beat the round-7 winner.

The 0.2 glyph is that unraised form (`w62de2d979979dc14`): upper bar 30 units longer and lower bar 60 units longer than Klee's, bars 50 units closer, uprights and stroke ends unchanged. Each round's ballots, design parameters and candidate outlines are in `votes/wi/`; every candidate id resolves to its outline in the matching `-candidates.svg`.
