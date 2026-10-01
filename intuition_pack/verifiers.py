"""Mechanical verifier registry: the "slow validation" half of the plugin.

P138 rule: verification is EXECUTED (the agent calls run_verifier and
gets a verdict + audit trail), never "read and weighed" by the model.
"""
from mpmath import mp, mpf, exp, pi, sqrt as msqrt

mp.dps = 60
_CUT = mpf(10) ** -(mp.dps - 12)   # scales with precision: P142 probe
# caught fixed 1e-24 cutoffs destroying large-d evaluations (q itself
# falls below a fixed cutoff, the series degenerates, and the verdict
# reads 0.5-confidence garbage out of band)


def _eta(q):
    s = mpf(1)
    n = 1
    while True:
        sg = -1 if n % 2 else 1
        p1 = n * (3 * n - 1) // 2
        p2 = n * (3 * n + 1) // 2
        s += sg * (q ** p1 + q ** p2)
        if q ** p1 < _CUT:
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
            if qn < _CUT:
                break
            s += mpf(n) * qn / (1 - qn)
            n += 1
        return s

    ec = 4 + 24 * (S(1) + 3 * S(3) - 2 * S(2) - 6 * S(6))
    w6 = _eta(q) * _eta(q ** 2) * _eta(q ** 3) * _eta(q ** 6)
    return ec / (4 * w6) + 2


CENSUS_BAND = (1, 300)   # P121: exhaustively verified, zero errors


def _p_rational(resid, tol):
    """P(1/x6 is an integer) from the residual/tolerance ratio.

    In the census band the method IS the ground truth (P121 exhaustive
    census, two code paths at 3.5e-17): the integer rows (residual
    ~1e-40) and the irrational rows (residual = O(1)) are completely
    separated, so the confidence saturates — reported honestly below
    1.0, never a fake 1.0.
    """
    if tol is None or resid is None or tol <= 0:
        return 0.5
    ratio = float(resid / tol)
    if ratio < 1e-6:
        return 1.0 - 1e-6
    if ratio < 1:
        return 0.999
    if ratio > 1e6:
        return 1e-6
    if ratio > 1:
        return 0.001
    return 0.5


