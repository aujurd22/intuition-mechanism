# -*- coding: utf-8 -*-
"""verify_verdict.py — the verification gate for registered experiments.

Rule (from P278 forward): a committed verdict is not sufficient. Every
experiment with ID >= CUTOFF_ID that ships a machine-readable verdict must also
ship a verification record in verifications/p<ID>.json containing

  independent_recompute : a script that recomputes the key numbers WITHOUT
                          importing the estimator under test, with a tolerance
                          and an observed error (status PASS)
  perturbation_test     : a script that perturbs an input so a registered gate
                          must fire, plus the observed outcome (status PASS)
  validity_clauses      : the data-validity rules the estimator obeys (non-empty)

and the verdict's own frozen hashes must still match the files they name.

Rows below CUTOFF_ID are grandfathered (listed, not enforced) — the discipline is
new and applying it retroactively would fail 200+ historical rows for reasons
unrelated to their content.

Run:  python verify_verdict.py          (CI mode; exit 1 on violation)
      python verify_verdict.py --list   (show which rows are enforced)
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CUTOFF_ID = 278
PLAN = os.path.join(ROOT, "docs", "RESEARCH_PLAN.md")


def sha256(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def verdict_files():
    out = {}
    for name in os.listdir(ROOT):
        m = re.fullmatch(r"p(\d+)_verdict\.json", name)
        if m:
            out[int(m.group(1))] = os.path.join(ROOT, name)
    return out


def registry_rows():
    text = open(PLAN, encoding="utf-8").read()
    rows = {}
    for m in re.finditer(r"(?m)^\| (P\d+[a-z]?(?:[- ][A-Za-z0-9]+)*) \|(.*)$", text):
        rows.setdefault(m.group(1), m.group(2))
    return rows


def main():
    list_mode = "--list" in sys.argv
    verdicts = verdict_files()
    rows = registry_rows()
    failures, enforced, grandfathered = [], [], []

    for pid_num in sorted(verdicts):
        pid = f"P{pid_num}"
        rec_path = os.path.join(ROOT, "verifications", f"p{pid_num}.json")
        if pid_num < CUTOFF_ID:
            grandfathered.append(pid)
            continue
        enforced.append(pid)
        if not os.path.exists(rec_path):
            failures.append(f"{pid}: no verification record (verifications/p{pid_num}.json)")
            continue
        try:
            rec = json.load(open(rec_path, encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{pid}: verification record is not valid JSON ({exc})")
            continue

        ir = rec.get("independent_recompute") or {}
        pt = rec.get("perturbation_test") or {}
        vc = rec.get("validity_clauses") or []
        for key, block, label in (("independent_recompute", ir, "independent recompute"),
                                  ("perturbation_test", pt, "perturbation test")):
            if block.get("status") != "PASS":
                failures.append(f"{pid}: {label} status is {block.get('status')!r}, not PASS")
            script = block.get("script")
            if not script or not os.path.exists(os.path.join(ROOT, script)):
                failures.append(f"{pid}: {label} script missing ({script!r})")
        if not vc or not all(isinstance(v, str) and v.strip() for v in vc):
            failures.append(f"{pid}: validity_clauses empty")
        if "independent_recompute" in rec:
            tol, obs = ir.get("tolerance_px"), ir.get("observed_max_abs_px")
            if not (isinstance(tol, (int, float)) and isinstance(obs, (int, float))):
                failures.append(f"{pid}: recompute tolerance/observed not numeric")
            elif obs > tol:
                failures.append(f"{pid}: recompute error {obs} px exceeds tolerance {tol} px")

        # frozen hashes must still match
        verdict = json.load(open(verdicts[pid_num], encoding="utf-8"))
        hashes = verdict.get("hashes") or {}
        for key in ("prereg_sha256", "raw_sha256"):
            if key not in hashes:
                continue
            target = {"prereg_sha256": f"p{pid_num}_preregistration.json",
                      "raw_sha256": f"out/p{pid_num}/p{pid_num}_raw.json"}[key]
            actual = sha256(os.path.join(ROOT, target))
            if actual is not None and actual != hashes[key]:
                failures.append(f"{pid}: frozen {key} no longer matches {target}")

        # the ledger row must carry the same overall polarity
        overall = verdict.get("overall", "")
        row_text = rows.get(pid)
        if row_text is None:
            failures.append(f"{pid}: no registry row (verdict without a row)")
        elif overall and overall not in row_text:
            failures.append(f"{pid}: registry row does not mention overall verdict {overall!r}")

    if list_mode:
        print(f"enforced (ID >= P{CUTOFF_ID}): {', '.join(enforced) or 'none'}")
        print(f"grandfathered (ID <  P{CUTOFF_ID}): {len(grandfathered)} rows")

    for f in failures:
        print(f"[FAIL] {f}")
    if failures:
        print(f"VERIFICATION GATE: {len(failures)} failures "
              f"(enforced rows: {', '.join(enforced) or 'none'})")
        sys.exit(1)
    print(f"VERIFICATION GATE: PASS — {len(enforced)} enforced row(s), "
          f"{len(grandfathered)} grandfathered (ID < P{CUTOFF_ID})")


if __name__ == "__main__":
    main()
