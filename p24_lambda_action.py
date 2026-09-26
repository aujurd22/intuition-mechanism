"""P24: class-group action on lambda (pre-registered,
docs/RESEARCH_PLAN.md P24 row).

For the quadratic-lambda rows (N = 2, 11, 19, 23, 25, 35, 43, 47):
each orbit form yields lambda_f.  Question: do all lambda_f of one N
satisfy the representative's quadratic (i.e. the class group conjugates
lambda within a fixed quadratic field, pairing the roots)?

Run:  python p24_lambda_action.py
"""
import json
import os
import sys
from math import comb, gcd, isqrt

import mpmath as mm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p19b_z12 import x12, rhs_identity  # noqa: E402
from p19_generate import t_seq  # noqa: E402

mm.mp.dps = 50

TS = t_seq(600)
ROWS = [2, 11, 19, 23, 25, 35, 43, 47]


def reduced_forms(D):
    forms = []
    amax = isqrt(-D // 3) + 1
    for a in range(1, amax + 1):
        for b in range(-a + 1, a + 1):
            if (b * b - D) % (4 * a):
                continue
            c = (b * b - D) // (4 * a)
            if c < a or (c == a and b < 0):
                continue
            if gcd(gcd(a, b), c) != 1:
                continue
            forms.append((a, b, c))
    return forms


def tsums(x0, N=600):
    S0 = mm.mpf(0)
    S1 = mm.mpf(0)
    xk = mm.mpf(1)
    n = 0
    for t in TS:
        S0 += t * xk
        S1 += n * t * xk
        xk *= x0
        n += 1
    return S0, S1


def main():
    out = {"rows": []}
    conf = 0
    for N in ROWS:
        D = -24 * N
        forms = reduced_forms(D)
        lams = []
        for (a, b, c) in forms:
            tau = (-b + mm.sqrt(mm.mpf(D))) / (2 * mm.mpf(a))
            qq = mm.exp(2 * mm.pi * 1j * tau)
            x0 = x12(qq)
            S0, S1 = tsums(x0)
            r = rhs_identity(N, x0)
            lams.append((r - S1) / S0)
        # REAL-lambda forms only (registered salvage): lambda_f is
        # complex for non-real tau forms; the quadratic-membership test
        # is defined on the real subset
        reals = [mm.mpf(l.real) for l in lams
                 if abs(mm.im(l)) < mm.mpf('1e-20')]
        if len(reals) < 2:
            print(f"  N={N}: <2 real lambdas, skip")
            continue
        lam_rep = reals[0]
        rel = mm.pslq([lam_rep ** 2, lam_rep, mm.mpf(1)],
                      tol=mm.mpf('1e-25'), maxcoeff=10 ** 6)
        if not rel:
            print(f"  N={N}: representative lambda not quadratic, skip")
            continue
        a2, b2, c2 = int(rel[0]), int(rel[1]), int(rel[2])
        disc = b2 * b2 - 4 * a2 * c2
        roots_ok = all(
            abs(a2 * mm.mpf(l) ** 2 + b2 * mm.mpf(l) + c2)
            < mm.mpf('1e-20') for l in reals)
        print(f"  N={N:3d}: forms={len(forms)} lambda-quad "
              f"{a2}v^2{b2:+d}v{c2:+d}=0 (disc {disc}) "
              f"real lambdas={n_real_roots} roots_ok={roots_ok}",
              flush=True)
        conf += int(roots_ok)
        out["rows"].append({"N": N, "quad": f"{a2}v^2{b2:+d}v{c2:+d}=0",
                            "disc": disc, "roots_ok": roots_ok,
                            "n_forms": len(forms)})
    frac = conf / len(ROWS)
    verdict = ("CONFIRMED" if frac >= 0.8 else
               "PARTIAL" if frac >= 0.5 else "NEGATIVE")
    out["verdict"] = verdict
    out["conf_fraction"] = round(frac, 3)
    print(f"\nmatch fraction: {frac:.2f}")
    print(f"P24 verdict: {verdict}")

    with open("p24_lambda_action_results.json", "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("results -> p24_lambda_action_results.json")


if __name__ == "__main__":
    main()
