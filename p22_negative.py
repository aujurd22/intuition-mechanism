"""P22: negative-branch generation + symmetry identity
(pre-registered, docs/RESEARCH_PLAN.md P22 row, commit 42c6cce).

  (i)   symmetry: 1/x(q) + 1/x(-q) = 4  at 3+ tau  (1e-30);
  (ii)  the five NEGATIVE-column Table-1 rows:
        N=3  x=-1/8   lambda=1/2
        N=5  x=-1/16  lambda=2/5
        N=7  x=-1/28  lambda=1/3
        N=13 x=-1/100 lambda=3/13
        N=17 x=-1/196 lambda=67/340
        identity: sum t(n)(n+lambda)x^n = (1/(2pi))sqrt(24/N)
                  / sqrt((1+4x)(1-4x)(1-8x))   at 1e-40.

Run:  python p22_negative.py
"""
import json
import os
import sys

import mpmath as mm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p19b_z12 import x12, tsums, rhs_identity  # noqa: E402

mm.mp.dps = 60

ROWS = [(3, mm.mpf(-1) / 8, mm.mpf(1) / 2),
        (5, mm.mpf(-1) / 16, mm.mpf(2) / 5),
        (7, mm.mpf(-1) / 28, mm.mpf(1) / 3),
        (13, mm.mpf(-1) / 100, mm.mpf(3) / 13),
        (17, mm.mpf(-1) / 196, mm.mpf(67) / 340)]


def main():
    out = {}

    print("=== (i) symmetry 1/x(q) + 1/x(-q) = 4 ===", flush=True)
    sym_ok = True
    for tau_im in ("0.5", "0.7", "1.0"):
        q = mm.exp(-2 * mm.pi * mm.mpf(tau_im))
        xq = x12(q)
        xm = x12(-q)
        v = 1 / xq + 1 / xm
        err = float(abs(v - 4))
        sym_ok = sym_ok and err < mm.mpf('1e-30')
        print(f"  tau={tau_im}i: 1/x(q)+1/x(-q) = {mm.nstr(v, 12)} "
              f"err={err:.2e}", flush=True)
    out["symmetry_ok"] = sym_ok

    print("\n=== (ii) negative-branch identities ===", flush=True)
    rows = []
    all_ok = True
    for N, x0, lam in ROWS:
        S0, S1 = tsums(x0, N=900)
        lhs = lam * S0 + S1
        r = rhs_identity(N, x0)
        err = float(abs(lhs - r))
        ok = err < mm.mpf('1e-40')
        all_ok = all_ok and ok
        rows.append({"N": N, "x0": str(x0), "lambda": str(lam),
                     "abs_err": err, "pass": ok})
        print(f"  N={N:3d} x={str(x0)[:8]:9s} lam={str(lam)[:7]:7s} "
              f"err={err:.2e} {'PASS' if ok else 'FAIL'}", flush=True)
    out["rows"] = rows
    verdict = ("CONFIRMED" if sym_ok and all_ok else
               "PARTIAL" if sym_ok or all_ok else "NEGATIVE")
    out["verdict"] = verdict
    print(f"\nP22 verdict: {verdict}")

    with open("p22_negative_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("results -> p22_negative_results.json")


if __name__ == "__main__":
    main()
