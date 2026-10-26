# -*- coding: utf-8 -*-
"""P279: consensus-cluster aggregation over the banked P278 template sets.

Pure arithmetic on out/p278/p278_raw.json (hash-gated). No model calls, no
image matching.  Frozen design: p279_preregistration.json.

Run:  python p279_consensus_cluster.py
Env overrides (used by the perturbation test): P279_RAW, P279_OUT, P279_PRE.
"""
import hashlib
import json
import os
import random
import statistics

PRE = os.environ.get("P279_PRE", "p279_preregistration.json")
RAW = os.environ.get("P279_RAW", "out/p278/p278_raw.json")
OUT = os.environ.get("P279_OUT", "p279_verdict.json")
BAR = 0.15
SHIFT_BAR = 0.05
GAP_PX = 5.0
SEED = 20261026
NON_EVALUABLE = {"Midd2"}   # <2 valid templates: cannot evaluate any rule


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def clusters(vals, gap=GAP_PX):
    """Single-linkage: consecutive sorted values whose gap <= tol join."""
    vs = sorted(vals)
    out = [[vs[0]]]
    for v in vs[1:]:
        if v - out[-1][-1] <= gap:
            out[-1].append(v)
        else:
            out.append([v])
    return out


def pick_consensus(templates):
    """R2: largest cluster; ties -> higher mean NCC, then lower median."""
    tmpl = [t for t in templates if t["disp"] >= 0]
    if not tmpl:
        return None
    groups = []
    for c in clusters([t["disp"] for t in tmpl]):
        members = [t for t in tmpl if t["disp"] in c]
        groups.append({
            "n": len(members),
            "median": statistics.median(c),
            "mean_ncc": sum(m["ncc"] for m in members) / len(members),
            "members": c,
        })
    groups.sort(key=lambda g: (-g["n"], -g["mean_ncc"], g["median"]))
    return groups


def main():
    pre = json.load(open(PRE, encoding="utf-8"))
    raw_hash = sha256(RAW)
    gate_ok = raw_hash == pre["frozen"]["banked_raw_sha256"]
    rows = json.load(open(RAW, encoding="utf-8"))
    rng = random.Random(SEED)

    verdict = {
        "id": "P279",
        "honest_label": pre["honest_label"],
        "gate": {"input": RAW, "sha256": raw_hash,
                 "expected": pre["frozen"]["banked_raw_sha256"],
                 "passed": gate_ok},
    }
    if not gate_ok:
        verdict.update({
            "predictions": [{"id": p["id"], "verdict": "NOT SCORED"}
                            for p in pre["predictions"]],
            "overall": "INCONCLUSIVE",
            "declared_deviation": "The banked-input hash gate FAILED, so no prediction is "
                                  "scored (pre-registered no-partial-credit rule).",
        })
        json.dump(verdict, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(verdict, ensure_ascii=False, indent=1))
        return

    detail = []
    for r in rows:
        tmpl = r["templates"]
        valid = [t for t in tmpl if t["disp"] >= 0]
        base_med = statistics.median([t["disp"] for t in valid]) if valid else None
        groups = pick_consensus(tmpl)
        best = groups[0] if groups else None
        rand = rng.choice(valid)["disp"] if valid else None
        ncc_pick = max(valid, key=lambda t: t["ncc"])["disp"] if valid else None
        f = r["f_full"]
        rel = lambda d: (None if d is None else
                         round(abs(f * 0.160 / d - r["z_gt"]) / r["z_gt"], 4))
        detail.append({
            "row": f"{r['scene']}/{r['obj'][:34]}",
            "scene": r["scene"], "obj": r["obj"],
            "was_p277_failure": r["was_p277_failure"],
            "evaluable": r["scene"] not in NON_EVALUABLE and len(valid) >= 2,
            "n_templates": len(tmpl), "n_valid": len(valid),
            "median_R1": base_med, "rel_R1": rel(base_med),
            "cluster_R2": best["median"] if best else None,
            "cluster_size": best["n"] if best else None,
            "cluster_members": best["members"] if best else [],
            "cluster_mean_ncc": round(best["mean_ncc"], 3) if best else None,
            "rel_R2": rel(best["median"]) if best else None,
            "random_R3": rand, "rel_R3": rel(rand),
            "best_ncc_R4": ncc_pick, "rel_R4": rel(ncc_pick),
            "gt_disp": round(f * 0.160 / r["z_gt"], 1),
        })

    board = next(d for d in detail
                 if d["scene"] == "Lampshade1" and d["was_p277_failure"])
    block = next(d for d in detail if d["scene"] == "Monopoly")
    controls = [d for d in detail if not d["was_p277_failure"] and d["evaluable"]]

    p1 = board["rel_R2"] is not None and board["rel_R2"] < BAR
    regressed = [d for d in controls if d["rel_R2"] is None or d["rel_R2"] >= BAR]
    # shift is measured on the depth scale: Z = f*B/d with f*B constant per row,
    # so the relative depth shift is |d_R1/d_R2 - 1|.
    shifted = []
    for d in controls:
        if d["cluster_R2"] is None or d["median_R1"] is None:
            continue
        if abs(d["median_R1"] / d["cluster_R2"] - 1) > SHIFT_BAR:
            shifted.append(d)
    p2 = not regressed and not shifted
    p3 = block["rel_R2"] is not None and block["rel_R2"] >= BAR
    r3_fail = [d for d in controls if d["rel_R3"] is None or d["rel_R3"] >= BAR]
    p4 = len(r3_fail) >= 3
    gt_board = board["gt_disp"]
    p5 = (board["cluster_size"] is not None and board["cluster_size"] >= 3
          and board["cluster_R2"] is not None
          and abs(board["cluster_R2"] - gt_board) / gt_board <= 0.15)

    verdict["predictions"] = [
        {"id": "P279-1", "verdict": "PASS" if p1 else "FAIL",
         "board_rel_R2": board["rel_R2"], "board_rel_R1": board["rel_R1"]},
        {"id": "P279-2", "verdict": "PASS" if p2 else "FAIL",
         "n_evaluable_controls": len(controls),
         "controls_regressed": [d["row"] for d in regressed],
         "controls_shifted": [d["row"] for d in shifted],
         "max_shift_R1_to_R2": round(max(
             (abs(d["median_R1"] / d["cluster_R2"] - 1) for d in controls
              if d["cluster_R2"] and d["median_R1"]), default=0.0), 4)},
        {"id": "P279-3", "verdict": "PASS" if p3 else "FAIL",
         "note": "registered NEGATIVE: block should NOT be fixed (3 samples, validity-filtered)",
         "block_rel_R2": block["rel_R2"], "block_cluster_members": block["cluster_members"]},
        {"id": "P279-4", "verdict": "PASS" if p4 else "FAIL",
         "random_seed": SEED, "random_failed_controls": [d["row"] for d in r3_fail]},
        {"id": "P279-5", "verdict": "PASS" if p5 else "FAIL",
         "board_cluster": board["cluster_members"],
         "board_cluster_median": board["cluster_R2"],
         "board_gt_disp": gt_board,
         "median_all_templates": board["median_R1"]},
    ]
    verdict["overall"] = ("PASS" if all(p["verdict"] == "PASS"
                                        for p in verdict["predictions"]) else "MIXED")
    verdict["rows"] = detail
    json.dump(verdict, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"id": "P279", "overall": verdict["overall"],
                      "gate": verdict["gate"],
                      "predictions": [(p["id"], p["verdict"])
                                      for p in verdict["predictions"]]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
