"""P157: Heegner shadow scan — near-integer residual census over [1, 5000].

P143 found d=978=6*163 with residual 7.5e-13 (the e^(pi*sqrt163) signature).
Hypothesis: near-integer rows are exactly d = 6h for Heegner h in
{1,2,3,7,11,19,43,67,163} (class-number-1 discriminants), i.e. the
Ramanujan near-integer shadows of the Heegner numbers inside the census.

Scan: residual = distance of 1/x6(d) to the nearest integer, recorded for
EVERY d (not just exact hits).  Near-integer band: 1e-30 < residual < 1e-4.
"""
import json
import time
from mpmath import mp, mpf, exp, pi, sqrt as msqrt, floor

mp.dps = 60
CUT = mpf(10) ** -(mp.dps - 12)

HEEGNER = [1, 2, 3, 7, 11, 19, 43, 67, 163]


def one_over_x6(d):
    q = exp(-2 * pi * msqrt(mpf(d) / 6))

    def S(k):
        s = mpf(0)
        n = 1
        while True:
            qn = q ** (k * n)
            if qn < CUT:
                break
            s += mpf(n) * qn / (1 - qn)
            n += 1
        return s

    def eta(q):
        s = mpf(1)
        n = 1
        while True:
            sg = -1 if n % 2 else 1
            p1 = n * (3 * n - 1) // 2
            p2 = n * (3 * n + 1) // 2
            s += sg * (q ** p1 + q ** p2)
            if q ** p1 < CUT:
                break
            n += 1
        return q ** (mpf(1) / 24) * s

    ec = 4 + 24 * (S(1) + 3 * S(3) - 2 * S(2) - 6 * S(6))
    w6 = eta(q) * eta(q ** 2) * eta(q ** 3) * eta(q ** 6)
    return ec / (4 * w6) + 2


def scan(dmax=5000):
    exact_hits, near_hits, residuals = [], [], {}
    t0 = time.time()
    for d in range(1, dmax + 1):
        v = one_over_x6(d)
        fl = floor(v)
        frac = v - fl
        resid = min(frac, 1 - frac)
        residuals[d] = float(resid)
        if resid < mpf("1e-30"):
            exact_hits.append((d, float(v)))
        elif resid < mpf("1e-4"):
            near_hits.append({"d": d, "residual": float(resid),
                              "value_head": mp.nstr(v, 18),
                              "is_6xHeegner": (d % 6 == 0 and d // 6 in HEEGNER)})
        if d % 500 == 0:
            print(f"  ... d={d} ({time.time()-t0:.0f}s)")
    return exact_hits, near_hits, residuals


if __name__ == "__main__":
    import mpmath
    exact, near, residuals = scan(5000)
    print(f"\nexact-integer hits: {[d for d, _ in exact]}")
    print(f"near-integer rows ({len(near)}):")
    for n in near:
        tag = "6xHeegner ✓" if n["is_6xHeegner"] else "other"
        print(f"  d={n['d']:>5} residual={n['residual']:.3e} value≈{n['value_head'][:20]} [{tag}]")
    # hypothesis check: every near-integer is 6xHeegner?
    all_heegner = all(n["is_6xHeegner"] for n in near)
    # and every 6xHeegner d in range is near-integer or exact?
    six_h = [6 * h for h in HEEGNER if 6 * h <= 5000]
    coverage = {d: (float(residuals[d]) < 1e-4 or
                    (residuals[d] < 1e-30)) for d in six_h}
    print("\n6xHeegner d values residual check:")
    for d in six_h:
        print(f"  d={d:>4} residual={residuals[d]:.3e}")
    print("\nHYPOTHESIS 'near-integer = 6xHeegner':",
          "CONFIRMED" if all_heegner else "REFUTED")
    json.dump({"exact_hits": exact, "near_hits": near,
               "six_h_res": {str(d): float(residuals[d]) for d in six_h},
               "hypothesis_confirmed": all_heegner},
              open("p157_heegner_scan.json", "w"), indent=1)
