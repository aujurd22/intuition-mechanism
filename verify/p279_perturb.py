# -*- coding: utf-8 -*-
"""Perturbation test for P279's banked-input hash gate.

P279 scores nothing unless the sha256 of out/p278/p278_raw.json equals the frozen
value in the pre-registration. This test tampers a copy of the raw data and runs
the REAL p279_consensus_cluster.py on it, then asserts the output is
INCONCLUSIVE with every prediction NOT SCORED.

Exit 0 iff the gate fired.

Run:  python verify/p279_perturb.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    tmp = tempfile.mkdtemp(prefix="p279_perturb_")
    try:
        raw = json.load(open(os.path.join(REPO, "out", "p278", "p278_raw.json"),
                             encoding="utf-8"))
        raw[0]["templates"][0]["disp"] += 7          # change one measurement
        tampered = os.path.join(tmp, "raw_tampered.json")
        json.dump(raw, open(tampered, "w", encoding="utf-8"), ensure_ascii=False)
        out = os.path.join(tmp, "verdict.json")
        env = dict(os.environ)
        env.update({"P279_RAW": tampered, "P279_OUT": out,
                    "P279_PRE": os.path.join(REPO, "p279_preregistration.json")})
        subprocess.run([sys.executable,
                        os.path.join(REPO, "p279_consensus_cluster.py")],
                       check=True, env=env, cwd=REPO, stdout=subprocess.DEVNULL)
        v = json.load(open(out, encoding="utf-8"))
        preds = {p["id"]: p["verdict"] for p in v["predictions"]}
        ok = (v.get("overall") == "INCONCLUSIVE"
              and set(preds.values()) == {"NOT SCORED"}
              and v["gate"]["passed"] is False)
        print(f"tampered run: overall={v.get('overall')} "
              f"gate_passed={v['gate']['passed']} preds={preds} -> "
              f"{'PASS' if ok else 'FAIL'}")
        sys.exit(0 if ok else 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
