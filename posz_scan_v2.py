"""Direction 2 v2: positive-z family from the CM point, CONSTRUCTIVELY.

Theory (Borwein & Borwein, Pi and the AGM ch.5; Ramanujan 1914 families):
for a CM point with singular modulus k_d (k'^2 = 1 - k^2), the positive-z
Ramanujan form uses

    z_d = 4 k_d^2 k_d'^2          (for the s=2/4 kernels, per family)

The classical instances: d=1 -> k^2=1/2 -> z = 1/4 (eq28).  More generally
each signature s has its own algebraic z_d built from k_d^2.  We CONSTRUCT
z_d = 4 k^2 (1-k^2) and run the two-sum PSLQ per signature, then verify
the resulting series against 1/pi at the 1e-25 gate.

The lattice of candidate z forms per signature:
  s=2: z = 4 k2 (1-k2)
  s=4: z = -4 k2 (1-k2) ... (negative => alternating, eq35-39 group)
  s=3: z = 27/4 * k2 (1-k2)  ... etc -- we scan a small family of
       rational multiples q * k2(1-k2), q in a fixed rational set, and
       let the PSLQ gate decide which (s, q) combos are real.

Run:  python posz_scan_v2.py
"""
import json
import math
import os
import sys

from mpmath import mp, mpc, mpf, pi, sqrt, rf, factorial, jtheta, exp, pslq

mp.dps = 90

HERE = os.path.dirname(os.path.abspath(__file__))

# j>0 d from D1 v2 classification + the known anchors (d=1 for eq28 sanity)
D_LIST = [1, 2, 20, 24, 40, 52, 88, 148, 232]

# candidate prefactors q for z = q * k2*(1-k2).  The classical families:
#   eq28 (d=1, s=2): k2=1/2 -> k2 k2' = 1/4 -> z=1/4 needs q=1
#   eq29: z=1/64 (d=3, s=2): k2=(2-sqrt3)^2... q=1 with d=3? -- scan decides
QS = [mpf(1), mpf(1)/4, mpf(1)/2, mpf(2), mpf(4), mpf(27)/4, mpf(1)/16,
      mpf(3)/4, mpf(9)/4]
SIGNS = [2, 3, 4, 6]


def cm_tau(d):
    if d % 4 == 3:
        return (1 + mpc(0, mpf(d) ** 0.5)) / 2
    return mpc(0, mpf(d) ** 0.5)


def k2_of(d):
    q = exp(mpc(0, mp.pi) * cm_tau(d))
    t2, t3 = jtheta(2, 0, q), jtheta(3, 0, q)
    return (t2 / t3) ** 4


def H(k, s):
    return rf(mpf(1) / 2, k) * rf(mpf(1) / s, k) * rf(mpf(1) - 1 / mpf(s), k) \
        / factorial(k) ** 3


def sums(z, s, terms):
    S0 = S1 = mpf(0)
    for k in range(terms):
        h = H(k, s) * z ** k
        S0 += h
        S1 += k * h
    return S0, S1


def n_terms(z):
    az = abs(float(z))
    if az >= 1:
        return None
    return min(4000, int(math.ceil(-55 / math.log10(az))) + 30)


def main():
    rows = []
    hits = []
    print("control: d=1, q=1, s=2 should give eq28 (A,B,M)=(1,6,4)\n")
    for d in D_LIST:
        k2 = k2_of(d)
        kk = k2 * (1 - k2)
        for q in QS:
            z = q * mp.re(kk)
            if abs(z) >= 1 or abs(z) < mpf(10) ** -7:
                continue
            terms = n_terms(z)
            if terms is None:
                continue
            for s in SIGNS:
                S0, S1 = sums(z, s, terms)
                if abs(S0) < 1e-30:
                    continue
                rel = pslq([S0, S1, -1 / pi], tol=mpf(10) ** -35,
                           maxcoeff=10 ** 9)
                if rel is None:
                    continue
                A, B, M = rel
                if (A, B) == (0, 0) or M == 0:
                    continue
                if max(abs(A), abs(B), abs(M)) > 10 ** 8:
                    continue
                # independent verification: series sum -> pi
                total = mpf(0)
                for k in range(terms + 60):
                    total += (A + B * k) * H(k, s) * z ** k
                pi_pred = M / total
                err = abs(pi_pred - pi)
                if err < mpf(10) ** -25:
                    hit = {"d": d, "s": s, "q": mp.nstr(q, 8),
                           "z": mp.nstr(z, 20), "A": A, "B": B, "M": M,
                           "pi_err": mp.nstr(err, 3)}
                    hits.append(hit)
                    print(f"  d={d:4d} s={s} q={mp.nstr(q, 6)}: "
                          f"(A,B,M)=({A},{B},{M})  z={mp.nstr(z, 15)}  "
                          f"pi_err={mp.nstr(err, 3)}", flush=True)
        if not any(h["d"] == d for h in hits):
            print(f"  d={d:4d}  miss on all (s, q) combos", flush=True)
        rows.append({"d": d, "hit": any(h["d"] == d for h in hits)})

    print(f"\n=== positive-z v2: {len(hits)} integer relations found "
          f"across {len(D_LIST)} d ===")
    out = os.path.join(HERE, "posz_scan_v2_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"hits": hits, "rows": rows}, f, indent=1, default=str)
    print(f"results -> {out}")


if __name__ == "__main__":
    main()
