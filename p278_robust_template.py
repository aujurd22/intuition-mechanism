# -*- coding: utf-8 -*-
"""P278: robust disparity by template aggregation (3x3 grid, median).

Reads P277's recorded VLM bboxes and images; recomputes disparity with (a) the
P277 centre template (reproduction gate) and (b) nine templates on a 3x3 grid
inside the same bbox, aggregated by median.  No model calls: only the template
policy varies.  Frozen design: p278_preregistration.json.

Run:  python p278_robust_template.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image

DATA = "out/p277"
OUT = "out/p278"
TARGET_W = 1100
B_M = 0.160
ORIG_W = 3072
HALF = 40
MAX_DISP = 520
GRID = (0.25, 0.50, 0.75)


def load_view(scene, view):
    sub = f"{DATA}/{scene}/Illum2Exp1/{view}.png"
    root = f"{DATA}/{scene}/{view}.png"
    path = sub if os.path.exists(sub) else root
    im = Image.open(path).convert("RGB")
    r = TARGET_W / im.width
    im2 = im.resize((TARGET_W, round(im.height * r)), Image.LANCZOS)
    return im2


def match_disp(gL, gR, cx, cy, half=HALF, max_disp=MAX_DISP):
    """Identical to p277_real_stereo.match_disparity, but at an explicit centre."""
    ty0, ty1 = max(0, cy - half), min(gL.shape[0], cy + half)
    tx0, tx1 = max(0, cx - half), min(gL.shape[1], cx + half)
    if ty1 - ty0 < 20 or tx1 - tx0 < 20:
        return None, 0.0
    T = gL[ty0:ty1, tx0:tx1]
    Tz = T - T.mean()
    tnorm = np.sqrt((Tz ** 2).sum()) + 1e-9
    best_d, best_n = None, -2.0
    for d in range(-40, min(max_disp, tx0) + 1, 2):
        if tx0 - d < 0 or tx1 - d > gR.shape[1]:
            continue
        P = gR[ty0:ty1, tx0 - d:tx1 - d]
        Pz = P - P.mean()
        ncc = float((Tz * Pz).sum() / (tnorm * np.sqrt((Pz ** 2).sum()) + 1e-9))
        if ncc > best_n:
            best_n, best_d = ncc, d
    if best_d is None:
        return None, best_n
    for d in range(max(best_d - 3, -40), min(best_d + 4, tx0 + 1)):
        if tx0 - d < 0 or tx1 - d > gR.shape[1]:
            continue
        P = gR[ty0:ty1, tx0 - d:tx1 - d]
        Pz = P - P.mean()
        ncc = float((Tz * Pz).sum() / (tnorm * np.sqrt((Pz ** 2).sum()) + 1e-9))
        if ncc > best_n:
            best_n, best_d = ncc, d
    return best_d, best_n


def candidates(bbox, half=HALF):
    x1, y1, x2, y2 = [int(v) for v in bbox]
    out = []
    for fx in GRID:
        for fy in GRID:
            cx = int(round(x1 + fx * (x2 - x1)))
            cy = int(round(y1 + fy * (y2 - y1)))
            if (cx - half >= x1 and cx + half <= x2
                    and cy - half >= y1 and cy + half <= y2):
                out.append((fx, fy, cx, cy))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = json.load(open(f"{DATA}/p277_raw.json", encoding="utf-8"))
    cohort = [r for r in rows if r["arm"] == "SL"
              and r.get("bboxL") and r.get("rel_err") is not None]
    raw, cache = [], {}
    for i, r in enumerate(cohort, 1):
        scene, obj = r["scene"], r["obj"]
        if scene not in cache:
            im1, im2 = load_view(scene, "view1"), load_view(scene, "view5")
            cache[scene] = (np.array(im1.convert("L"), dtype=float),
                            np.array(im2.convert("L"), dtype=float),
                            im1.width)
        gL, gR, W = cache[scene]
        f_full = 3740.0 * W / ORIG_W
        bbox = r["bboxL"]
        x1, y1, x2, y2 = [int(v) for v in bbox]
        cx_c, cy_c = (x1 + x2) // 2, (y1 + y2) // 2

        # (a) reproduction: centre template exactly as P277
        d_c, ncc_c = match_disp(gL, gR, cx_c, cy_c)

        # (b) 3x3 grid
        cand = candidates(bbox)
        if not cand:
            # PRE-REGISTRATION GAP (declared in the verdict): bbox too small to
            # hold an 80x80 window at any grid point -> fall back to P277's own
            # estimator (median == centre), no threshold is touched.
            grid = [(0.5, 0.5, cx_c, cy_c)]
            fallback = True
        else:
            grid = cand
            fallback = False
        ds = []
        for fx, fy, cx, cy in grid:
            d, n = match_disp(gL, gR, cx, cy)
            if d is not None:
                ds.append({"fx": fx, "fy": fy, "cx": cx, "cy": cy,
                           "disp": int(d), "ncc": round(float(n), 3)})
        vals = [d["disp"] for d in ds]
        med = float(np.median(vals)) if vals else None
        mad = (float(np.median(np.abs(np.asarray(vals) - med)))
               if vals else None)
        z_gt = r["Z_gt"]
        z_c = (f_full * B_M / d_c) if (d_c and d_c > 5) else None
        z_m = (f_full * B_M / med) if (med and med > 5) else None
        raw.append({
            "scene": scene, "obj": obj, "bboxL": bbox,
            "z_gt": z_gt, "f_full": round(f_full, 2),
            "disp_recorded": r.get("disp_px"),
            "disp_centre": None if d_c is None else int(d_c),
            "ncc_centre": round(float(ncc_c), 3),
            "grid_n": len(vals), "grid_fallback": fallback,
            "templates": ds,
            "disp_median": med, "mad": mad,
            "z_centre": None if z_c is None else round(z_c, 4),
            "z_median": None if z_m is None else round(z_m, 4),
            "rel_centre": round(abs(z_c - z_gt) / z_gt, 4) if z_c else None,
            "rel_median": round(abs(z_m - z_gt) / z_gt, 4) if z_m else None,
            "was_p277_failure": not bool(r.get("pass_")),
        })
        print(f"[{i:2d}/{len(cohort)}] {scene:11s} {obj[:28]:28s} "
              f"rec {r.get('disp_px')} c {d_c} med {med} rel_c "
              f"{raw[-1]['rel_centre']} rel_m {raw[-1]['rel_median']}", flush=True)

    json.dump(raw, open(f"{OUT}/p278_raw.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("saved", f"{OUT}/p278_raw.json", "rows", len(raw))


if __name__ == "__main__":
    main()
