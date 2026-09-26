"""P18: Z(X) implementation gate (pre-registered,
docs/RESEARCH_PLAN.md P18 row, commit 12b88bb).

Implements the Cooper-Wan-Zudilin level-6 machinery numerically and
verifies the two structural identities:

  Z  = 1/4 (6P(q^6) - 3P(q^3) + 2P(q^2) - P(q))
  X  = (eta(tau) eta(2tau) eta(3tau) eta(6tau) / Z)^2
  P(q) = 24 q d/dq ln eta(q)

  (i)  X^2(1-4X)(1-36X) Z''' + 3X(1-60X+288X^2) Z''
       + (1-132X+972X^2) Z'  =  6 (1-18X) Z
       where d/dX of a q-function f is (df/dq)/(dX/dq), applied
       recursively for the second and third derivatives.
  (ii) q dX/dq = Z X sqrt((1-4X)(1-36X))

Then the X0 table at CM points tau = i*sqrt(d/6).

Run:  python p18_zx.py
"""
import json
import os
import sys

import mpmath as mm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d1_eta import eta, q_of_tau  # noqa: E402

mm.mp.dps = 80
CUT = mm.mpf(10) ** -(mm.mp.dps - 10)


def p_eisenstein(q):
    """P(q) = 1 - 24 sum_{j>=1} j q^j/(1-q^j)."""
    s = mm.mpf(0)
    j = 1
    while True:
        qj = q ** j
        s += j * qj / (1 - qj)
        if abs(qj) < CUT:
            break
        j += 1
    return 1 - 24 * s


def z_of_q(q):
    return (6 * p_eisenstein(q ** 6) - 3 * p_eisenstein(q ** 3)
            + 2 * p_eisenstein(q ** 2) - p_eisenstein(q)) / 4


def x_of_q(q):
    Z = z_of_q(q)
    num = eta(q) * eta(q ** 2) * eta(q ** 3) * eta(q ** 6)
    return (num / Z) ** 2


def main():
    out = {"gate": [], "x0_table": []}

    # NOTE (registered): the sqrt branch has TWO sheets meeting at the
    # stationary point X = 1/36 (tau ~ 0.42i on the imaginary axis); the
    # identity as written holds on the cusp-side sheet (tau_im >= ~0.45).
    # Verified: at tau=0.3i, dX/dq < 0 while the +sqrt rhs > 0 -- the
    # opposite sheet.  Gate points are on the cusp-side sheet.
    print("=== gate (ii): q dX/dq = Z X sqrt((1-4X)(1-36X)) ===", flush=True)
    for tau_im in ("0.45", "0.6", "1.0"):
        q = q_of_tau(mm.mpc(0, mm.mpf(tau_im)))
        Z = z_of_q(q)
        X = x_of_q(q)
        dX_q = q * mm.diff(x_of_q, q)
        rhs = Z * X * mm.sqrt((1 - 4 * X) * (1 - 36 * X))
        rel = float(abs(dX_q - rhs) / abs(rhs))
        out["gate"].append({"tau_im": tau_im, "identity": "dX",
                            "rel_err": rel})
        print(f"  tau={tau_im}i: rel_err={rel:.2e}", flush=True)

    print("=== gate (i): third-order ODE for Z(X) ===", flush=True)
    # parametric derivatives: d/dX f = (df/dq)/(dX/dq), applied recursively
    Z1 = lambda q: mm.diff(z_of_q, q) / mm.diff(x_of_q, q)
    Z2 = lambda q: mm.diff(Z1, q) / mm.diff(x_of_q, q)
    Z3 = lambda q: mm.diff(Z2, q) / mm.diff(x_of_q, q)
    for tau_im in ("0.45", "0.6", "1.0"):
        q = q_of_tau(mm.mpc(0, mm.mpf(tau_im)))
        Z0 = z_of_q(q)
        X0 = x_of_q(q)
        lhs = (X0 ** 2 * (1 - 4 * X0) * (1 - 36 * X0) * Z3(q)
               + 3 * X0 * (1 - 60 * X0 + 288 * X0 ** 2) * Z2(q)
               + (1 - 132 * X0 + 972 * X0 ** 2) * Z1(q))
        rhs = 6 * (1 - 18 * X0) * Z0
        rel = float(abs(lhs - rhs) / abs(rhs))
        out["gate"].append({"tau_im": tau_im, "identity": "ODE",
                            "rel_err": rel})
        print(f"  tau={tau_im}i: ODE rel_err={rel:.2e}", flush=True)

    ok = all(g["rel_err"] < 1e-25 for g in out["gate"])
    print(f"P18 gate: {'PASS' if ok else 'FAIL'}")
    out["gate_pass"] = ok

    if ok:
        print("\n=== X0 table at CM points ===", flush=True)
        for d in (1, 2, 3, 6, 12, 19, 43, 67, 163):
            q = q_of_tau(mm.mpc(0, mm.sqrt(mm.mpf(d) / 6)))
            try:
                X0 = x_of_q(q)
                Z0 = z_of_q(q)
                r = float(X0.real) if abs(X0.imag) < 1e-30 else None
                row = {"d": d, "X0": float(X0.real) if r is not None
                       else "complex", "Z0_re": float(Z0.real)}
                out["x0_table"].append(row)
                print(f"  d={d:4d}: X0 = {mm.nstr(X0, 12)}  "
                      f"Z0 = {mm.nstr(Z0, 12)}", flush=True)
            except Exception as ex:
                print(f"  d={d}: error {ex}", flush=True)

    with open("p18_zx_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("results -> p18_zx_results.json")


if __name__ == "__main__":
    main()
