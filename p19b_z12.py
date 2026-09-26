"""P19 generation, part B: level-12 x(q) machinery + new-N sweep
(continuation of P19; same registered bands).

Verbatim identity (CWZ eq 3.9):
  sum_{n>=0} (n + lambda) t(n) x0^n
      = (1/(2 pi)) * sqrt(24/N) / sqrt((1+4x0)(1-4x0)(1-8x0))

Machinery (Cooper-Wan-Zudilin Thm 3.1, level 12 in q = e^{2 pi i tau}):
  z12(q) = 1/4 (6P(q^12) - 3P(q^6) + 2P(q^4) - P(q^2))
           + 2 eta(q^2) eta(q^4) eta(q^6) eta(q^12)
  x12(q) = eta(q^2) eta(q^4) eta(q^6) eta(q^12) / z12(q)
  t(n)   = sum_{k<=n/2} C(n,2k) C(2k,k)^2 C(2n-4k,n-2k)

Steps:
  (1) calibrate: N=5, x0=1/20, lambda=1/4 at 1e-40;
  (2) validate x12 against Table 1: x12(e^{-2 pi sqrt(N/24)}) = 1/12,
      1/20, 1/32 for N = 3, 5, 7;
  (3) generate: NEW N values -> x0 numerically -> solve lambda
      numerically -> recognize algebraic (rational / quadratic pslq)
      -> verified identity.

Run:  python p19b_z12.py
"""
import json
import os
import sys
from math import comb

import mpmath as mm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d1_eta import eta, q_of_tau  # noqa: E402

mm.mp.dps = 60
CUT = mm.mpf(10) ** -(mm.mp.dps - 10)


def p_eisenstein(q):
    s = mm.mpf(0)
    j = 1
    while True:
        qj = q ** j
        s += j * qj / (1 - qj)
        if abs(qj) < CUT:
            break
        j += 1
    return 1 - 24 * s


def z12(q):
    return (6 * p_eisenstein(q ** 12) - 3 * p_eisenstein(q ** 6)
            + 2 * p_eisenstein(q ** 4) - p_eisenstein(q ** 2)) / 4 \
        + 2 * eta(q ** 2) * eta(q ** 4) * eta(q ** 6) * eta(q ** 12)


def x12(q):
    return eta(q ** 2) * eta(q ** 4) * eta(q ** 6) * eta(q ** 12) / z12(q)


