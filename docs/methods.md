# How the forms were chosen

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

Four rounds, the last still open.

1. Ten forms assembled from Klee stroke components on the 井 frame. Set aside after a printed proof: the printed sources suggested starting from Klee's own ヰ instead.
2. Ten forms starting from Klee's own ヰ, varying only the left stroke. Rejected: the two horizontal bars sat too far apart.
3. Spacing study: eight forms that close the gap between the bars by increasing amounts, everything else fixed (`votes/wi/spacing-study-31.json`, `votes/wi/spacing-candidates.svg`). The six non-repeat finalist comparisons gave one decisive choice, two ties and three "neither", so the study did not settle the form.
4. Component study: 24 forms varying bar length, vertical placement, horizontal offsets and upright spacing, with three round-3 finalists as controls (`votes/wi/component-screening-54.json`, `votes/wi/component-candidates.svg`). The preference model then reduced the field to five and scheduled small batches of unseen pairs (`votes/wi/shortlist-batch-29.json`).

The shipped glyph is `w17c3c4a14c32a3ee`: bars 60 units closer than in Klee's ヰ, lower bar 110 units longer, uprights and stroke ends unchanged. Across the screening and the first shortlist batch it has seven wins, no losses and one "neither". Three forms remain under comparison; if another wins, the next release replaces the outline and this page records the result.
