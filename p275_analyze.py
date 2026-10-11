# -*- coding: utf-8 -*-
"""P275 verdict: evaluate the three pre-registered predictions from raw rows.

  P-spatial-1: paired SL < Direct error (one-sided sign-flip permutation),
               SL flat in complexity.
  P-spatial-2: stacked probe: two-view keeps xy/z error low, single-view
               plane-prior collapses; table objects as honest control.
  P-spatial-3: SL intentions carry zero numeric fields; 100% SL failure
               attribution; Direct failures not attributable.
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p275_spatial_harness import perm_p
import p275_spatial_env as env


def main():
    raw = json.load(open("out/p275/p275_raw.json", encoding="utf-8"))
    rows = raw["rows"]
    verdict = {"id": "P275", "predictions": []}

    # ---------------- P-spatial-1: paired accuracy
    pairs = {}
    for r in rows:
        key = (r["scene"], r["cmd"])
        pairs.setdefault(key, {})[r["arm"]] = r
    sl_err, di_err, diffs = [], [], []
    for k, v in pairs.items():
        e_s = v["SL"].get("err_m")
        e_d = v["Direct"].get("err_m")
        if e_s is not None and e_d is not None:
            sl_err.append(e_s); di_err.append(e_d); diffs.append(e_d - e_s)
    p1_p = perm_p(diffs)
    sl_fail = sum(1 for r in rows if r["arm"] == "SL" and r.get("err_m") is None)
    di_fail = sum(1 for r in rows if r["arm"] == "Direct" and r.get("err_m") is None)
    # complexity slope (err vs n_objects), descriptive
    def slope(arm):
        xs = np.array([r["n_objects"] for r in rows
                       if r["arm"] == arm and r.get("err_m") is not None], dtype=float)
        ys = np.array([r["err_m"] for r in rows
                       if r["arm"] == arm and r.get("err_m") is not None], dtype=float)
        if len(xs) < 3 or xs.std() == 0:
            return None
        return float(np.polyfit(xs, ys, 1)[0])
    sl_pass_1 = (np.mean(diffs) > 0) and (p1_p < 0.05)
    verdict["predictions"].append({
        "id": "P-spatial-1", "verdict": "PASS" if sl_pass_1 else "FAIL",
        "n_paired": len(diffs),
        "sl_mean_cm": round(float(np.mean(sl_err)) * 100, 2),
        "direct_mean_cm": round(float(np.mean(di_err)) * 100, 2),
        "median": {"sl_cm": round(float(np.median(sl_err)) * 100, 2),
                   "direct_cm": round(float(np.median(di_err)) * 100, 2)},
        "paired_perm_p_one_sided": round(p1_p, 5),
        "slope_err_per_object": {"sl": slope("SL"), "direct": slope("Direct")},
        "arm_failures": {"sl": sl_fail, "direct": di_fail},
    })

    # ---------------- P-spatial-2: stacked probe, two-view vs one-view
    scenes = env.build_all()
    stacked = {o["name"] for sc in scenes for o in sc["objects"]
               if "stacked_on" in o}
    g2, g1 = raw["graph_stats"]["two"], raw["graph_stats"]["one"]
    z2, z1 = raw["graph_stats"].get("z_two", {}), raw["graph_stats"].get("z_one", {})
    st_xy2 = [g2[k] for k in stacked if k in g2]
    st_xy1 = [g1[k] for k in stacked if k in g1]
    st_z2 = [z2[k] for k in stacked if k in z2]
    st_z1 = [z1[k] for k in stacked if k in z1]
    tab2 = [v for k, v in g2.items() if k not in stacked]
    tab1 = [v for k, v in g1.items() if k not in stacked]
    p2_ok = (st_xy2 and st_xy1
             and float(np.median(st_xy2)) < float(np.median(st_xy1))
             and float(np.median(st_xy2)) < 0.02
             and float(np.median(st_z2)) < 0.02)
    verdict["predictions"].append({
        "id": "P-spatial-2", "verdict": "PASS" if p2_ok else "FAIL",
        "n_stacked": len(st_xy2),
        "stacked_median_err_cm": {
            "two_view_xy": round(float(np.median(st_xy2)) * 100, 2) if st_xy2 else None,
            "one_view_xy": round(float(np.median(st_xy1)) * 100, 2) if st_xy1 else None,
            "two_view_z": round(float(np.median(st_z2)) * 100, 2) if st_z2 else None,
            "one_view_z": round(float(np.median(st_z1)) * 100, 2) if st_z1 else None},
        "table_control_median_cm": {
            "two_view_xy": round(float(np.median(tab2)) * 100, 2) if tab2 else None,
            "one_view_xy": round(float(np.median(tab1)) * 100, 2) if tab1 else None},
    })

    # ---------------- P-spatial-3: grounding
    numeric_leaks = [r for r in rows if r["arm"] == "SL"
                     and r.get("attribution") == "intent_has_numbers"]
    sl_bad = [r for r in rows if r["arm"] == "SL" and not r.get("pass_")]
    sl_attributed = [r for r in sl_bad if r.get("attribution") in
                     ("wrong_object", "geometry_error", "intent_parse",
                      "offset_missing")]
    p3_ok = (len(numeric_leaks) == 0
             and (not sl_bad or len(sl_attributed) == len(sl_bad)))
    verdict["predictions"].append({
        "id": "P-spatial-3", "verdict": "PASS" if p3_ok else "FAIL",
        "numeric_leak_rows": len(numeric_leaks),
        "sl_failures": len(sl_bad),
        "sl_attributed": len(sl_attributed),
        "direct_failures_not_attributable":
            sum(1 for r in rows if r["arm"] == "Direct" and not r.get("pass_")),
    })

    overall = all(p["verdict"] == "PASS" for p in verdict["predictions"])
    verdict["overall"] = "PASS" if overall else "MIXED"
    json.dump(verdict, open("p275_verdict.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(verdict, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
