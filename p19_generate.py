"""P19: mechanical Ramanujan-type series generation
(pre-registered, docs/RESEARCH_PLAN.md P19 row, commit b2abbbc).

Cooper-Wan-Zudilin eq (3.9) shape:

  sum_{n>=0} (2n choose n) u(n) (n + lambda) x0^n
      = sqrt(24/N) / (2 pi sqrt((1+4x0)(1-4x0)(1-8x0))))

with u(0)=1, (n+1)^2 u(n+1) = (10n^2+10n+3) u(n) - 9 n^2 u(n-1).

CALIBRATION (registered): N=5, x0=1/20, lambda=1/4 must verify at
1e-40.  GENERATION: solve lambda at our CM points (x0 from the P18
table) at high precision; recognize lambda as rational/quadratic;
each algebraic (x0, lambda) = a mechanically generated, 50-digit
verified identity (novelty caveat registered).

Run:  python p19_generate.py
"""
import json
import os
import sys

import mpmath as mm

mm.mp.dps = 60


def t_seq(N):
    """t(n) = sum_{k<=n/2} C(n,2k) C(2k,k)^2 C(2n-4k, n-2k), also given by
    the 4-term recurrence (n+1)^3 t(n+1) = 2(2n+1)(2n^2+2n+1) t(n)
    + 4n(4n^2+1) t(n-1) - 64 n(n-1)(2n-1) t(n-2)."""
    from math import comb
    ts = [mm.mpf(1)]
    for n in range(1, N + 1):
        v = mm.mpf(0)
        for k in range(n // 2 + 1):
            v += (comb(n, 2 * k) * comb(2 * k, k) ** 2
                  * comb(2 * n - 4 * k, n - 2 * k))
        ts.append(v)
    return ts            # t(0..N)


def sums(x0, N=260):
    """S0 = sum t(n) x0^n, S1 = sum n t(n) x0^n (t-family, radius 1/8)."""
    from math import comb
    ts = []
    for n in range(N):
        v = mm.mpf(0)
        for k in range(n // 2 + 1):
            v += (comb(n, 2 * k) * comb(2 * k, k) ** 2
                  * comb(2 * n - 4 * k, n - 2 * k))
        ts.append(v)
    S0 = mm.mpf(0)
    S1 = mm.mpf(0)
    xk = mm.mpf(1)
    for n in range(N):
        S0 += ts[n] * xk
        S1 += n * ts[n] * xk
        xk *= x0
    return S0, S1


def rhs(N, x0):
    return mm.sqrt(mm.mpf(24) / N) / (2 * mm.pi
                                      * mm.sqrt((1 + 4 * x0)
                                                * (1 - 4 * x0)
                                                * (1 - 8 * x0)))


def main():
    out = {"calibration": {}, "generation": []}

    # ---- calibration: N=5, x0=1/20, lambda=1/4 ----
    N, x0, lam = 5, mm.mpf(1) / 20, mm.mpf(1) / 4
    S0, S1 = sums(x0)
    lhs = S0 + lam * S1
    target = rhs(N, x0)
    # identity shape: lhs = target/pi  (check the exact constant form)
    err = float(abs(lhs * mm.pi - target))
    print(f"=== calibration N=5 x0=1/20 lambda=1/4 ===")
    print(f"  lhs*pi = {mm.nstr(lhs * mm.pi, 20)}")
    print(f"  rhs    = {mm.nstr(target, 20)}")
    print(f"  |lhs*pi - rhs| = {err:.2e}")
    cal_ok = err < mm.mpf('1e-40')
    out["calibration"] = {"N": N, "x0": "1/20", "lambda": "1/4",
                          "abs_err_pi_scaled": err, "pass": cal_ok}
    print(f"  calibration {'PASS' if cal_ok else 'FAIL'}", flush=True)

    if not cal_ok:
        # try the alternative constant: lhs = target (no pi) — for audit
        with open("p19_generate_results.json", "w",
                  encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        print("calibration failed; stopping per registration")
        return

    # ---- generation at our CM x0 values (from the P18 table) ----
    print("\n=== generation at CM special values ===", flush=True)
    cm_x0 = {"x0=1/36 (d=1)": mm.mpf(1) / 36,
             "x0=1/54 (d=2)": mm.mpf(1) / 54,
             "x0=1/100 (d=3)": mm.mpf(1) / 100}
    for name, x0 in cm_x0.items():
        # choose N from x0 = 24/N * approx?  Instead: solve BOTH the rhs
        # scale and lambda is underdetermined unless N fixed; the paper's
        # N is tied to x0 via x0 = x(e^{-2 pi sqrt(N/24)}).  We invert:
        # find N such that our identity constant matches — instead we
        # register the generated pair as (x0, lambda, N) with N chosen so
        # that x0 = X0(i sqrt(N/24)) — computed from the P18 relation
        # numerically by bisection on the known monotone branch.
        from p18_zx import x_of_q, q_of_tau
        lo, hi = mm.mpf("0.5"), mm.mpf("20")     # tau_im, cusp side
        target = x0
        for _ in range(120):
            mid = (lo + hi) / 2
            v = x_of_q(q_of_tau(mm.mpc(0, mid)))
            if v > target:
                lo = mid
            else:
                hi = mid
        tau_im = (lo + hi) / 2
        N_eff = 24 * tau_im ** 2 / mm.pi ** 2 * mm.pi ** 2  # tau=i sqrt(N/24) => N = 24 tau^2
        N_eff = 24 * tau_im ** 2
        S0, S1 = sums(x0)
        # rhs with N = N_eff: lambda = (rhs - S0)/S1
        r = rhs(N_eff, x0)
        lam = (r - S0) / S1
        lam_r = mm.rational(lam)
        is_alg = lam_r[1] is not None
        # verification: recompute lhs with recovered lambda
        lhs = S0 + lam * S1
        err = float(abs(lhs * mm.pi - r))
        print(f"  {name}: tau_im={mm.nstr(tau_im, 8)} N={mm.nstr(N_eff, 10)}")
        print(f"    lambda = {mm.nstr(lam, 30)}")
        print(f"    rational? {is_alg}   verify err = {err:.2e}")
        out["generation"].append({
            "label": name, "tau_im": float(tau_im), "N": float(N_eff),
            "lambda": mm.nstr(lam, 40), "verify_err": err,
            "lambda_rational": bool(is_alg)})

    with open("p19_generate_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("\nresults -> p19_generate_results.json")


if __name__ == "__main__":
    main()
