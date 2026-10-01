"""Mechanical verifier registry: the "slow validation" half of the plugin.

P138 rule: verification is EXECUTED (the agent calls run_verifier and
gets a verdict + audit trail), never "read and weighed" by the model.
"""
from mpmath import mp, mpf, exp, pi, sqrt as msqrt

mp.dps = 30


def _eta(q):
    s = mpf(1)
    n = 1
    while True:
        sg = -1 if n % 2 else 1
        p1 = n * (3 * n - 1) // 2
        p2 = n * (3 * n + 1) // 2
        s += sg * (q ** p1 + q ** p2)
        if q ** p1 < mpf(10) ** -24:
            break
        n += 1
    return q ** (mpf(1) / 24) * s


def lambert_one_over_x6(d: int):
    """1/x6(i*sqrt(d/6)) via the P121 Lambert-series census method."""
    q = exp(-2 * pi * msqrt(mpf(d) / 6))

    def S(k):
        s = mpf(0)
        n = 1
        while True:
            qn = q ** (k * n)
            if qn < mpf(10) ** -25:
                break
            s += mpf(n) * qn / (1 - qn)
            n += 1
        return s

    ec = 4 + 24 * (S(1) + 3 * S(3) - 2 * S(2) - 6 * S(6))
    w6 = _eta(q) * _eta(q ** 2) * _eta(q ** 3) * _eta(q ** 6)
    return ec / (4 * w6) + 2


def lambert_sixrow(payload: dict) -> dict:
    """Verifier for the ramanujan-sixrow domain.

    payload: {"d": int}  (or {"x0": ...} ignored — the census is indexed by d)
    Decision rule: 1/x6 integer to 1e-12 relative tolerance => RATIONAL.
    Audit trail: the value itself.
    """
    d = int(payload["d"])
    v = lambert_one_over_x6(d)
    r = round(float(v)) if abs(float(v)) < 1e12 else None
    resid = abs(v - r) if r is not None else None
    tol = mpf("1e-12") * max(1, abs(r)) if r is not None else None
    is_int = resid is not None and resid < tol
    return {
        "verdict": "RATIONAL" if is_int else "NOT",
        "value": float(v),
        "nearest_integer": r,
        "residual": float(resid) if resid is not None else None,
        "tolerance": float(tol) if tol is not None else None,
        "method": "P121 Lambert-series census (two-code-path verified to 3.5e-17)",
    }


def integer_check(payload: dict) -> dict:
    """Generic integer check on a supplied value (domain-independent)."""
    v = float(payload["value"])
    r = round(v)
    ok = abs(v - r) < 1e-9 * max(1.0, abs(v))
    return {"verdict": "INTEGER" if ok else "NONINTEGER",
            "value": v, "nearest_integer": int(r)}


VERIFIERS = {
    "lambert_sixrow": lambert_sixrow,
    "integer_check": integer_check,
}


def run_verifier(name: str, payload: dict) -> dict:
    if name not in VERIFIERS:
        raise KeyError(f"unknown verifier {name!r}; registered: {list(VERIFIERS)}")
    out = VERIFIERS[name](payload)
    out["verifier"] = name
    out["executed_at"] = time.time()
    return out


import time  # noqa: E402
