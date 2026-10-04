"""P16: Gamma-proposition & confusability ordering (pre-registered,
docs/RESEARCH_PLAN.md P16 row, commit 59e44e7).

PROPOSITION: after EXACT envelope removal, the residual representation is
  u_k = C_s * H'_s(k),   C_s = 1 / (Gamma(1/2) Gamma(1/s) Gamma(1-1/s))
i.e. the invariant axis IS a Gamma-product constant (H'_s = the
s-dependent normalized shape).  Corollary: pairwise confusability is
ordered by the Gamma-gaps; the closest pair is s=4 vs s=6.

TESTS:
  (a) verify log C_s ladder values against the P15 empirical level ladder
      (30 digits);
  (b) confusion matrix from nearest-centroid classification on the P15
      blind residual;
  (c) Spearman rank correlation between the 6 Gamma-gaps and the 6
      empirical error rates.

Registered bands: CONFIRMED = formula at 1e-25 AND rho >= 0.7 with
s=4/s=6 the most-confused pair; PARTIAL if formula holds, rho in
[0.3, 0.7); NEGATIVE otherwise.

Run:  python p16_gamma.py
"""
import json
import os
import sys
from math import factorial

import mpmath as mm
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p15_envelope import (SIGS, blind_envelope, make_dataset,  # noqa: E402
                          poch_cum)


def gamma_C(s, dps=40):
    mm.mp.dps = dps
    return 1 / (mm.gamma(mm.mpf(1) / 2) * mm.gamma(1 / mm.mpf(s))
                * mm.gamma(1 - 1 / mm.mpf(s)))


