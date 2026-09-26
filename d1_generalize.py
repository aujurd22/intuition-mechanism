"""Direction 1: generalize series_from_j to ALL 27 d (Heegner + class-number-2)
and sweep the full pipeline -- using the EXACT series_gen.py-validated path
(d=163 residual 1.6e-114 there).

Per d (all mechanical, no literature lookup):
  tau(d) -> nome q -> theta -> k2 -> j -> z = 1728/Re(j)
  -> S0, S1 (Chudnovsky rf/factorial sums, real z)
  -> A*S0 + B*S1 = base^(3/2)/(12*pi)
  -> integer recovery of (A, B) -> gate at 1e-40 relative

MISS list (d that fail) = primary data product: the measured map of which
steps resist mechanization.

Run:  python d1_generalize.py
"""
import json
import os
import sys

from mpmath import mp, mpc, mpf, sqrt, jtheta, exp, rf, factorial, power, pi

mp.dps = 120

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 640320


def cm_tau(d):
    if d % 4 == 3:
        return (1 + mpc(0, mpf(d) ** 0.5)) / 2
    return mpc(0, mpf(d) ** 0.5)


def j_of_tau(tau):
    q = exp(mpc(0, mp.pi) * tau)
    t2, t3 = jtheta(2, 0, q), jtheta(3, 0, q)
    k2 = (t2 / t3) ** 4
    return 256 * (1 - k2 + k2 ** 2) ** 3 / (k2 ** 2 * (1 - k2) ** 2)


def sum_S(z, terms=25):
    S0 = mpf(0)
    S1 = mpf(0)
    for k in range(terms):
        ck = (rf(mpf(1) / 2, k) * rf(mpf(1) / 6, k) * rf(mpf(5) / 6, k)
              / factorial(k) ** 3)
        ckz = ck * z ** k
        S0 += ckz
        S1 += k * ckz
    return S0, S1


def d_list():
    h1 = [1, 2, 3, 7, 11, 19, 43, 67, 163]
    h2 = [15, 20, 24, 35, 40, 51, 52, 88, 91, 115, 123, 148, 187, 232, 235,
          267, 403, 427]
    return h1 + h2


def main():
    rows = []
    n_hit = 0
    for d in d_list():
        tau = cm_tau(d)
        try:
            j = j_of_tau(tau)
            z = 1728 / mp.re(j)          # real z (negative => alternating)
            S0, S1 = sum_S(z)
            Y = power(BASE, mpf(3) / 2) / (12 * pi)
            A_raw = Y / S0
            B_raw = (Y - A_raw * S0) / S1
            A_int = int(mp.floor(mp.re(A_raw) + mpf('0.5')))
            B_int = int(mp.floor(mp.re(B_raw) + mpf('0.5')))
            rec = A_int * S0 + B_int * S1
            err = abs(rec - Y) / abs(Y)
            a_ok = abs(mp.re(A_raw) - A_int) < mpf(10) ** -30
            b_ok = abs(mp.re(B_raw) - B_int) < mpf(10) ** -30
            hit = bool(a_ok and b_ok and err < mpf(10) ** -40)
            rows.append({"d": d, "A": A_int, "B": B_int, "hit": hit,
                         "rel": mp.nstr(err, 3),
                         "A_exact_ok": a_ok, "B_exact_ok": b_ok})
            n_hit += hit
            status = "HIT" if hit else "MISS"
            print(f"  d={d:4d}  A={A_int}  B={B_int}  rel={mp.nstr(err, 3)}  "
                  f"{status}", flush=True)
        except Exception as e:
            rows.append({"d": d, "error": str(e)[:80]})
            print(f"  d={d:4d}  ERROR {str(e)[:60]}", flush=True)

    n = len(rows)
    miss = [r["d"] for r in rows if not r.get("hit")]
    print(f"\n=== D1 generalization: {n_hit}/{n} d produced integer (A,B) ===")
    print(f"  MISS list: {miss}")

    out = os.path.join(HERE, "d1_generalization_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"total": n, "hits": n_hit, "miss_list": miss,
                   "rows": rows}, f, ensure_ascii=False, indent=1,
                  default=str)
    print(f"results -> {out}")


if __name__ == "__main__":
    main()
