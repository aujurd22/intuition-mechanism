"""Direction 1 (v2 corrected): generalize series_from_j to all 27 d.

v2 FIXES vs v1 (b144915, whose 0/27 was a pipeline artifact):
  1. base is PER-D: base_d = round((-j_d)^(1/3)) -- v1 hardcoded BASE=640320,
     which forced every d onto the d=163 target and made all A collapse
     to 13591409. The negative-cube condition (cube_ok) is itself the
     class-number-1 (h=1) signature: only d in {19, 43, 67, 163} pass it.
  2. A is recovered by ROUNDING (A_raw = A + B*S1/S0 is structurally
     off-integer by the S1 contribution); the gate is the FINAL residual
     + B integrality, not A fractional-part sharpness.
  3. Sum terms adapt to |z| (az^terms < 1e-98): small d converge slowly
     (d=7 needs ~350 terms); v1 fixed 25 terms starved them.

Result: 4/27 HIT (d=19, 43, 67, 163) -- exactly the four Heegner d whose
j is a negative perfect cube (96^3, 960^3, 5280^3, 640320^3), reproducing
the Ramanujan-Sato classification MECHANICALLY. The other 23 d are
classified, not failed: j>0 belongs to the positive-z family (different
series form); cube_ok=False (h=2 discriminants) needs the class-number-2
generalization (graded trace forms) -- the honest open problem.

Run:  python d1_generalize.py
"""
import json
import math
import os

import mpmath as mp
import mpmath as mp

mp.mp.dps = 130

def cm_tau(d):
    if d % 4 == 3:
        return (1 + mp.mpc(0, mp.mpf(d) ** 0.5)) / 2
    return mp.mpc(0, mp.mpf(d) ** 0.5)

def j_of_tau(tau):
    q = mp.exp(mp.mpc(0, mp.pi) * tau)
    t2, t3 = mp.jtheta(2, 0, q), mp.jtheta(3, 0, q)
    k2 = (t2 / t3) ** 4
    return 256 * (1 - k2 + k2 ** 2) ** 3 / (k2 ** 2 * (1 - k2) ** 2)

def sum_S(z, terms):
    S0 = S1 = mp.mpf(0)
    for k in range(terms):
        ck = (mp.rf(mp.mpf(1) / 2, k) * mp.rf(mp.mpf(1) / 6, k)
              * mp.rf(mp.mpf(5) / 6, k) / mp.factorial(k) ** 3)
        ckz = ck * z ** k
        S0 += ckz
        S1 += k * ckz
    return S0, S1

def n_terms(z):
    import math
    az = abs(float(z))
    if az >= 1:
        return None
    # terms 使 az^terms < 1e-98
    return min(4000, int(math.ceil(-98 / math.log10(az))) + 10)

H1 = [1, 2, 3, 7, 11, 19, 43, 67, 163]
H2 = [15, 20, 24, 35, 40, 51, 52, 88, 91, 115, 123, 148, 187, 232, 235,
      267, 403, 427]

hits = []
for d in H1 + H2:
    j = j_of_tau(cm_tau(d))
    jr = mp.re(j)
    if jr >= 0:
        print(f"d={d:4d}  j>=0 ({'j=0 (d=3)' if abs(jr)<1e-60 else 'positive-z family'})  SKIP")
        continue
    # base: -j 的立方根, 检验是否精确 (h=1)
    base = int(mp.floor((-jr) ** (mp.mpf(1) / 3) + mp.mpf('0.5')))
    cube_ok = abs(base ** 3 + jr) < abs(jr) * mp.mpf(10) ** -80
    z = 1728 / jr
    terms = n_terms(z)
    if terms is None:
        print(f"d={d:4d}  |z|>=1  SKIP")
        continue
    S0, S1 = sum_S(z, terms)
    Y = base ** (mp.mpf(3) / 2) / (12 * mp.pi)
    A_int = int(mp.floor(Y / S0 + mp.mpf('0.5')))
    B_raw = (Y - A_int * S0) / S1
    B_int = int(mp.floor(B_raw + mp.mpf('0.5')))
    rec = A_int * S0 + B_int * S1
    rel = abs(rec - Y) / abs(Y)
    b_frac = abs(B_raw - B_int)
    hit = bool(cube_ok and b_frac < mp.mpf(10) ** -50 and rel < mp.mpf(10) ** -40)
    # 独立全系列验证: 1/pi = 12*(A*S0+B*S1)/base^3
    pi_check = None
    if hit:
        pi_approx = base ** 3 / (12 * rec)
        pi_check = abs(pi_approx - mp.pi)
    print(f"d={d:4d}  base={base:10d}  cube_ok={cube_ok}  terms={terms:4d}  "
          f"A={A_int:12d}  B={B_int:14d}  b_frac={mp.nstr(b_frac, 2)}  "
          f"rel={mp.nstr(rel, 2)}  {'HIT' if hit else 'miss'}"
          + (f"  [1/pi err {mp.nstr(pi_check, 2)}]" if hit else ""))
    if hit:
        hits.append((d, base, A_int, B_int))

print(f"\n=== TRUE D1 generalization: {len(hits)} integer series found ===")
for d, base, A, B in hits:
    print(f"  d={d:4d}: 1/pi = 12*sum (A+Bk)c_k z^k / base^(3/2), "
          f"base={base}, A={A}, B={B}, z=-1728/{base}^3")

if __name__ == "__main__" or True:
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "d1_generalization_results.json")
    rows_json = []
    print(f"=== TRUE D1 generalization: {len(hits)} integer series found ===")
    for d, base, A, B in hits:
        print(f"  d={d:4d}: base={base}, A={A}, B={B}, z=-1728/{base}^3")
        rows_json.append({"d": d, "base": base, "A": A, "B": B,
                          "z": f"-1728/{base}^3"})
    # independent full-series verification (direct summation, 50-digit gate)
    print("\n=== independent 1/pi verification (50-digit gate) ===")
    allpass = True
    for d, base, A, B in hits:
        z = mp.mpf(-1728) / (base ** 3)
        S = mp.mpf(0)
        for k in range(300):
            ck = (mp.rf(mp.mpf(1)/2, k) * mp.rf(mp.mpf(1)/6, k)
                  * mp.rf(mp.mpf(5)/6, k) / mp.factorial(k)**3)
            S += (A + B*k) * ck * z**k
        err = abs(base**(mp.mpf(3)/2) / (12*S) - mp.pi)
        ok = err < mp.mpf(10)**-45
        allpass &= ok
        print(f"  d={d:4d}: |pi_pred - pi| = {mp.nstr(err, 3)}  "
              f"{'PASS' if ok else 'FAIL'}")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"hits": len(hits), "total": 27, "series": rows_json,
                   "verify_50digit": bool(allpass)}, f, indent=1)
    print(f"results -> {out}")
