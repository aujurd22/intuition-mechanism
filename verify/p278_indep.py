# -*- coding: utf-8 -*-
"""Independent recompute for P278 — deliberately does NOT import
p278_robust_template.py (no shared code with the estimator under test).

Recomputes, for every row in out/p278/p278_raw.json: the centre-template
disparity and the disparities at the same 3x3 grid positions, using a from-
scratch NCC matcher, then compares against the stored values.

Exit 0 iff max |diff| <= 1 px on every position.

Run:  python verify/p278_indep.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, "out", "p278", "p278_raw.json")
IMAGES = os.path.join(REPO, "out", "p277")
W_RESIZE, HALF, MAX_DISP = 1100, 40, 520
FRACTIONS = (0.25, 0.50, 0.75)
TOL = 1.0


def gray(scene, view):
    sub = os.path.join(IMAGES, scene, "Illum2Exp1", view + ".png")
    root = os.path.join(IMAGES, scene, view + ".png")
    im = Image.open(sub if os.path.exists(sub) else root).convert("L")
    im = im.resize((W_RESIZE, round(im.height * W_RESIZE / im.width)), Image.LANCZOS)
    return np.asarray(im, dtype=float)


def ncc_at(lft, rgt, cx, cy):
    y0, y1 = max(0, cy - HALF), min(lft.shape[0], cy + HALF)
    x0, x1 = max(0, cx - HALF), min(lft.shape[1], cx + HALF)
    if y1 - y0 < 20 or x1 - x0 < 20:
        return None
    patch = lft[y0:y1, x0:x1]
    patch = patch - patch.mean()
    norm = np.sqrt((patch ** 2).sum()) + 1e-9
    best_d, best_r = None, -2.0
    for d in list(range(-40, min(MAX_DISP, x0) + 1, 2)):
        if x0 - d < 0 or x1 - d > rgt.shape[1]:
            continue
        cand = rgt[y0:y1, x0 - d:x1 - d]
        cand = cand - cand.mean()
        r = float((patch * cand).sum() / (norm * np.sqrt((cand ** 2).sum()) + 1e-9))
        if r > best_r:
            best_r, best_d = r, d
    for d in range(max(best_d - 3, -40), min(best_d + 4, x0 + 1)):
        if x0 - d < 0 or x1 - d > rgt.shape[1]:
            continue
        cand = rgt[y0:y1, x0 - d:x1 - d]
        cand = cand - cand.mean()
        r = float((patch * cand).sum() / (norm * np.sqrt((cand ** 2).sum()) + 1e-9))
        if r > best_r:
            best_r, best_d = r, d
    return best_d


def main():
    rows = json.load(open(RAW, encoding="utf-8"))
    cache = {}
    worst = 0.0
    checked = 0
    problems = []
    for row in rows:
        scene = row["scene"]
        if scene not in cache:
            cache[scene] = (gray(scene, "view1"), gray(scene, "view5"))
        lft, rgt = cache[scene]
        x1, y1, x2, y2 = [int(v) for v in row["bboxL"]]
        cxc, cyc = (x1 + x2) // 2, (y1 + y2) // 2
        got_centre = ncc_at(lft, rgt, cxc, cyc)
        worst = max(worst, abs(got_centre - row["disp_centre"]))
        checked += 1
        want = {(round(t["fx"], 2), round(t["fy"], 2)): t["disp"]
                for t in row["templates"]}
        for fx in FRACTIONS:
            for fy in FRACTIONS:
                key = (round(fx, 2), round(fy, 2))
                if key not in want:
                    continue
                cx = int(round(x1 + fx * (x2 - x1)))
                cy = int(round(y1 + fy * (y2 - y1)))
                if not (cx - HALF >= x1 and cx + HALF <= x2
                        and cy - HALF >= y1 and cy + HALF <= y2):
                    continue
                got = ncc_at(lft, rgt, cx, cy)
                diff = abs(got - want[key])
                worst = max(worst, diff)
                checked += 1
                if diff > TOL:
                    problems.append((scene, row["obj"][:20], key, want[key], got))
    print(f"positions checked: {checked}, max |diff| = {worst} px (tolerance {TOL})")
    for p in problems:
        print("  MISMATCH", p)
    sys.exit(0 if (not problems and worst <= TOL) else 1)


if __name__ == "__main__":
    main()
