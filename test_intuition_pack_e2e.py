"""End-to-end v1 test: build the ramanujan-sixrow pack from the P121
census, store it, reload it, execute the verifier, run the gate.
Also exercises the FlyMemoryStore probe (auto backend selection).
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intuition_pack.pack import build_pack, Pack
from intuition_pack.store import get_store, LocalFileStore
from intuition_pack.verifiers import run_verifier, lambert_one_over_x6
from intuition_pack.regression import mechanical_gate, load_testset

DOMAIN = "ramanujan-sixrow"
CHARTER = ("Single evidence source: the stored exemplar set below is the "
           "exhaustively verified rational locus; judge a candidate by "
           "matching it against these exemplars, then CONFIRM by executing "
           "the registered verifier. Never weigh raw numbers yourself.")

LOCUS = [1, 3, 5, 7, 13, 17]
EXEMPLARS = []
for d, v in zip(LOCUS, [8, 12, 20, 32, 104, 200]):
    from p33_n20 import params_for
    x0, lam = params_for(d)
    EXEMPLARS.append({"d": d,
                      "inputs": {"x0": f"{x0:.6f}", "lam": f"{lam:.6f}", "d": d},
                      "label": "RATIONAL", "note": f"1/x6 = {v}"})
# near-boundary contrast exemplar: d=10 (2-elementary but NOT rational)
from p33_n20 import params_for as pf
x0, lam = pf(10)
EXEMPLARS.append({"d": 10, "inputs": {"x0": f"{x0:.6f}", "lam": f"{lam:.6f}",
                                      "d": 10},
                  "label": "NOT", "note": "2-elementary yet irrational: the "
                  "nearest miss in the locus — do not generalize from "
                  "'small d' or '2-elementary'"})


def main():
    print("== backend selection ==")
    store = get_store()
    print("  store:", type(store).__name__)

    print("== build + store ==")
    pack = build_pack(DOMAIN, CHARTER, EXEMPLARS,
                      {"name": "lambert_sixrow",
                       "rule": "verifier(1/x6) integer to 1e-12 => RATIONAL"},
                      source="P121 census + P138 protocol")
    version = store.put(DOMAIN, pack.to_json())
    print(f"  stored version {version}, {len(pack.exemplars)} exemplars")

    print("== atomic reload ==")
    raw = store.get(DOMAIN)
    pack2 = Pack.from_json(raw)
    assert pack2.charter == pack.charter and len(pack2.exemplars) == len(pack.exemplars)
    print(f"  roundtrip OK (version {pack2.version})")
    print("  prompt_block preview:")
    for line in pack2.prompt_block().splitlines()[:6]:
        print("   ", line[:90])

    print("== verifier execution (agent-side, P138 rule) ==")
    for d, expect in [(3, "RATIONAL"), (17, "RATIONAL"), (35, "NOT"),
                      (10, "NOT"), (77, "NOT")]:
        out = run_verifier("lambert_sixrow", {"d": d})
        ok = out["verdict"] == expect
        print(f"  d={d:>3}: {out['verdict']:>8} (expect {expect}) "
              f"value={out['value']:.6f} {'OK' if ok else 'MISMATCH'}")
        assert ok

    print("== mechanical regression gate ==")
    testset = load_testset()
    report = mechanical_gate(pack2, testset)
    print(json.dumps({k: v for k, v in report.items()
                      if k != "G2_disagreements" and k != "G4_errors"}, indent=1))
    assert report["PASS"], report
    print("GATE PASS")

    print("== flymemory probe ==")
    from intuition_pack.store import FlyMemoryStore
    try:
        s = FlyMemoryStore()
        s._rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                              "clientInfo": {"name": "probe", "version": "0"}})
        print("  flymemory reachable: True (production backend available)")
    except Exception as e:
        print("  flymemory reachable: False (", str(e)[:60], ") — local backend active")

    print("\nE2E PASS")


if __name__ == "__main__":
    main()
