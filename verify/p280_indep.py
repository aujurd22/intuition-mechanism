# -*- coding: utf-8 -*-
"""Independent recompute for P280 — does NOT import p280_run.py.

Recomputes, for every row in out/p280/p280_raw.json, all 3x3 grid template
disparities with a from-scratch NCC matcher, and compares with the stored values
(tolerance 1 px).

Run:  python verify/p280_indep.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, "out", "p280", "p280_raw.json")
DATA = os.path.join(REPO, "out", "p280", "data")
W_RESIZE, HALF, MAX_DISP, TOL = 1100, 40, 520, 1.0


def gray(scene, view):
    im = Image.open(os.path.join(DATA, scene, view + ".png")).convert("L")
    im = im.resize((W_RESIZE, round(im.height * W_RESIZE / im.width)), Image.LANCZOS)
    return np.asarray(im, dtype=float)


def ncc(lft, rgt, cx, cy):
    y0, y1 = max(0, cy - HALF), min(lft.shape[0], cy + HALF)
    x0, x1 = max(0, cx - HALF), min(lft.shape[1], cx + HALF)
    if y1 - y0 < 20 or x1 - x0 < 20:
        return None
    T = lft[y0:y1, x0:x1]
    T = T - T.mean()
    n = np.sqrt((T ** 2).sum()) + 1e-9
    best = (-2.0, None)
    for d in range(-40, min(MAX_DISP, x0) + 1, 2):
        if x0 - d < 0 or x1 - d > rgt.shape[1]:
            continue
        P = rgt[y0:y1, x0 - d:x1 - d]
        P = P - P.mean()
        r = float((T * P).sum() / (n * np.sqrt((P ** 2).sum()) + 1e-9))
        if r > best[0]:
            best = (r, d)
    for d in range(max(best[1] - 3, -40), min(best[1] + 4, x0 + 1)):
        if x0 - d < 0 or x1 - d > rgt.shape[1]:
            continue
        P = rgt[y0:y1, x0 - d:x1 - d]
        P = P - P.mean()
        r = float((T * P).sum() / (n * np.sqrt((P ** 2).sum()) + 1e-9))
        if r > best[0]:
            best = (r, d)
    return best[1]


def main():
    rows = json.load(open(RAW, encoding="utf-8"))
    cacheH = {}
    worst, checked, problems = 0.0, 0, []
    for r in rows:
        if not r.get("evaluable"):
            continue
        scene = r["scene"]
        if scene not in cacheH:
            cacheH[scene] = (gray(scene, "view1"), gray(scene, "view5"))
        L, R = cacheH[scene]
        x1, y1, x2, y2 = r["bbox"]
        for t in r["templates"]:
            cx = int(round(x1 + t["fx"] * (x2 - x1)))
            cy = int(round(y1 + t["fy"] * (y2 - y1)))
            got = ncc(L, R, cx, cy)
            checked += 1
            if got is None:
                problems.append((scene, r["label"][:20], "None"))
                continue
            diff = abs(got - t["disp"])
            worst = max(worst, diff)
            if diff > TOL:
                problems.append((scene, r["label"][:20], t["disp"], got))
    print(f"templates checked: {checked}, max |diff| = {worst} px (tolerance {TOL})")
    for p in problems:
        print("  MISMATCH", p)
    sys.exit(0 if (not problems and worst <= TOL) else 1)


if __name__ == "__main__":
    main()
