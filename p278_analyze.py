# -*- coding: utf-8 -*-
"""P278 verdict: four pre-registered predictions on the robust-template rows."""
import json

RAW = "out/p278/p278_raw.json"
OUT = "p278_verdict.json"
BAR = 0.15          # identical to P277
SHIFT_BAR = 0.05    # P-tmpl-3


def is_outlier(r):
    if r["disp_centre"] is None or r["disp_median"] is None:
        return None
    if r["mad"] is None:
        return None
    delta = abs(r["disp_centre"] - r["disp_median"])
    if r["mad"] == 0:
        return delta >= 2
    return delta > 3 * r["mad"]


def main():
    rows = json.load(open(RAW, encoding="utf-8"))
    targets = [r for r in rows if r["was_p277_failure"]]
    controls = [r for r in rows if not r["was_p277_failure"]]

    # --- P-tmpl-4: reproduction gate (checked first) ---
    repro = [abs(r["disp_centre"] - r["disp_recorded"]) for r in rows
             if r["disp_centre"] is not None]
    gate = bool(repro) and max(repro) <= 1

    # --- P-tmpl-1: mechanism ---
    out_t = {f"{r['scene']}/{r['obj'][:24]}": is_outlier(r) for r in targets}
    out_c = [r for r in controls if is_outlier(r) is True]
    p1 = bool(out_t) and all(v is True for v in out_t.values()) and len(out_c) <= 1

    # --- P-tmpl-2: fix ---
    fixed = [r for r in targets if r["rel_median"] is not None
             and r["rel_median"] < BAR]
    p2 = len(targets) == 2 and len(fixed) == 2

    # --- P-tmpl-3: no regression ---
    regressed = [r for r in controls
                 if r["rel_median"] is None or r["rel_median"] >= BAR]
    shifted = [r for r in controls
               if r["z_median"] is not None and r["z_centre"] is not None
               and abs(r["z_median"] - r["z_centre"]) / r["z_gt"] > SHIFT_BAR]
    p3 = not regressed and not shifted

    verdict = {
        "id": "P278",
        "n_rows": len(rows), "n_targets": len(targets), "n_controls": len(controls),
        "predictions": [
            {"id": "P-tmpl-4",
             "verdict": "PASS" if gate else "FAIL",
             "note": "reproduction gate: recomputed centre disparity vs P277 recorded",
             "max_abs_px_diff": max(repro) if repro else None,
             "rows_checked": len(repro)},
            {"id": "P-tmpl-1",
             "verdict": "PASS" if p1 else "FAIL",
             "note": "centre template is a >3xMAD outlier inside its own 3x3 grid",
             "target_outliers": out_t,
             "control_outliers": [f"{r['scene']}/{r['obj'][:24]}" for r in out_c],
             "control_outlier_count": len(out_c)},
            {"id": "P-tmpl-2",
             "verdict": "PASS" if p2 else "FAIL",
             "note": f"median-of-N disparity gives rel_err < {BAR} on both P277 failures",
             "fixed": [f"{r['scene']}/{r['obj'][:24]}" for r in fixed],
             "targets_detail": [
                 {"row": f"{r['scene']}/{r['obj'][:40]}",
                  "disp_centre": r["disp_centre"], "disp_median": r["disp_median"],
                  "mad": r["mad"], "rel_centre": r["rel_centre"],
                  "rel_median": r["rel_median"],
                  "p277_attribution": "geometry_error"} for r in targets]},
            {"id": "P-tmpl-3",
             "verdict": "PASS" if p3 else "FAIL",
             "note": f"controls keep rel_err < {BAR} and shift <= {SHIFT_BAR} of GT",
             "controls_regressed": [f"{r['scene']}/{r['obj'][:24]}" for r in regressed],
             "controls_shifted": [f"{r['scene']}/{r['obj'][:24]}" for r in shifted],
             "max_shift_over_gt": round(max(
                 (abs(r["z_median"] - r["z_centre"]) / r["z_gt"] for r in controls
                  if r["z_median"] and r["z_centre"]), default=0.0), 4)},
        ],
        "declared_prereg_gap": (
            "The 3x3 grid requires an 80x80 template window inside the bbox; the "
            "Midd2 yellow-object bbox is 96x48 px, so no grid point fits. Rule "
            "adopted without touching any threshold: fall back to the P277 centre "
            "template (median == centre) and count the row as a zero-change control."
        ),
        "declared_deviation": (
            "P278 ran on the DSH bundled Python (numpy 2.3.5, Pillow 12.3.0) "
            "instead of the P277 host env; the reproduction gate (P-tmpl-4) is what "
            "licenses the comparison, and it passed with max |diff| = "
            f"{max(repro) if repro else None} px."
        ),
    }
    verdict["overall"] = ("PASS" if all(p["verdict"] == "PASS"
                                        for p in verdict["predictions"]) else "MIXED")

    # --- POST-HOC DESCRIPTIVE (no prediction is scored on these fields) ------
    # Added after the run because the grid composition turned out to be part of
    # the story: how many templates fit, and whether the ground-truth disparity
    # was even present among them.
    desc = []
    for r in rows:
        gt_disp = (r["f_full"] * 0.160 / r["z_gt"]) if r.get("z_gt") else None
        ds = [t["disp"] for t in r["templates"]]
        near = ([d for d in ds if abs(d - gt_disp) <= 5] if gt_disp else [])
        desc.append({
            "row": f"{r['scene']}/{r['obj'][:34]}",
            "grid_n": r["grid_n"], "grid_fallback": r["grid_fallback"],
            "templates": ds, "gt_disp": None if gt_disp is None else round(gt_disp, 1),
            "n_templates_within_5px_of_gt": len(near),
            "median": r["disp_median"],
        })
    verdict["post_hoc_descriptive"] = {
        "note": "Not part of the pre-registered scoring; reported because it "
                "explains the partial fix and motivates P279.",
        "rows": desc,
    }
    json.dump(verdict, open(OUT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(verdict, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
