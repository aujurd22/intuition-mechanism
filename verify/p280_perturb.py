# -*- coding: utf-8 -*-
"""Perturbation test for P280's design gate.

The verdict must refuse to score a decimated input: fewer than 4 evaluable rows
-> INCOMPLETE, every prediction NOT SCORED. This test keeps only 2 rows and runs
the real p280_verdict.py.

Exit 0 iff the gate fired.

Run:  python verify/p280_perturb.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    tmp = tempfile.mkdtemp(prefix="p280_perturb_")
    try:
        raw = json.load(open(os.path.join(REPO, "out", "p280", "p280_raw.json"),
                             encoding="utf-8"))
        evaluable = [r for r in raw if r.get("evaluable")][:2]
        decimated = os.path.join(tmp, "raw_decimated.json")
        json.dump(evaluable, open(decimated, "w", encoding="utf-8"), ensure_ascii=False)
        out = os.path.join(tmp, "verdict.json")
        env = dict(os.environ)
        env.update({"P280_RAW": decimated, "P280_OUT": out})
        subprocess.run([sys.executable, os.path.join(REPO, "p280_verdict.py")],
                       check=True, env=env, cwd=REPO, stdout=subprocess.DEVNULL)
        v = json.load(open(out, encoding="utf-8"))
        preds = {p["id"]: p["verdict"] for p in v["predictions"]}
        ok = (v.get("overall") == "INCOMPLETE"
              and set(preds.values()) == {"NOT SCORED"})
        print(f"decimated run: overall={v.get('overall')} preds={preds} -> "
              f"{'PASS' if ok else 'FAIL'}")
        sys.exit(0 if ok else 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
