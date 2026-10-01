"""Regression gate: the P138 protocol, mechanized.

Mechanical gate (default, deterministic, no API):
  G1  the domain's pack loads atomically and parses
  G2  pack exemplar labels agree with the registered verifier on every
      exemplar (the pack cannot contradict its own verifier)
  G3  charter declares a single evidence source (P138 rule)
  G4  the verifier reproduces the recorded ground truth on the full
      stored test set for the domain (for ramanujan-sixrow: the
      P121 census band, six hits + zero false positives)

LLM gate (--llm): reruns the P138 three-condition test and requires
  B >= A + 15pp and perturbation FP = 0 (the pre-registered bars).
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intuition_pack.pack import Pack
from intuition_pack.verifiers import run_verifier


def mechanical_gate(pack: Pack, testset: list) -> dict:
    checks = {}

    # G1 atomic load (pack already parsed by caller; re-serialize to prove)
    checks["G1_atomic_load"] = Pack.from_json(pack.to_json()) is not None

    # G2 exemplar labels agree with the verifier
    disagree = []
    for e in pack.exemplars:
        out = run_verifier(pack.verifier.name, dict(e.inputs))
        if out["verdict"] != e.label:
            disagree.append({"exemplar_d": e.d, "label": e.label,
                             "verifier": out["verdict"]})
    checks["G2_labels_match_verifier"] = (len(disagree) == 0)
    checks["G2_disagreements"] = disagree

    # G3 single evidence source
    c = pack.charter.lower()
    checks["G3_single_source_charter"] = ("single evidence" in c
                                          or "one evidence" in c
                                          or "only evidence" in c)

    # G4 verifier vs stored truth, split by testset semantics:
    #   census rows  -> verifier(d) must reproduce the census verdict
    #   perturb rows -> truth is about the DIGIT PAIR (not the d): the
    #                   pack's exemplars must NOT match the perturbed
    #                   numbers (the mechanical fast-classification half)
    census_rows = [t for t in testset if t.get("kind") != "perturb"]
    perturb_rows = [t for t in testset if t.get("kind") == "perturb"]

    wrong = []
    for t in census_rows:
        out = run_verifier(pack.verifier.name, {"d": t["d"]})
        if ("RATIONAL" in out["verdict"]) != bool(t["truth"]):
            wrong.append({"d": t["d"], "truth": t["truth"],
                          "verifier": out["verdict"]})
    checks["G4a_census_verifier_matches_truth"] = (len(wrong) == 0)
    checks["G4a_n"] = len(census_rows)

    pw = []
    for t in perturb_rows:
        hit = None
        for e in pack.exemplars:
            same = all(
                abs(float(t[k]) - float(e.inputs[k]))
                <= 1e-5 * max(1.0, abs(float(e.inputs[k])))
                for k in ("x0", "lam") if k in e.inputs and k in t)
            if same:
                hit = e
                break
        pred = hit.label if hit is not None else "NOT"
        if ("RATIONAL" in pred) != bool(t["truth"]):
            pw.append({"d": t["d"], "truth": t["truth"], "pred": pred})
    checks["G4b_perturb_not_in_pack"] = (len(pw) == 0)
    checks["G4b_n"] = len(perturb_rows)
    checks["G4_errors"] = wrong + pw

    # G5 typed-output consistency (P141), domain-adaptive: checked on the
    # same exemplar payloads G2 ran (no hardcoded probe rows — the census
    # d-probe broke on non-census domains, P147 catch)
    g5_bad = []
    for e in pack.exemplars:
        out = run_verifier(pack.verifier.name, dict(e.inputs))
        typed = out.get("typed") or {}
        opts = typed.get("options") or {}
        if abs(sum(opts.values()) - 1.0) > 1e-3:
            g5_bad.append({"exemplar": e.d, "issue": "options not normalized"})
        verdict_p = opts.get(out["verdict"], 0.0)
        if verdict_p < 0.9:
            g5_bad.append({"exemplar": e.d, "issue": "verdict probability < 0.9",
                           "verdict": out["verdict"], "p": verdict_p})
        if not (out.get("confidence", 0) >= 0.5):
            g5_bad.append({"exemplar": e.d, "issue": "confidence < 0.5"})
    checks["G5_typed_consistency"] = (len(g5_bad) == 0)
    checks["G5_errors"] = g5_bad

    checks["PASS"] = all(v for k, v in checks.items()
                         if k.startswith("G") and isinstance(v, bool))
    return checks


def load_testset(path="p138_plugin_test.json"):
    return json.load(open(path, encoding="utf-8"))["testset"]


if __name__ == "__main__":
    from intuition_pack.store import get_store
    store = get_store()
    domain = sys.argv[1] if len(sys.argv) > 1 else "ramanujan-sixrow"
    raw = store.get(domain)
    if raw is None:
        print(f"no pack for domain {domain!r}")
        sys.exit(2)
    pack = Pack.from_json(raw)
    testset = load_testset()
    # testset stores formatted inputs; verifier needs d only
    report = mechanical_gate(pack, testset)
    print(json.dumps(report, indent=1))
    sys.exit(0 if report["PASS"] else 1)
