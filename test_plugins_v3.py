# -*- coding: utf-8 -*-
"""v3 upgrade smoke test — exercises all nine upgrade items without any
network call.  Run: python test_plugins_v3.py   (exit 0 = all pass)"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PASS = []
FAIL = []

def check(name, ok):
    (PASS if ok else FAIL).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")

# ---- 1+2: coordinate-adaptive feedback + tiered ladder ----
from hallucination_gate.evidence import (coordinate_adaptive_feedback,
                                         tiered_evidence, _detect_mismatch)
claims = [(21, 32, 3), (22, 33, 3), (23, 32, 3)]
actual = [(32, 21, 3), (33, 22, 3), (33, 23, 3)]  # transposed
cls, hint = _detect_mismatch(claims, actual)
check("1: transposed-mismatch detected", cls == "TRANSPOSED")
fb = coordinate_adaptive_feedback(claims, actual)
check("1: feedback names mismatch + anchors model coords",
      "COORDINATE MISMATCH" in fb and "you claimed" in fb)
lvl3, e3 = tiered_evidence(1, claims, actual)
lvl5, e5 = tiered_evidence(2, claims, actual)
lvl10, e10 = tiered_evidence(5, claims, actual, grid_fn=lambda r, c: 99)
check("2: ladder escalates rich3->rich5->rich10",
      lvl3 == "rich3" and lvl5 == "rich5" and lvl10 == "rich10"
      and "COORDINATE" in e5 and "grid values" in e10)

# ---- 3: preamble protocol ----
from hallucination_gate.preamble_ledger import (preamble_prompt,
                                                check_preamble,
                                                PredictionLedger)
good = check_preamble("row 0 = top, 0-based indexing")
bad = check_preamble("I will use my own coordinates")
contra = check_preamble("0-based indexing and 1-based row 1 = first")
check("3: preamble good/missing/contradictory",
      good["ok"] and not bad["ok"] and not contra["ok"])

# ---- 4: prediction ledger ----
tmp = tempfile.mkdtemp()
led = PredictionLedger(os.path.join(tmp, "ledger.jsonl"))
rec = led.record("speculative claim", "if X then frame turns red")
led.resolve(rec["id"], "frame turned red", hit=True)
st = led.stats()
check("4: ledger record/resolve/stats",
      st["resolved"] == 1 and st["hit_rate"] == 1.0 and st["open"] == 0)

# ---- 5: validator auto-registration (structure only — no scan run) ----
src = open("auto_scan_loop.py", encoding="utf-8").read()
check("5: scan loop registers verifiers on build",
      "auto_verifiers.json" in src and "verifier_registered" in src)

# ---- 6: out-of-sample probe ----
from intuition_pack.probe_alignment import probe_out_of_sample
items = [{"code": f"def f{i}():\n    return {i % 2}", "test": "assert True",
          "passes": i % 2 == 0} for i in range(10)]
res = probe_out_of_sample(items, [], judge_fn=lambda p, n: [True] * n)
check("6: out-of-sample probe returns gap+verdict",
      {"train_acc", "holdout_acc", "gap", "verdict"} <= set(res))

# ---- 7: error-pool pack build ----
from intuition_pack.error_feedback import build_pack_with_errors, load_error_pool
tmpdir = tempfile.mkdtemp()
pool = [{"id": "e1", "code": "def g():", "test": "assert g()", "passes": False}]
json.dump(pool, open(os.path.join(tmpdir, "dom_errors.json"), "w"))
pack, stats = build_pack_with_errors("dom", "judge code vs tests", [],
                                     {"name": "pytest_check",
                                      "rule": "execution"}, tmpdir)
check("7: error-pool items become pack exemplars",
      stats["pool_reused"] == 1 and len(pack.exemplars) == 1)
pack.to_json  # sanity
import json as _json
_json.dump(_json.loads(pack.to_json()),
           open(os.path.join(tmpdir, "dom.json"), "w"),
           ensure_ascii=False)

# ---- 8: transferability grading ----
from intuition_pack.probe_alignment import grade_transferability
pj = {"charter": "judge code", "exemplars": [{"inputs": {"code": "x"}, "label": "PASS"}]}
grades = grade_transferability(pj, {"neighborA": [{"inputs": {"code": "y"}, "label": "PASS"}]},
                               judge_fn=lambda p, n: ["PASS"] * n)
check("8: transferability graded", grades["grade"] in
      ("LOCAL_ONLY", "NEIGHBOR_OK", "GENERAL", "UNTESTED"))

# ---- 9: cognitive booth (fused router) ----
from hallucination_gate.cognitive_booth import CognitiveBooth
booth = CognitiveBooth(packs_dir=tmpdir)
r1 = booth.route("d=5 is RATIONAL", domain="sixrow", payload={"d": 5, "claimed": "RATIONAL"})
check("9a: verifier route (zone-1)", r1["handler"] == "mechanical-gate"
      and r1["status"] in ("VERIFIED", "REFUTED", "ABSTAIN"))
r2 = booth.route("this pack judges code", domain="dom", preamble="row 0 = top, 0-based")
check("9b: pack route", r2["handler"] == "pack-judge")
r3 = booth.route("some unknown domain claim", domain="never_seen_domain_xyz")
check("9c: scanner-candidate route + ledger record",
      r3["handler"] == "scan-candidate" and r3.get("prediction_id"))
qf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan_queue.json")
q = json.load(open(qf, encoding="utf-8"))
check("9d: booth auto-registered scanner candidate",
      any(d.get("domain") == "never_seen_domain_xyz" for d in q["domains"]))
q["domains"] = [d for d in q["domains"] if d.get("domain") != "never_seen_domain_xyz"]
json.dump(q, open(qf, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

print(f"\n{'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)} "
      f"({len(PASS)} passed)")
sys.exit(1 if FAIL else 0)
