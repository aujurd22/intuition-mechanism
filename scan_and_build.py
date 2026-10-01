"""scan_and_build: the generalization loop, automated (P147).

For each registered candidate domain in domains_to_scan.json:
  1. probe(domain items, mixed exemplar pool)   [P145 laws enforced]
  2. verdict -> COMPRESSION SIGNAL  => build pack + mechanical gate
             -> SATURATED           => record (no pack; zero-shot ceiling)
             -> TOXIC               => record (do not build)
State: packs/ (authority) + p147_scan_report.json (the scan log).
Usage: py -3 scan_and_build.py
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intuition_pack.pack import build_pack, Pack
from intuition_pack.store import get_store
from intuition_pack.regression import mechanical_gate

REGISTRY = {
    # verifier name -> module-level registered function is assumed loaded
    # by the domain spec file itself (each spec imports what it needs)
}


def scan(spec_path="domains_to_scan.json"):
    from intuition_pack.verifiers import run_verifier
    spec = json.load(open(spec_path, encoding="utf-8"))
    store = get_store()
    report = []
    for dom in spec["domains"]:
        name = dom["domain"]
        items = dom["items"]
        pool = dom["exemplar_pool"]
        # toxicity guard: mixed labels required (P145)
        labels = {it["passes"] for it in pool}
        if len(labels) < 2:
            report.append({"domain": name, "verdict": "POISONOUS-POOL"})
            continue
        # probe (mechanical part done externally per domain prompt fn;
        # here we run the registered verifier against truth for the
        # mechanical half + record the LLM probe result if provided)
        verify_ok = all(
            run_verifier(dom["verifier"], it["payload"])["verdict"]
            == ("PASS" if it["passes"] else "FAIL")
            for it in items)
        entry = {"domain": name, "verifier_consistent": verify_ok,
                 "probe": dom.get("probe_result", "not-run"),
                 "built": False}
        if dom.get("build", False) and dom.get("probe_result") in (
                "COMPRESSION SIGNAL (confirm with single-turn protocol)",
                "COMPRESSION (build the pack)"):
            pack = build_pack(name, dom["charter"], dom["exemplars"],
                              {"name": dom["verifier"],
                               "rule": dom["verifier_rule"]},
                              source=dom.get("source", ""),
                              triggers=dom.get("triggers"))
            version = store.put(name, pack.to_json())
            entry["built"] = True
            entry["version"] = version
            p2 = Pack.from_json(store.get(name))
            gate = mechanical_gate(p2, dom.get("gate_testset", []))
            entry["gate"] = {k: v for k, v in gate.items()
                             if isinstance(v, bool)}
        report.append(entry)
    json.dump(report, open("p147_scan_report.json", "w"), indent=1)
    return report


if __name__ == "__main__":
    for e in scan():
        print(json.dumps(e, ensure_ascii=False))
