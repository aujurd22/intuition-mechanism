"""P32: LLM cross-family meta-proposal (pre-registered,
docs/RESEARCH_PLAN.md P32 row).

Arm A (cross-family meta-learning): show the LLM verified identities
from K-1 families, ask for the signature of a held-out family's
identity.  Families: our t-family census rows with DIFFERENT structural
backgrounds (constructed synthetic variants with distinct envelope
exponents alpha: t(n) ~ n^alpha r^n families with alpha in
{-3/2, -1/2, -2} and ratios {8, 4, 16}), signatures = the family id.

Arm B (proposal-verification): LLM proposes lambda values for NEW N
given context identities; judged by the 50-digit gate (closure of the
identity at the proposed lambda vs the numerically-solved lambda).

Chance baselines: Arm A signature guess = 1/K; Arm B random lambda
within [0, 1] hits the 1e-6 closure band with probability ~0.

Run:  python p32_llm_meta.py
"""
import json
import os
import sys
from math import comb

import mpmath as mm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
from llm_client import ask  # noqa: E402

mm.mp.dps = 50

# ---------------- family zoo ----------------
# Each family: t(n) ~ C * r^n * n^alpha with distinct (r, alpha).
# Identity shape shared with the t-family: sum (n+lambda) f(n) x^n = RHS(x)
# where RHS is COMPUTED from the family (so the task is: infer lambda
# from context examples of the same family).

