# -*- coding: utf-8 -*-
"""P278 verdict — v2 after independent verification (2026-10-26 23:5x).

Fixes forced by the verifier:
  1. The reproduction gate is now a real short-circuit: if it fails, every other
     prediction is NOT SCORED and the overall verdict is INCONCLUSIVE (the
     pre-registration's "no partial credit" clause), instead of being ignored.
  2. The outlier rule is the registered one (|delta| > 3*MAD), with no extra
     unregistered branch for MAD == 0.
  3. A post-hoc VALIDITY check is declared and reported: a negative disparity is
     physically impossible for rectified stereo with a positive baseline, so the
     Monopoly grid's -18 px sample is a matcher artefact. Removing it changes the
     block's outlier status, so P-tmpl-1 is downgraded from PASS to PARTIAL.
  4. Rows whose median is literally the centre template (fallback / MAD 0) are
     non-evaluable tautologies for P-tmpl-3 and are excluded from its pass count.
  5. Hashes of the frozen pre-registration and the raw artifact are recorded so a
     reviewer can check what was frozen.
"""
import hashlib
import json
import statistics

import os

RAW = os.environ.get("P278_RAW", "out/p278/p278_raw.json")
PRE = os.environ.get("P278_PRE", "p278_preregistration.json")
OUT = os.environ.get("P278_OUT", "p278_verdict.json")
BAR = 0.15          # identical to P277
SHIFT_BAR = 0.05    # P-tmpl-3


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def median_mad(vals):
    med = statistics.median(vals)
    mad = statistics.median([abs(v - med) for v in vals])
    return med, mad


def is_outlier(disp, med, mad):
    """Registered rule: |delta| > 3*MAD.  With MAD == 0 this reduces to delta > 0."""
    return abs(disp - med) > 3 * mad


