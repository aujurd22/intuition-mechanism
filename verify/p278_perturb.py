# -*- coding: utf-8 -*-
"""Perturbation test for P278's reproduction gate.

The pre-registration says: if the reproduction gate fails, no other prediction
is scored and the verdict is INCONCLUSIVE ("no partial credit"). This test
proves that clause is implemented by running the REAL analyze script on a
perturbed copy of the raw data (+5 px to every recorded disparity, which must
break the +-1 px gate) and checking the output verdict.

Exit 0 iff the perturbed run is INCONCLUSIVE with every prediction NOT SCORED.

Run:  python verify/p278_perturb.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    tmp = tempfile.mkdtemp(prefix="p278_perturb_")
    try:
        raw = json.load(open(os.path.join(REPO, "out", "p278", "p278_raw.json"),
                             encoding="utf-8"))
        for r in raw:
            r["disp_recorded"] = r["disp_recorded"] + 5
        perturbed = os.path.join(tmp, "raw_perturbed.json")
        json.dump(raw, open(perturbed, "w", encoding="utf-8"), ensure_ascii=False)
        out = os.path.join(tmp, "verdict.json")
        env = dict(os.environ)
        env.update({"P278_RAW": perturbed, "P278_OUT": out,
                    "P278_PRE": os.path.join(REPO, "p278_preregistration.json")})
        subprocess.run([sys.executable,
                        os.path.join(REPO, "p278_analyze.py")],
                       check=True, env=env, cwd=REPO,
                       stdout=subprocess.DEVNULL)
        v = json.load(open(out, encoding="utf-8"))
        preds = {p["id"]: p["verdict"] for p in v["predictions"]}
        dev_ok = "FAILED" in v.get("declared_deviation", "")
        ok = (v.get("overall") == "INCONCLUSIVE"
              and set(preds.values()) == {"NOT SCORED"}
              and dev_ok)
        print(f"perturbed run: overall={v.get('overall')} predictions={preds} "
              f"deviation_mentions_FAILED={dev_ok} -> "
              f"{'PASS' if ok else 'FAIL'}")
        sys.exit(0 if ok else 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