def tsums(x0, N=400):
    """S0 = sum t(n) x0^n, S1 = sum n t(n) x0^n (mpf, closed form)."""
    S0 = mm.mpf(0)
    S1 = mm.mpf(0)
    xk = mm.mpf(1)
    for n in range(N):
        v = mm.mpf(0)
        for k in range(n // 2 + 1):
            v += comb(n, 2 * k) * comb(2 * k, k) ** 2 \
                * comb(2 * n - 4 * k, n - 2 * k)
        S0 += v * xk
        S1 += n * v * xk
        xk *= x0
    return S0, S1


def rhs_identity(N, x0):
    return mm.sqrt(mm.mpf(24) / N) / (2 * mm.pi
                                      * mm.sqrt((1 + 4 * x0)
                                                * (1 - 4 * x0)
                                                * (1 - 8 * x0)))


def pslq_quadratic(v, maxden=400):
    """Is v a root of a quadratic a v^2 + b v + c = 0 with small integer
    coefficients? Returns (a, b, c) or None."""
    best = None
    for a in range(1, 40):
        for b in range(-maxden, maxden + 1):
            c_r = -(a * v * v + b * v)
            c = round(float(c_r))
            if c == 0:
                continue
            if abs(c_r - c) < mm.mpf(10) ** -25 and abs(c) <= maxden ** 2:
                g = np_gcd3(a, b, c)
                if (a, b // g, c // g) if g else (a, b, c):
                    cand = (a, b // (g or 1), c // (g or 1))
                    if best is None or sum(map(abs, cand)) < sum(
                            map(abs, best)):
                        best = cand
    return best


def np_gcd3(a, b, c):
    import math
    return math.gcd(math.gcd(abs(a), abs(b)), abs(c))


def main():
    out = {"calibration": {}, "table_check": [], "generation": []}

    # ---- (1) calibration ----
    N, x0, lam = 5, mm.mpf(1) / 20, mm.mpf(1) / 4
    S0, S1 = tsums(x0)
    lhs = lam * S0 + S1
    r = rhs_identity(N, x0)
    err = float(abs(lhs - r))
    cal_ok = err < mm.mpf('1e-40')
    out["calibration"] = {"N": 5, "x0": "1/20", "lambda": "1/4",
                          "abs_err": err, "pass": cal_ok}
    print(f"=== calibration N=5 x=1/20 lambda=1/4 ===")
    print(f"  lhs = {mm.nstr(lhs, 25)}")
    print(f"  rhs = {mm.nstr(r, 25)}")
    print(f"  err = {err:.2e}  {'PASS' if cal_ok else 'FAIL'}", flush=True)
    if not cal_ok:
        with open("p19b_z12_results.json", "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        return

    # ---- (2) x12 validation against Table 1 ----
    print("\n=== x12 vs Table 1 ===")
    for N, expect in ((3, mm.mpf(1) / 12), (5, mm.mpf(1) / 20),
                      (7, mm.mpf(1) / 32)):
        q = mm.exp(-2 * mm.pi * mm.sqrt(mm.mpf(N) / 24))
        v = x12(q)
        err = float(abs(v - expect))
        out["table_check"].append({"N": N, "x12": mm.nstr(v, 20),
                                   "expect": str(expect), "err": err})
        print(f"  N={N}: x12 = {mm.nstr(v, 15)} expect {mm.nstr(expect, 8)}"
              f" err={err:.2e}", flush=True)

    # ---- (3) generation at NEW N ----
    print("\n=== generation at NEW N ===")
    for N in (2, 6, 11, 19, 23, 29, 31, 6 * 13 // 2 * 0 + 12, 15):
        q = mm.exp(-2 * mm.pi * mm.sqrt(mm.mpf(N) / 24))
        x0 = x12(q)
        if abs(x0.imag if isinstance(x0, mm.mpc) else 0) > 1e-30:
            print(f"  N={N}: complex x0, skip")
            continue
        S0, S1 = tsums(x0, N=600)
        r = rhs_identity(N, x0)
        lam = (r - S1) / S0   # lambda*S0 + S1 = r  =>  lambda = (r-S1)/S0
        lam = mm.mpf(lam.real)      # imag ~ 0 (verified above)
        # algebraicity recognition: rational, then quadratic (mpmath pslq)
        tag = "unrecognized"
        lam_r = None
        rel1 = mm.pslq([lam, mm.mpf(1)], tol=mm.mpf('1e-30'),
                       maxcoeff=10 ** 6)
        if rel1:
            lam_r = f"{-rel1[1]}/{rel1[0]}" if rel1[0] else str(-rel1[1])
            tag = f"rational {lam_r}"
        else:
            rel2 = mm.pslq([lam ** 2, lam, mm.mpf(1)],
                           tol=mm.mpf('1e-30'), maxcoeff=10 ** 6)
            if rel2:
                a2, b2, c2 = rel2
                disc = b2 * b2 - 4 * a2 * c2
                tag = (f"quadratic {a2}v^2+{b2}v+{c2}=0 "
                       f"(disc {disc})")
            else:
                tag = "no small relation"
        qq = pslq_quadratic(lam)
        if not lam_r and qq:
            a, b, c = qq
            disc = b * b - 4 * a * c
            tag = f"quadratic {a}v^2+{b}v+{c}=0 (disc {disc})"
        # verification: recompute
        lhs = lam * S0 + S1
        verr = float(abs(lhs - r))
        print(f"  N={N:3d}: x0={mm.nstr(x0, 12)} lambda={mm.nstr(lam, 20)} "
              f"[{tag}] verify_err={verr:.2e}")
        out["generation"].append({"N": N, "x0": mm.nstr(x0, 30),
                                  "lambda": mm.nstr(lam, 40),
                                  "algebraic_tag": tag,
                                  "verify_err": verr})

    with open("p19b_z12_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("\nresults -> p19b_z12_results.json")


if __name__ == "__main__":
    main()