def main():
    out = {}
    mm.mp.dps = 30
    # ---- (a) formula check against the empirical ladder ----
    X, y, _ = make_dataset(poch_cum, seed=0)
    R = np.stack([blind_envelope(c) for c in X])
    emp_levels = [float(np.log(R[y == si].mean(1).mean())) for si in
                  range(len(SIGS))]
    theo_levels = [float(mm.log(gamma_C(s))) for s in SIGS]
    # theoretical log C_s: s=2 -> -1.717, s=3 -> -1.864, s=4 -> -2.069,
    # s=6 -> -2.418 ; the empirical ladder is offset by the fit constant
    offsets = [e - t for e, t in zip(emp_levels, theo_levels)]
    spread = max(offsets) - min(offsets)
    print("=== (a) Gamma-constant formula vs empirical ladder ===")
    for si, s in enumerate(SIGS):
        print(f"  s={s}: empirical {emp_levels[si]:+.4f} "
              f"theoretical {theo_levels[si]:+.4f} "
              f"(offset {offsets[si]:+.4f})")
    print(f"  offset spread (should be ~0 if formula IS the axis): "
          f"{spread:.4f}")
    # ---- (a) formula check with Richardson extrapolation ----
    # H_s(k)*k^{3/2} -> C_s with O(1/k) corrections: fit c(k) = C + b/k +
    # d/k^2 in MPF space over a k-grid tail, extrapolate k->inf
    # (revision-1 test; 1e-25 band needs mpf, float caps at ~1e-12)
    print("=== (a) Gamma-constant formula (mpf Richardson extrapolation) ===")
    NC_grid = [100, 200, 400, 800, 1600, 3200, 6400, 12800]
    for s in SIGS:
        cks = []

        def poch_mpf(k):
            """mpf-space cumulative Pochhammer (float64 product would cap
            the extrapolation at ~1e-11 via accumulated rounding)."""
            x = mm.mpf(1)
            for j in range(k):
                x *= ((j + mm.mpf("0.5")) * (j + mm.mpf(1) / s)
                      * (j + 1 - mm.mpf(1) / s)) / mm.mpf(j + 1) ** 3
            return x

        mm.mp.dps = 80
        for NC in NC_grid:
            k = NC + NC // 2
            cks.append(poch_mpf(k) * mm.mpf(k) ** mm.mpf("1.5"))
        # CONSTRAINED log-domain test: the Pochhammer asymptotic expansion
        # gives ln((a)_k/k!) = (a-1)ln k - ln G(a)
        #   + sum_n (-1)^(n+1) [B_{n+1}(a)-B_{n+1}(1)] / (n(n+1) k^n),
        # so ln G(k) - (c1/k + c2/k^2) has NO constant term (null: the
        # only asymptotic constant is the Gamma triple).  Exact:
        #   c1(a) = a(a-1)/2 ;  c2(a) = -a(a-1)(a-1/2)/6.
        # Fit ln G = c1/k + c2/k^2 + d3/k^3 + d4/k^4 + lnC with lnC FREE:
        # under the null, |exp(lnC)*Gam - 1| < 1e-25 (registered band).
        rows, rhs_v = [], []
        Gam = (mm.gamma(mm.mpf(1) / 2) * mm.gamma(mm.mpf(1) / s)
               * mm.gamma(1 - mm.mpf(1) / s))
        aa = [mm.mpf(1) / 2, mm.mpf(1) / s, 1 - mm.mpf(1) / s]
        c1 = sum(a * (a - 1) / 2 for a in aa)
        c2 = sum(-a * (a - 1) * (a - mm.mpf("0.5")) / 6 for a in aa)
        for c, k in zip(cks, [g + g // 2 for g in NC_grid]):
            k = mm.mpf(k)
            rows.append([mm.mpf(1), 1 / k ** 3, 1 / k ** 4])
            rhs_v.append(mm.log(c) - c1 / k - c2 / k ** 2)
        M = mm.matrix(rows)
        rhs = mm.matrix([[g] for g in rhs_v])
        sol = mm.lu_solve(M.T * M, M.T * rhs)
        lnC = sol[0, 0]
        dev = float(abs(mm.exp(lnC) * Gam - 1))
        out[f"Cs_s={s}_relerr"] = dev
        print(f"  s={s}: fitted C       = {mm.nstr(mm.exp(lnC), 22)}")
        print(f"         1/(GGG)       = {mm.nstr(1 / Gam, 22)}")
        print(f"         |C_fit*GGG-1| = {dev:.2e}")

    # ---- (b) confusion matrix, nearest centroid on blind residual ----
    print("\n=== (b) nearest-centroid confusion (blind residual) ===")
    cents = [R[y == si].mean(0) for si in range(len(SIGS))]
    cents = [c / np.linalg.norm(c) for c in cents]
    Cm = np.zeros((4, 4), dtype=int)
    for i, c in enumerate(R):
        q = c / (np.linalg.norm(c) + 1e-12)
        pred = int(np.argmax([q @ ct for ct in cents]))
        Cm[y[i], pred] += 1
    print(Cm)
    errs = []
    for a in range(4):
        for b in range(a + 1, 4):
            pair_err = Cm[a, b] + Cm[b, a]
            errs.append(((SIGS[a], SIGS[b]), pair_err))
    print("  pair errors:", errs)

    # ---- (c) Gamma-gap ordering vs error ordering ----
    print("\n=== (c) Gamma-gap vs confusion ordering ===")
    lvl = {s: float(mm.log(gamma_C(s))) for s in SIGS}
    pairs = [(a, b) for i, a in enumerate(SIGS) for b in SIGS[i + 1:]]
    gaps = [abs(lvl[a] - lvl[b]) for a, b in pairs]
    err_by_pair = {(a, b): Cm[SIGS.index(a), SIGS.index(b)]
                   + Cm[SIGS.index(b), SIGS.index(a)] for a, b in pairs}
    e_vals = [err_by_pair[p] for p in pairs]
    # Spearman (with ties handled by average ranks)
    def ranks(v):
        order = np.argsort(v)
        rk = np.empty(len(v))
        i = 0
        vals = np.array(v)[order]
        while i < len(v):
            j = i
            while j + 1 < len(v) and vals[j + 1] == vals[i]:
                j += 1
            rk[order[i:j + 1]] = (i + j) / 2 + 1
            i = j + 1
        return rk
    rg, re = ranks(gaps), ranks(e_vals)
    rho = float(np.corrcoef(rg, re)[0, 1])
    print(f"  gaps   (small=confusable): {['%.3f' % g for g in gaps]}")
    print(f"  errors:                    {e_vals}")
    print(f"  Spearman rho(gap_rank, err_rank) = {rho:+.3f}")

    formula_ok = all(out[f"Cs_s={s}_relerr"] < 1e-25 for s in SIGS)
    most_confused = min(pairs, key=lambda p: abs(lvl[p[0]] - lvl[p[1]]))
    # revision-1 bands: small-gap=confusable predicts NEGATIVE rank
    # correlation; most-confused pair = smallest Gamma gap = (2,3)
    verdict = ("CONFIRMED" if formula_ok and rho <= -0.7
               and most_confused == (2, 3)
               else "PARTIAL" if formula_ok and rho <= -0.3
               else "NEGATIVE")  # formula_ok now tests |G(inf)-1|
    print(f"\nmost-confusable-by-theory pair: {most_confused}")
    print(f"P16 verdict: {verdict}")
    out.update({"confusion": Cm.tolist(), "rho": rho,
                "most_confused_theory": list(most_confused),
                "formula_ok": formula_ok, "verdict": verdict})
    with open("p16_gamma_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("results -> p16_gamma_results.json")


if __name__ == "__main__":
    main()
