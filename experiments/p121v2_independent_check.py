"""P121-v2: independent-method verification of the Lambert-series census.

P121 computed Ec from the closed-form Lambert combination
Ec = 4 + 24*(S1 + 3*S3 - 2*S2 - 6*S6).  This check recomputes Ec at
the six locus rows (+ 4 random non-rows) by COMPLEX CENTRAL DIFFERENCE
of dlogP/dtau directly on the eta products — a different code path
with different error modes (truncation vs series coefficients).

Acceptance: |Ec_cd - Ec_lambert| < 1e-25 at 50 dps (h = 1e-9).
"""
import json
from mpmath import mp, mpf, mpc, exp, pi, sqrt as msqrt, fabs, nstr

mp.dps = 50


def eta(q):
    q = mpc(q)
    cut = mpf(10) ** -(mp.dps - 5)
    s = mpc(1)
    n = 1
    while True:
        sg = -1 if n % 2 else 1
        p1 = n * (3 * n - 1) // 2
        p2 = n * (3 * n + 1) // 2
        s += sg * (q ** p1 + q ** p2)
        if fabs(q) ** p1 < cut:
            break
        n += 1
    return q ** (mpf(1) / 24) * s


def P(tau):
    # nome convention: eta(k*tau) = eta_nome(q**k), matching p121/P80
    q = exp(2 * pi * 1j * tau)
    return eta(q ** 2) * eta(q ** 6) / (eta(q) * eta(q ** 3))


def W6(tau):
    q = exp(2 * pi * 1j * tau)
    return eta(q) * eta(q ** 2) * eta(q ** 3) * eta(q ** 6)


def lambert(q, k):
    s = mpf(0)
    n = 1
    q = mpf(q)
    while True:
        qn = q ** (k * n)
        if qn < mpf(10) ** -45:
            break
        s += n * qn / (1 - qn)
        n += 1
    return s


def Ec_lambert(d):
    # tau0 = i*sqrt(d/6)  =>  q = exp(-2*pi*sqrt(d/6)), real positive
    qr = exp(-2 * pi * msqrt(mpf(d) / 6))
    return 4 + 24 * (lambert(qr, 1) + 3 * lambert(qr, 3)
                     - 2 * lambert(qr, 2) - 6 * lambert(qr, 6))


def Ec_central_diff(tau, h=mpf("1e-9")):
    lp = P(tau + h)
    lm = P(tau - h)
    dlogP = (lp - lm) / (2 * h * P(tau))
    return 12 / (pi * 1j) * dlogP


ROWS = {1: 8, 3: 12, 5: 20, 7: 32, 13: 104, 17: 200}
NONROWS = [10, 35, 77, 101]

out = {"rows": [], "nonrows": [], "max_err": 0.0}
for d in list(ROWS) + NONROWS:
    tau = 1j * msqrt(mpf(d) / 6)
    e_cd = Ec_central_diff(tau)
    e_lm = Ec_lambert(d)
    err = fabs(e_cd - e_lm)
    out["max_err"] = max(out["max_err"], float(err))
    entry = {"d": d, "Ec_cd": nstr(e_cd.real, 12), "Ec_lm": nstr(e_lm, 12),
             "err": nstr(err, 3)}
    if d in ROWS:
        x = e_cd / (4 * W6(tau)) + 2
        entry["1/x6_via_cd"] = nstr(x, 10)
        out["rows"].append(entry)
    else:
        out["nonrows"].append(entry)
    print(entry)

json.dump(out, open("p121v2_independent_check.json", "w"), indent=1)
print("max err:", out["max_err"])
