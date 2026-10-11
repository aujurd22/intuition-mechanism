# -*- coding: utf-8 -*-
"""P277 verdict: three pre-registered predictions on the real-stereo rows."""
import json
import sys

import numpy as np

sys.path.insert(0, ".")
from p275_spatial_harness import perm_p


def main():
    rows = json.load(open("out/p277/p277_raw.json", encoding="utf-8"))
    sl = [r for r in rows if r["arm"] == "SL"]
    di = [r for r in rows if r["arm"] == "Direct"]
    # pair by (scene, obj)
    sl_m = {(r["scene"], r["obj"]): r for r in sl}
    di_m = {(r["scene"], r["obj"]): r for r in di}
    keys = [k for k in sl_m if k in di_m
            and sl_m[k].get("rel_err") is not None
            and di_m[k].get("rel_err") is not None]
    e_sl = [sl_m[k]["rel_err"] for k in keys]
    e_di = [di_m[k]["rel_err"] for k in keys]
    diffs = [d - s for s, d in zip(e_sl, e_di)]
    p1 = perm_p(diffs)
    med_sl = float(np.median(e_sl)) if e_sl else float("nan")
    med_di = float(np.median(e_di)) if e_di else float("nan")

    signed = [r["signed_err"] for r in di if r.get("signed_err") is not None]
    # two-sided test: H0 median signed error = 0 (perm_p above is one-sided
    # positive-direction; a negative bias needs the absolute-value null)
    s = np.asarray([x for x in signed if not np.isnan(x)])
    rng = np.random.default_rng(11)
    obs = float(np.median(s))
    null = np.median(rng.choice((-1.0, 1.0), size=(20000, len(s))) * s, axis=1)
    p2_p = float((np.abs(null) >= abs(obs)).mean())
    med_signed = obs

    sl_bad = [r for r in sl if not r.get("pass_")]
    mech = {"bbox_parse", "bbox_bad_bbox", "bbox_out_of_range", "bbox_edge_clipped",
            "degenerate_disp"}
    sl_attributed = sum(1 for r in sl_bad if r.get("attribution") in mech)
    di_bad = [r for r in di if not r.get("pass_")]

    verdict = {
        "id": "P277", "n_objects": len(rows) // 2, "n_paired": len(keys),
        "predictions": [
            {"id": "P-real-1",
             "verdict": "PASS" if (med_sl < 0.15 and p1 < 0.05) else "FAIL",
             "sl_median_rel_err": round(med_sl, 4),
             "direct_median_rel_err": round(med_di, 4),
             "paired_perm_p": round(p1, 5),
             "sl_rel_errs": [round(e, 3) for e in e_sl],
             "direct_rel_errs": [round(e, 3) for e in e_di]},
            {"id": "P-real-2",
             "verdict": "PASS" if (abs(med_signed) > 0.10 and p2_p < 0.05) else "FAIL",
             "direct_signed_median": round(med_signed, 4),
             "perm_p_two_idea_zero": round(p2_p, 5),
             "signed_errs": [round(s, 3) for s in signed]},
            {"id": "P-real-3",
             "verdict": "PASS" if (not sl_bad or sl_attributed == len(sl_bad)) else "FAIL",
             "sl_failures": len(sl_bad), "sl_attributed_mechanical": sl_attributed,
             "sl_attributions": [r.get("attribution") for r in sl_bad],
             "direct_failures": len(di_bad)},
        ],
    }
    verdict["overall"] = ("PASS" if all(p["verdict"] == "PASS"
                                        for p in verdict["predictions"]) else "MIXED")
    json.dump(verdict, open("p277_verdict.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(verdict, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