def main():
    rows = json.load(open(RAW, encoding="utf-8"))
    targets = [r for r in rows if r["was_p277_failure"]]
    controls = [r for r in rows if not r["was_p277_failure"]]

    repro = [abs(r["disp_centre"] - r["disp_recorded"]) for r in rows
             if r["disp_centre"] is not None]
    max_repro = max(repro) if repro else None
    gate_ok = bool(repro) and max_repro <= 1

    base = {
        "id": "P278",
        "n_rows": len(rows), "n_targets": len(targets), "n_controls": len(controls),
        "hashes": {"prereg_sha256": sha256(PRE), "raw_sha256": sha256(RAW)},
        "gate": {"prediction": "P-tmpl-4",
                 "max_abs_px_diff": max_repro, "rows_checked": len(repro),
                 "passed": gate_ok},
    }

    if not gate_ok:
        base.update({
            "predictions": [
                {"id": p, "verdict": "NOT SCORED"} for p in
                ("P-tmpl-4", "P-tmpl-1", "P-tmpl-2", "P-tmpl-3")],
            "overall": "INCONCLUSIVE",
            "declared_deviation": (
                "The reproduction gate FAILED (max |diff| = "
                f"{max_repro} px > 1 px), so per the pre-registration no other "
                "prediction is scored and the overall verdict is INCONCLUSIVE."
            ),
        })
        json.dump(base, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(base, ensure_ascii=False, indent=1))
        return

    # --- P-tmpl-1: mechanism (registered rule) ---
    out_t = {}
    for r in targets:
        if r["disp_median"] is None or r["mad"] is None:
            out_t[f"{r['scene']}/{r['obj'][:24]}"] = None
        else:
            out_t[f"{r['scene']}/{r['obj'][:24]}"] = is_outlier(
                r["disp_centre"], r["disp_median"], r["mad"])
    out_c = [r for r in controls
             if is_outlier(r["disp_centre"], r["disp_median"], r["mad"])]
    registered_pass = all(v is True for v in out_t.values()) and len(out_c) <= 1

    # --- post-hoc VALIDITY check (declared, weakens P-tmpl-1) ---
    # rectified stereo with a positive baseline cannot produce a negative
    # disparity for a visible point; such a sample is a matcher artefact and
    # must not be trusted inside a 3-point MAD.
    valid = {}
    for r in rows:
        vals = [t["disp"] for t in r["templates"] if t["disp"] >= 0]
        if len(vals) < 2:
            valid[f"{r['scene']}/{r['obj'][:24]}"] = None
            continue
        med, mad = median_mad(vals)
        valid[f"{r['scene']}/{r['obj'][:24]}"] = {
            "n_used": len(vals), "n_dropped": r["grid_n"] - len(vals),
            "median": med, "mad": mad,
            "centre_outlier": is_outlier(r["disp_centre"], med, mad),
            "z_from_median": r["f_full"] * 0.160 / med,
            "rel_from_median": round(
                abs(r["f_full"] * 0.160 / med - r["z_gt"]) / r["z_gt"], 4),
        }
    validity_t = {k: valid[k] for k in out_t}
    validity_pass = all(v is not None and v["centre_outlier"] is True
                        for v in validity_t.values())

    p1 = ("PASS" if (registered_pass and validity_pass)
          else "PARTIAL" if registered_pass else "FAIL")

    # --- P-tmpl-2: fix (registered estimator, all produced templates) ---
    fixed = [r for r in targets if r["rel_median"] is not None
             and r["rel_median"] < BAR]
    p2 = len(targets) == 2 and len(fixed) == 2

    # --- P-tmpl-3: no regression over EVALUABLE controls ---
    # a row whose median is literally the centre (fallback bbox or MAD 0) cannot
    # change under the estimator: it is a tautology, not evidence.
    evaluable = [r for r in controls
                 if not r["grid_fallback"] and (r["mad"] or 0) > 0
                 and r["disp_median"] is not None]
    tautological = [r for r in controls if r not in evaluable]
    regressed = [r for r in evaluable
                 if r["rel_median"] is None or r["rel_median"] >= BAR]
    shifted = [r for r in evaluable
               if r["z_median"] is not None and r["z_centre"] is not None
               and abs(r["z_median"] - r["z_centre"]) / r["z_gt"] > SHIFT_BAR]
    p3 = not regressed and not shifted

    verdict = dict(base)
    verdict["predictions"] = [
        {"id": "P-tmpl-4", "verdict": "PASS",
         "note": "reproduction gate (short-circuits the rest on failure)",
         "max_abs_px_diff": max_repro, "rows_checked": len(repro)},
        {"id": "P-tmpl-1",
         "verdict": p1,
         "note": ("registered rule: centre template is a |delta| > 3*MAD outlier inside "
                  "its own grid; PARTIAL because the post-hoc validity check removes an "
                  "impossible negative-disparity sample on the block"),
         "target_outliers_registered": out_t,
         "control_outliers_registered": [f"{r['scene']}/{r['obj'][:24]}" for r in out_c],
         "validity_check_targets": validity_t,
         "registered_pass": registered_pass,
         "validity_pass": validity_pass},
        {"id": "P-tmpl-2",
         "verdict": "PASS" if p2 else "FAIL",
         "note": f"median of the available templates gives rel_err < {BAR} on both P277 failures",
         "fixed": [f"{r['scene']}/{r['obj'][:24]}" for r in fixed],
         "targets_detail": [
             {"row": f"{r['scene']}/{r['obj'][:40]}",
              "grid_n": r["grid_n"], "disp_centre": r["disp_centre"],
              "disp_median": r["disp_median"], "mad": r["mad"],
              "rel_centre": r["rel_centre"], "rel_median": r["rel_median"]}
             for r in targets]},
        {"id": "P-tmpl-3",
         "verdict": "PASS" if p3 else "FAIL",
         "note": (f"evaluable controls keep rel_err < {BAR} and shift <= {SHIFT_BAR} of GT; "
                  "tautological controls are excluded from the pass count, not counted as wins"),
         "n_evaluable_controls": len(evaluable),
         "tautological_controls_excluded": [f"{r['scene']}/{r['obj'][:24]}" for r in tautological],
         "controls_regressed": [f"{r['scene']}/{r['obj'][:24]}" for r in regressed],
         "controls_shifted": [f"{r['scene']}/{r['obj'][:24]}" for r in shifted],
         "max_shift_over_gt": round(max(
             (abs(r["z_median"] - r["z_centre"]) / r["z_gt"] for r in evaluable
              if r["z_median"] and r["z_centre"]), default=0.0), 4),
         "shift_px_examples": sorted(
             ((round(r["disp_centre"] - r["disp_median"], 1),
               f"{r['scene']}/{r['obj'][:20]}") for r in evaluable
              if r["disp_centre"] is not None and r["disp_median"] is not None),
             key=lambda t: -abs(t[0]))[:3]},
    ]
    verdict["overall"] = ("PASS" if all(p["verdict"] == "PASS"
                                        for p in verdict["predictions"]) else "MIXED")
    verdict["amendments"] = [
        {"id": "A1", "kind": "pre-registration gap (declared at implementation)",
         "text": ("The 3x3 grid needs an 80x80 window inside the bbox. The Midd2 "
                  "yellow-object bbox is 96x48 px, so no grid point fits; the fallback "
                  "is the centre template (median == centre). No threshold was touched, "
                  "and the row is now marked non-evaluable instead of 'zero-change control'.")},
        {"id": "A2", "kind": "post-hoc robustness (weakens a verdict)",
         "text": ("A negative disparity is impossible in rectified stereo with a positive "
                  "baseline. The Monopoly grid's -18 px sample is a matcher artefact; "
                  "dropping it leaves {71, 421} -> median 246, MAD 175, |421-246| = 175 < "
                  "525, so the block's centre is NO LONGER an outlier. P-tmpl-1 is therefore "
                  "reported PARTIAL, not PASS. The fix claim for the block (P-tmpl-2) also "
                  "does not survive the filter (rel 0.717), so it stays FAIL.")},
        {"id": "A3", "kind": "claim precision",
         "text": ("The estimator used the templates that fit: 12 rows x 9 + Monopoly x 3 + "
                  "Midd2 x 1 = 112 template matches, not 14 x 9 = 126. 'median-of-9' was "
                  "sloppy wording for 'median of the available templates'.")},
        {"id": "A4", "kind": "post-hoc descriptive (not scored)",
         "text": ("Grid composition and GT-in-grid table, added after the run because it "
                  "explains the partial fix: every row has at least one template within "
                  "+-5 px of the true disparity.")},
        {"id": "A5", "kind": "wording corrections vs the first draft",
         "text": ("(i) 'the 6 rows without bboxL' -> 5 rows have no bboxL and 1 (Bowling1 "
                  "white pin) has a bbox but no rel_err (degenerate disparity, -26 px); "
                  "exclusion is by missing rel_err. (ii) '~2 px shift' -> mean -1.3 px, "
                  "largest two are -6 px (157->151) and -3 px (132->129). (iii) 'centre "
                  "lands on background' -> the centre match is a NEARER, low-NCC "
                  "(0.435/0.574) surface (0.99 m / 0.51 m against GT 3.01/3.08 m), i.e. "
                  "the matcher locked onto a spurious patch; 'outlier' is the measured "
                  "claim, 'background' was an unmeasured gloss.")},
        {"id": "A6", "kind": "bookkeeping",
         "text": ("p278_preregistration.json's artifacts_planned omits p278_analyze.py "
                  "(the frozen file is left untouched; this note is the correction).")},
    ]

    # --- POST-HOC DESCRIPTIVE (not scored) ---
    desc = []
    for r in rows:
        gt_disp = (r["f_full"] * 0.160 / r["z_gt"]) if r.get("z_gt") else None
        ds = [t["disp"] for t in r["templates"]]
        near = ([d for d in ds if abs(d - gt_disp) <= 5] if gt_disp else [])
        desc.append({
            "row": f"{r['scene']}/{r['obj'][:34]}",
            "grid_n": r["grid_n"], "grid_fallback": r["grid_fallback"],
            "templates": ds,
            "gt_disp": None if gt_disp is None else round(gt_disp, 1),
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
    print(json.dumps({k: verdict[k] for k in
                      ("id", "overall", "gate", "hashes")},
                     ensure_ascii=False, indent=1))
    print("predictions:", [(p["id"], p["verdict"]) for p in verdict["predictions"]])


if __name__ == "__main__":
    main()