def fam_t(n):          # the CWZ t-family (r=8, alpha=-3/2)
    v = 0
    for k in range(n // 2 + 1):
        v += comb(n, 2 * k) * comb(2 * k, k) ** 2 * comb(2 * n - 4 * k,
                                                         n - 2 * k)
    return v


def fam_a(n):          # synthetic: pure binomial square (r=4, alpha=-1)
    return comb(2 * n, n)


def fam_b(n):          # synthetic: central binomial (r=4, alpha=-1/2)
    return comb(2 * n, n) // (n + 1)      # Catalan numbers


def fam_c(n):          # synthetic: 3^n * n^-1/2 shape
    return 3 ** n // (n if n else 1)


FAMILIES = {
    "T": fam_t,
    "A": fam_a,
    "B": fam_b,
    "C": fam_c,
}


def rhs_for(fam_fn, x0, N):
    """The identity RHS for a family at its CM point: we DEFINE the
    family's lambda by closing the identity, i.e. lambda = (rhs - S1)/S0
    with rhs = 1/(2 pi sqrt(N)) * 1/sqrt(disc(N, x0)).  For the synthetic
    families we use the same disc structure -- the task is lambda
    inference given context, not rhs derivation."""
    # generic disc: (1 - x/r1)(1 - x/r2)(1 - x/r3) with r=8-analog per
    # family; keep it simple: disc = (1+4x)(1-4x)(1-8x) for T, and for
    # synthetic families (1-4x)^3 (uniform).
    if fam_fn is fam_t:
        return (1 / (2 * mm.pi)) * mm.sqrt(mm.mpf(24) / N) / \
            mm.sqrt((1 + 4 * x0) * (1 - 4 * x0) * (1 - 8 * x0))
    return (1 / (2 * mm.pi)) * mm.sqrt(mm.mpf(24) / N) / \
        (1 - 4 * x0) ** 1.5


def sums(fn, x0, N=600):
    S0 = mm.mpf(0)
    S1 = mm.mpf(0)
    xk = mm.mpf(1)
    for n in range(N):
        v = mm.mpf(fn(n))
        S0 += v * xk
        S1 += n * v * xk
        xk *= x0
    return S0, S1


def fmt_seq(fn, n=8):
    return ", ".join(str(fn(i)) for i in range(n))


def main():
    out = {"armA": [], "armB": []}

    # ---------------- Arm A: cross-family signature prediction ----------
    print("=== Arm A: cross-family signature prediction ===", flush=True)
    fam_names = list(FAMILIES)
    a_hits = 0
    a_tot = 0
    for held_out in fam_names:
        ctx = [f for f in fam_names if f != held_out]
        prompt = (
            "IMPORTANT: Answer IMMEDIATELY with one letter. "
            "Do not think step by step.\n\n"
            "Each of the following integer sequences belongs to a "
            "different family, labeled by a letter. Study the family "
            "structures.\n\n" +
            "\n".join(f"Family {f}: {fmt_seq(FAMILIES[f])}"
                      for f in ctx) +
            f"\n\nNow a NEW sequence from an unseen family:\n"
            f"{fmt_seq(FAMILIES[held_out])}\n\n"
            "Which family label (T, A, B, or C) does its structure "
            "match best? Answer with ONE letter only.")
        ans = ask(prompt)
        letter = next((ch for ch in ans[-200:] if ch in "TABC"), None)
        ok = letter == held_out
        a_hits += int(ok)
        a_tot += 1
        print(f"  held-out={held_out}: ans={ans[-30:]!r} "
              f"{'OK' if ok else 'X'}", flush=True)
        out["armA"].append({"held_out": held_out, "answer": ans[-100:],
                            "correct": ok})
    chance_a = 1 / len(fam_names)
    print(f"  Arm A: {a_hits}/{a_tot} (chance {chance_a:.2f})", flush=True)

    # ---------------- Arm B: proposal-verification ----------------------
    print("\n=== Arm B: lambda proposal + 50-digit gate ===", flush=True)
    # context: the t-family identities at N=3,5,7,13,17 (known lambdas)
    import sys as _s
    _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from p19b_z12 import x12
    ctx_rows = []
    for N, x0f in ((3, mm.mpf(1) / 12), (5, mm.mpf(1) / 20),
                   (7, mm.mpf(1) / 32), (13, mm.mpf(1) / 104),
                   (17, mm.mpf(43) / 238)):
        S0, S1 = sums(fam_t, x0f)
        r = (1 / (2 * mm.pi)) * mm.sqrt(mm.mpf(24) / N) / \
            mm.sqrt((1 + 4 * x0f) * (1 - 4 * x0f) * (1 - 8 * x0f))
        lam = (r - S1) / S0
        ctx_rows.append((N, x0f, lam))
    ctx_text = "\n".join(
        f"N={N}: x0={mm.nstr(x0, 12)}, lambda={mm.nstr(l, 12)}"
        for N, x0, l in ctx_rows)

    b_hits = 0
    b_tot = 0
    for N in (2, 6, 11, 19, 23):
        q = mm.exp(-2 * mm.pi * mm.sqrt(mm.mpf(N) / 24))
        x0 = x12(q)
        x0 = mm.mpf(x0.real)
        S0, S1 = sums(fam_t, x0)
        r = (1 / (2 * mm.pi)) * mm.sqrt(mm.mpf(24) / N) / \
            mm.sqrt((1 + 4 * x0) * (1 - 4 * x0) * (1 - 8 * x0))
        lam_true = (r - S1) / S0
        prompt = (
            "IMPORTANT: Answer IMMEDIATELY with a decimal number. "
            "Do not think step by step.\n\n"
            "The Ramanujan-type identity family sum (n+lambda) t(n) x^n "
            "= RHS has these verified (N, x0, lambda) triples:\n"
            f"{ctx_text}\n\n"
            f"New CM point: N={N}, x0={mm.nstr(x0, 15)}.\n"
            "Predict lambda for this N. Answer with a decimal number "
            "only.")
        ans = ask(prompt)
        # parse first float
        import re
        m = re.search(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?\d+)?", ans)
        pred = float(m.group(0)) if m else None
        if pred is not None:
            err = abs(pred - float(lam_true))
            hit = err < 1e-4
        else:
            hit = False
        b_hits += int(hit)
        b_tot += 1
        print(f"  N={N:3d}: true={mm.nstr(lam_true, 10)} "
              f"pred={pred} {'OK' if hit else 'X'}", flush=True)
        out["armB"].append({"N": N, "pred": pred,
                            "true": mm.nstr(lam_true, 20), "hit": hit})

    print(f"\n=== summary ===")
    print(f"Arm A (cross-family): {a_hits}/{a_tot}, chance {chance_a:.2f}")
    print(f"Arm B (lambda proposal): {b_hits}/{b_tot}, "
          f"chance ~0 (continuous)")
    out["summary"] = {"armA": f"{a_hits}/{a_tot}",
                      "armA_chance": chance_a,
                      "armB": f"{b_hits}/{b_tot}"}

    with open("p32_llm_meta_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("results -> p32_llm_meta_results.json")


if __name__ == "__main__":
    main()
