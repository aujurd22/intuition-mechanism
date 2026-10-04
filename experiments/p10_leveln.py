"""P10 (parent-run, v2): positive-z family via level-n singular moduli.

Construction (mechanical): for base discriminant d (j>0 set), the level-n
singular modulus is beta_n = lambda(i * n * sqrt(d)) -- i.e. the CM point
at discriminant d*n^2.  Candidate z forms:

    z = q * beta_n * (1 - beta_n),  q in a fixed rational set

Health checks (must reproduce before any scan output is trusted):
  eq28: d=1, n=1, q=1  -> z=1/4,  (A,B,c0,M) ~ (1,6,1,4)
  eq29: d=1, n=1, q=1/16 (empirical offset from posz_scan_v2) -> z=1/64

Scan: 9 positive d x levels {1,2,3,4,5,7} x signatures {2,3,4,6} x q-set;
4-dim PSLQ [S0, S1, 1, -1/pi] (integer c0 allowed); independent 1/pi
verification at 1e-25.

Verdict per registry P10: EXTENDED / BOUNDARY-CONFIRMED / PIPELINE-FAIL.

Run:  python p10_leveln.py
"""
import json
import math
import os

from mpmath import mp, mpc, mpf, pi, rf, factorial, jtheta, exp, pslq

mp.dps = 80
HERE = os.path.dirname(os.path.abspath(__file__))

QS = [mpf(1), mpf(1) / 4, mpf(1) / 16, mpf(1) / 64, mpf(4),
      mpf(27) / 4, mpf(9) / 4, mpf(3) / 4]
LEVELS = [1, 2, 3, 4, 5, 7]
SIGNS = [2, 3, 4, 6]
POS_D = [1, 2, 20, 24, 40, 52, 88, 148, 232]


def k2_imag(r):
    """lambda(i*r) = k^2 at the pure-imaginary CM point i*r."""
    q = exp(-mp.pi * mpf(r))
    t2, t3 = jtheta(2, 0, q), jtheta(3, 0, q)
    return (t2 / t3) ** 4


def H(k, s):
    return rf(mpf(1) / 2, k) * rf(mpf(1) / s, k) * rf(mpf(1) - 1 / mpf(s), k) \
        / factorial(k) ** 3


def n_terms(z):
    az = abs(float(z))
    if az >= 1 or az < 1e-30:
        return None
    return min(3000, int(math.ceil(-55 / math.log10(az))) + 30)


def try_pslq(z, s, label, results, verbose=True):
    terms = n_terms(z)
    if terms is None:
        return False
    S0 = S1 = mpf(0)
    for k in range(terms):
        h = H(k, s) * z ** k
        S0 += h
        S1 += k * h
    if abs(S0) < mpf(10) ** -20 or abs(S1) < mpf(10) ** -20:
        return False
    rel = pslq([S0, S1, mpf(1), -1 / pi], tol=mpf(10) ** -35,
               maxcoeff=10 ** 8)
    if rel is None:
        return False
    A, B, C, M = (int(r) for r in rel)
    if M == 0 or (A == 0 and B == 0):
        return False
    if max(abs(A), abs(B), abs(C), abs(M)) > 10 ** 7:
        return False
    total = mpf(C)
    for k in range(terms + 80):
        total += (A + B * k) * H(k, s) * z ** k
    err = abs(M / total - pi)
    ok = err < mpf(10) ** -25
    if ok:
        results.append({"label": label, "s": s, "z": mp.nstr(z, 25),
                        "A": A, "B": B, "c0": C, "M": M,
                        "pi_err": mp.nstr(err, 3)})
        if verbose:
            print(f"  HIT {label}: s={s} z={mp.nstr(z, 18)} "
                  f"(A,B,c0,M)=({A},{B},{C},{M}) pi_err={mp.nstr(err, 2)}",
                  flush=True)
    return ok


def main():
    results = []

    print("health check eq28: expect z=1/4, (A,B,c0,M)~(1,6,1,4)")
    beta = k2_imag(1)                      # d=1, n=1
    z = beta * (1 - beta)
    print(f"  beta(1)={mp.nstr(beta, 16)}  z={mp.nstr(z, 16)}")
    try_pslq(z, 2, "eq28-check(d=1,n=1,q=1)", results)
    print("health check eq29: expect z=1/64, (A,B,c0,M)~(5,42,5,16)")
    z29 = beta * (1 - beta) / 16
    try_pslq(z29, 2, "eq29-check(d=1,n=1,q=1/16)", results)

    print(f"\nscan: {len(POS_D)} d x {len(LEVELS)} levels x {len(SIGNS)} s "
          f"x {len(QS)} q-values")
    tried = 0
    for d in POS_D:
        for n in LEVELS:
            beta_n = k2_imag(n * mpf(d) ** 0.5)
            kk = beta_n * (1 - beta_n)
            if not (0 < float(kk) < 1):
                continue
            for q in QS:
                z = q * kk
                if not (0 < abs(float(z)) < 1):
                    continue
                for s in SIGNS:
                    tried += 1
                    try_pslq(z, s, f"d={d},n={n},q={mp.nstr(q, 6)}",
                             results, verbose=False)
        print(f"  d={d:4d} done (cumulative hits: {len(results)})",
              flush=True)

    print(f"\n=== P10 v2: {len(results)} integer relations "
          f"({tried} cells tried) ===")
    checks = {r["label"] for r in results if "check" in r["label"]}
    novel = [r for r in results if "check" not in r["label"]]
    # novelty test: a scan hit is NOVEL only if it is not a relabeling of a
    # known series (eq28-44 params). Known (A,B,M) triples from the paper:
    known_abm = {(1, 6, 4), (5, 42, 16)}
    truly_novel = [r for r in novel
                   if (r["A"], r["B"], r["M"]) not in known_abm]
    if len(checks) < 2:
        verdict = "PIPELINE-FAIL"
    elif truly_novel:
        verdict = "EXTENDED"
    else:
        verdict = "BOUNDARY-CONFIRMED"
    print(f"verdict: {verdict}  (checks reproduced: {sorted(checks)}; "
          f"scan hits: {len(novel)}, truly novel: {len(truly_novel)})")

    out = os.path.join(HERE, "p10_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"verdict": verdict, "tried": tried, "results": results},
                  f, indent=1, default=str)
    print(f"results -> {out}")


if __name__ == "__main__":
    main()
