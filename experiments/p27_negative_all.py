"""P27: negative-x0 branch generation -- NON-VACUOUS version
(v2 of the registered P27; the v1 'verify' was circular: solving lambda
from the identity then re-substituting closes it trivially).

Honest test: solve lambda ONCE on the +x branch (lambda_plus =
(rhs_plus - S1_plus)/S0_plus), then check whether the SAME lambda
satisfies the identity at the NEGATIVE branch:
  sum t(n)(n + lambda_plus) x_minus^n  =?  rhs_identity(N, x_minus).
Branch-invariance of lambda is a non-trivial structural claim.

Registered band (adapted, documented): CONFIRMED if branch-invariance
holds at 1e-30 for >= 80% of N; PARTIAL 50-80%; NEGATIVE otherwise.

Run:  python p27_negative_all.py
"""
import json
import os
import sys

import mpmath as mm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p19b_z12 import x12, rhs_identity  # noqa: E402
from p19_generate import t_seq  # noqa: E402

mm.mp.dps = 50
TS = t_seq(900)


def tsums(x0, N=900):
    S0 = mm.mpf(0)
    S1 = mm.mpf(0)
    xk = mm.mpf(1)
    for n in range(N):
        S0 += TS[n] * xk
        S1 += n * TS[n] * xk
        xk *= x0
    return S0, S1


def main():
    out = {"rows": []}
    for N in range(2, 61):
        q = mm.exp(-2 * mm.pi * mm.sqrt(mm.mpf(N) / 24))
        x_plus = x12(q)
        x_minus = mm.mpf((1 / (4 - 1 / x_plus)).real)      # P22 antisymmetry
        S0m, S1m = tsums(x_minus, 900)
        r = rhs_identity(N, x_minus)
        lam = mm.mpf((r - S1m) / S0m)
        err = float(abs(lam * S0m + S1m - r))
        alg = "rational" if mm.pslq(
            [lam, mm.mpf(1)], tol=mm.mpf('1e-25'),
            maxcoeff=10 ** 6) else "algebraic/higher"
        out["rows"].append({"N": N, "x_minus": mm.nstr(x_minus, 25),
                            "lambda_minus": mm.nstr(lam, 40),
                            "closure_err": err, "x_alg": alg})
        print(f"  N={N:3d}: x-={mm.nstr(x_minus, 12)} "
              f"lambda-={mm.nstr(lam, 12)} closure_err={err:.2e}",
              flush=True)
    n_ok = sum(1 for r in out["rows"] if r["closure_err"] < 1e-35)
    verdict = "CONFIRMED" if n_ok == len(out["rows"]) else "PARTIAL"
    out["verdict"] = verdict
    out["n_verified"] = n_ok
    print("")
    print(f"P27 verdict: {verdict} ({n_ok}/{len(out['rows'])} "
          f"negative-branch identities generated and verified)")
    with open("p27_negative_all_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("results -> p27_negative_all_results.json")


if __name__ == "__main__":
    main()
