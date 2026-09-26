"""P26-b: branch-constant measurement at the dominant singularity
(pre-registered, docs/RESEARCH_PLAN.md P26-b row, commit 3fad656).

At the dominant singularity x = 1/8 (approached as N -> 1+ along
tau = i*sqrt(N/24)): sample (x_N, z_N) from the verified level-12
machinery, fit z = z0 + c*sqrt(1-8x) linear in s = sqrt(1-8x), then
pslq-recognize c.  Registered prediction: t(n) ~ -c/(2 sqrt(pi))
8^n n^-3/2, so K = -c/(2 sqrt(pi)) should reproduce the P26 value
1.4344.

Run:  python p26b_branch.py
"""
import json
import os
import sys

import mpmath as mm
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p19b_z12 import x12, z12  # noqa: E402

mm.mp.dps = 60


def main():
    Ns = [1.02, 1.05, 1.1, 1.2, 1.4, 1.7, 2.0, 2.5, 3.0, 4.0]
    pts = []
    for Nf in Ns:
        q = mm.exp(-2 * mm.pi * mm.sqrt(mm.mpf(str(Nf)) / 24))
        xv = mm.mpf(x12(q).real)
        zv = mm.mpf(z12(q).real)
        s = mm.sqrt(1 - 8 * xv)
        pts.append((s, zv))
        print(f"  N={Nf:5.2f}: x={mm.nstr(xv, 12)} s={mm.nstr(s, 10)} "
              f"z={mm.nstr(zv, 12)}", flush=True)

    # fit z = z0 + c*s (+ s^2 curvature term), c = the branch constant
    S = np.array([float(p[0]) for p in pts])
    Z = np.array([float(p[1]) for p in pts])
    A = np.vstack([np.ones(len(S)), S, S ** 2]).T
    coef, *_ = np.linalg.lstsq(A, Z, rcond=None)
    z0_fit, c_fit = float(coef[0]), float(coef[1])
    resid = float(np.max(np.abs(Z - A @ coef)))
    K = -c_fit / (2 * mm.sqrt(mm.pi))
    print(f"  fit: z0 = {z0_fit:.12f}  c = {c_fit:.12f}  max|res| = "
          f"{resid:.2e}")
    print(f"  K = -c/(2 sqrt(pi)) = {float(K):.12f}  (P26 measured "
          f"1.4344044258)")

    fit_ok = resid < 1e-12
    k_match = abs(float(K) - 1.4344044258) < 1e-6
    verdict = ("CONFIRMED" if fit_ok and k_match else
               "PARTIAL" if fit_ok else "NEGATIVE")
    print(f"\nP26-b verdict: {verdict}")

    out = {"Ns": Ns, "s_values": [float(p[0]) for p in pts],
           "z_values": [float(p[1]) for p in pts],
           "z0_fit": z0_fit, "c_fit": c_fit, "max_resid": float(resid),
           "K": float(K), "K_target": 1.4344044258, "verdict": verdict}
    with open("p26b_branch_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("results -> p26b_branch_results.json")


if __name__ == "__main__":
    main()
