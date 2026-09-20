"""Derive sources/glyphs/mark-positions.json: where the combining handakuten sits on the
full-size bases Klee One does not voice with it (カ キ ク ケ コ セ ツ ト).

Rule: start from where Klee places the dakuten on the same base (ガ ギ グ ゲ ゴ ゼ ヅ ド),
move by the mean offset between Klee's own handakuten and dakuten on ハ ヒ フ ヘ ホ, then push
the ring straight away from its nearest point on the letter until it has プ's clearance
(24 units). Offsets are relative to the mark glyph's own position (sources/glyphs/mark-309a.svg).
Run from the repository root: .venv/bin/python scripts/mark_positions.py
"""
import json, math
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen

import build

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sources/glyphs/mark-positions.json"
CLEARANCE = 24                       # measured on Klee's プ
TARGETS = {"カ": "ガ", "キ": "ギ", "ク": "グ", "ケ": "ゲ", "コ": "ゴ", "セ": "ゼ", "ツ": "ヅ", "ト": "ド"}
REFERENCE = {"ハ": ("バ", "パ"), "ヒ": ("ビ", "ピ"), "フ": ("ブ", "プ"), "ヘ": ("ベ", "ペ"), "ホ": ("ボ", "ポ")}


def flatten(recording, n=8):
    pts, cur = [], None
    for op, args in recording:
        if op in ("moveTo", "lineTo"):
            cur = args[0]; pts.append(cur)
        elif op == "qCurveTo":
            offs, on = list(args[:-1]), args[-1]
            for i, off in enumerate(offs):
                nxt = on if i == len(offs) - 1 else ((off[0] + offs[i + 1][0]) / 2, (off[1] + offs[i + 1][1]) / 2)
                pts += [((1 - t) ** 2 * cur[0] + 2 * (1 - t) * t * off[0] + t * t * nxt[0], (1 - t) ** 2 * cur[1] + 2 * (1 - t) * t * off[1] + t * t * nxt[1]) for t in (k / n for k in range(1, n + 1))]
                cur = nxt
    return pts


def contours(glyph_set, name):
    pen = DecomposingRecordingPen(glyph_set); glyph_set[name].draw(pen)
    result, cur = [], []
    for op, args in pen.value:
        if op == "moveTo": cur = [args[0]]
        elif op in ("lineTo", "qCurveTo", "curveTo"): cur += [a for a in args if a]
        elif op in ("closePath", "endPath"): result.append(cur); cur = []
    return result


def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def mark_centre(glyph_set, cmap, base, marked):
    """Centre of the mark's contours in a precomposed voiced kana: the contours absent from the base."""
    base_boxes = [bbox(c) for c in contours(glyph_set, cmap[ord(base)])]
    marks = [c for c in contours(glyph_set, cmap[ord(marked)]) if not any(all(abs(x - y) <= 3 for x, y in zip(bbox(c), b)) for b in base_boxes)]
    assert len(marks) == 2, (marked, len(marks))
    m = bbox([p for c in marks for p in c])
    return (m[0] + m[2]) / 2, (m[1] + m[3]) / 2


def main():
    klee = build.fetch_klee(); gs = klee.getGlyphSet(); cmap = klee.getBestCmap()
    shifts = []
    for base, (voiced, semi) in REFERENCE.items():
        d, h = mark_centre(gs, cmap, base, voiced), mark_centre(gs, cmap, base, semi)
        shifts.append((h[0] - d[0], h[1] - d[1]))
    shift = (sum(s[0] for s in shifts) / len(shifts), sum(s[1] for s in shifts) / len(shifts))
    # the mark glyph as the build places it at (0, 0)
    mark = build.svg_glyph(build.GLYPHS / "mark-309a.svg")
    pen = RecordingPen(); mark.draw(pen, None); mark_pts = flatten(pen.value)
    mb = bbox(mark_pts); mark_c = ((mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2)
    positions = json.loads(OUT.read_text())
    for base, voiced in TARGETS.items():
        cx, cy = mark_centre(gs, cmap, base, voiced)
        dx, dy = cx + shift[0] - mark_c[0], cy + shift[1] - mark_c[1]
        lp = RecordingPen(); gs[cmap[ord(base)]].draw(lp); letter = flatten(lp.value)
        for _ in range(40):
            ring = [(x + dx, y + dy) for x, y in mark_pts]
            d, pb = min(((math.hypot(p[0] - q[0], p[1] - q[1]), q) for p in ring for q in letter), key=lambda t: t[0])
            if d >= CLEARANCE - 0.5: break
            vx, vy = mark_c[0] + dx - pb[0], mark_c[1] + dy - pb[1]; L = math.hypot(vx, vy) or 1
            dx += vx / L * (CLEARANCE - d + 1); dy += vy / L * (CLEARANCE - d + 1)
        positions[base + "゚"] = [round(dx), round(dy)]
        print(f"{base}゚ {positions[base + '゚']}  clearance {d:.0f}")
    OUT.write_text(json.dumps(positions, ensure_ascii=False, indent=2) + "\n")
    print(f"handakuten sits ({shift[0]:+.0f}, {shift[1]:+.0f}) from the dakuten on Klee's ハ–ホ")


if __name__ == "__main__":
    main()