def lambert_sixrow(payload: dict) -> dict:
    """Verifier for the ramanujan-sixrow domain.

    payload: {"d": int}  (or {"x0": ...} ignored — the census is indexed by d)
    Decision rule: 1/x6 integer to a scaled absolute tolerance => RATIONAL.
    Output is Jev-typed (P141): verdict + calibrated confidence + a choice
    distribution the agent can threshold on, with the confidence basis
    made explicit (in/out of the exhaustive census band).
    """
    d = int(payload["d"])
    v = lambert_one_over_x6(d)
    # integrality decided entirely in the mp domain (P142: float-rounding
    # capped large-d rows at a fake 0.5 confidence)
    fl = mp.floor(v)
    frac = v - fl
    r = int(fl)
    resid = min(frac, 1 - frac)
    tol = mpf("1e-9")   # absolute: at 60dps the float noise of |v|~1e17
    # is ~1e-43, so 1e-9 sits far above numerics and far below "maybe
    # integer"; the earlier scaled tolerance let 2.85e12-scale rows pass
    # anything (P142 catch)
    # three-band verdict (P142 discovery: d=978=6*163 gives a
    # Ramanujan near-integer 262537412640768746 - residual 7.5e-13,
    # the e^(pi*sqrt(163)) signature — an exact-integer test must not
    # call it RATIONAL, nor garbage NOT)
    is_int = resid < mpf("1e-30")
    is_near = (not is_int) and resid < tol
    in_band = CENSUS_BAND[0] <= d <= CENSUS_BAND[1]
    p_rat = _p_rational(resid, tol)
    if not in_band:
        # numeric test unchanged, but the completeness argument is not
        # verified out of band (P135 scope) — cap and flag
        p_rat = min(p_rat, 0.99) if is_int else max(p_rat, 0.01)
    conf = max(p_rat, 1.0 - p_rat)   # confidence in the emitted verdict
    verdict = ("RATIONAL" if is_int else
               "NEAR_INTEGER" if is_near else "NOT")
    if is_near:
        p_rat = 0.5   # genuinely ambiguous at machine precision
        conf = 0.5
    return {
        "verdict": verdict,
        "confidence": round(conf, 6),
        "typed": {
            "kind": "choice",
            "options": {"RATIONAL": round(p_rat, 6),
                        "NOT": round(1.0 - p_rat, 6)},
            "threshold_hint": "agent-side gate; band-internal judgments "
                              "are census-exhaustive",
        },
        "confidence_basis": ("census_exhaustive_band" if in_band
                             else "out_of_band_numeric_only"),
        "in_band": in_band,
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




def pytest_check(payload: dict, timeout: int = 10) -> dict:
    """Verifier for the code-pass-fail domain: EXECUTE code+tests in a
    subprocess.  This is the 'verifier-rich' class of domains (P136):
    the ground truth is the test suite itself."""
    import subprocess
    prog = payload["code"] + "\n" + payload["test"]
    try:
        r = subprocess.run([sys.executable, "-c", prog],
                           capture_output=True, timeout=timeout,
                           text=True)
        passed = (r.returncode == 0)
        trail = (r.stderr or "")[:300]
    except subprocess.TimeoutExpired:
        passed, trail = False, "timeout"
    return {"verdict": "PASS" if passed else "FAIL",
            "confidence": 1.0 - 1e-9,
            "typed": {"kind": "choice",
                      "options": {"PASS": 1.0 - 1e-9 if passed else 1e-9,
                                  "FAIL": 1e-9 if passed else 1.0 - 1e-9}},
            "confidence_basis": "direct_execution",
            "exec_trail": trail}




def constraint_check(payload: dict) -> dict:
    """Verifier for constrained-set domains: evaluate each claimed
    constraint against the object, return a STRUCTURED violation report
    (which constraints fail) — the auditability payload no LLM judgment
    can produce reliably."""
    obj = payload["object"]
    results = []
    for c in payload["constraints"]:
        fn = CONSTRAINT_FNS[c["name"]]
        results.append({"name": c["name"], "ok": bool(fn(obj))})
    violated = [r["name"] for r in results if not r["ok"]]
    passed = not violated
    return {"verdict": "PASS" if passed else "FAIL",
            "confidence": 1.0 - 1e-9,
            "typed": {"kind": "choice",
                      "options": {"PASS": 1.0 - 1e-9 if passed else 1e-9,
                                  "FAIL": 1e-9 if passed else 1.0 - 1e-9}},
            "confidence_basis": "direct_execution",
            "violated_constraints": violated,
            "per_constraint": results}


from .constraint_fns import BUILT_IN as _BUILT_IN_CONSTRAINTS

CONSTRAINT_FNS = dict(_BUILT_IN_CONSTRAINTS)   # + runtime register_constraint


def register_constraint(name, fn):
    CONSTRAINT_FNS[name] = fn


VERIFIERS = {
    "lambert_sixrow": lambert_sixrow,
    "integer_check": integer_check,
    "pytest_check": pytest_check,
    "constraint_check": constraint_check,
}


def run_verifier(name: str, payload: dict) -> dict:
    if name not in VERIFIERS:
        raise KeyError(f"unknown verifier {name!r}; registered: {list(VERIFIERS)}")
    out = VERIFIERS[name](payload)
    out["verifier"] = name
    out["executed_at"] = time.time()
    return out


import time  # noqa: E402
import sys  # noqa: E402

def score_candidates(candidates: list) -> list:
    """Jev `score` analogue: order candidates by P(RATIONAL), descending —
    the "closeness to the rational locus" ordering.  Each item carries its
    typed choice distribution so the agent can apply its own threshold.
    candidates: [{"d": int} | {"value": float}, ...]
    """
    scored = []
    for c in candidates:
        if "d" in c:
            out = lambert_sixrow({"d": c["d"]})
        else:
            out = integer_check({"value": c["value"]})
        typed = out.get("typed") or {
            "options": {"INTEGER": 1.0 if out["verdict"] == "INTEGER" else 0.0,
                        "NONINTEGER": 0.0 if out["verdict"] == "INTEGER" else 1.0}}
        opts = typed["options"]
        p_rat = opts.get("RATIONAL", opts.get("INTEGER", 0.0))
        scored.append({**c, "verdict": out["verdict"],
                       "p_rational": p_rat,
                       "confidence": out.get("confidence"),
                       "confidence_basis": out.get("confidence_basis", "generic"),
                       "residual": out.get("residual"),
                       "in_band": out.get("in_band", True)})
    scored.sort(key=lambda x: -x["p_rational"])
    return scored
