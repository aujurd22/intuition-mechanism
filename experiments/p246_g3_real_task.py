# -*- coding: utf-8 -*-
"""P246 (gap G3, oldest untouched review item): GENERATION-SIDE REAL TASK.

A research-grade problem with a programmatic verifier and a KNOWN BOUNDARY TO
IMPROVE (not a known optimum to reach):

  Task: write eval_x6(d) — a fast pure-Python evaluator of 1/x6(d)
        (= Ec/(4*W6) + 2, the six-row census function; 1/x6(d) is an exact
        integer exactly at d in {1,3,5,7,13,17} — P121).
  Baseline (known boundary): the repo's mpmath 50-dps reference implementation.
  Correctness: relative error <= 1e-9 on a HOLDOUT range d in [201, 400]
        (the model is given [1,200] for self-testing; holdout answers are
        never shown unless the model fails there — lookup tables fail).
  Score: speedup = baseline holdout time / model holdout time.
  Anti-cheat: blacklist (mpmath/numpy/reference names/file IO/exec-of-reference);
        pure computation only.
  Feedback: LABELED (P240 lesson) — failing d values with ref vs model numbers,
        plus current time vs baseline.

Registered expectations (pre-stated):
  E1: models improve on the baseline (speedup > 1 with full correctness) —
      generation side OPEN on a real task.
  E2 (boundary law): improvements are verifier-gated — at least one submitted
      version fails correctness or the anti-cheat before (or instead of) passing.
"""
import os, sys, json, re, time, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpmath import mp, mpf, exp, pi, sqrt as msqrt
mp.dps = 50

SELF_RANGE = range(1, 201)
HOLDOUT = list(range(1, 201))   # real truncation work at small d (q not tiny)
MODELS = ["kimi-k2.8-preview", "glm-5.3-flash"]
ROUNDS = 3
BLACKLIST = ["mpmath", "numpy", "one_over_x6", "verify_certificate",
             "open(", "__import__", "subprocess", "eval(", "exec(",
             "references", "REFS"]

MATH_BLOCK = """Write a PYTHON function `eval_x6(d)` that computes L(d) = Ec(d)/(4*W6(d)) + 2
for positive integers d, where (q-series, q = exp(-2*pi*sqrt(d/6))):

  S(k)  = sum over n >= 1 of n*q^(k*n) / (1 - q^(k*n)), stopping when terms < 1e-35
  Ec(d) = 4 + 24*(S(1) + 3*S(3) - 2*S(2) - 6*S(6))
  W6(d) = eta(q)*eta(q^2)*eta(q^3)*eta(q^6),
          eta(x) = x^(1/24) * prod over n >= 1 of (1 - x^n)

Reference values (your function must reproduce these to 1e-9 relative error):
  L(1)=8, L(3)=12, L(5)=20, L(7)=32, L(13)=104, L(17)=200
"""

def ref_one_over_x6(d):
    """Reference implementation (mpmath, 50 dps) — the repo's C1 evaluator."""
    q = exp(-2 * pi * msqrt(mpf(d) / 6))
    def S(k):
        s = mpf(0); n = 1
        while True:
            qn = q ** (k * n)
            if qn < mpf(10) ** -35: break
            s += mpf(n) * qn / (1 - qn); n += 1
        return s
    ec = 4 + 24 * (S(1) + 3 * S(3) - 2 * S(2) - 6 * S(6))
    def eta(x):
        s = mpf(1); n = 1
        while True:
            t = x ** n
            if abs(t) < mpf(10) ** -30: break
            s *= (1 - t); n += 1
        return x ** (mpf(1) / 24) * s
    w6 = eta(q) * eta(q ** 2) * eta(q ** 3) * eta(q ** 6)
    return ec / (4 * w6) + 2

print("precomputing holdout references (200 values, mpmath 50dps)...", flush=True)
T0 = time.perf_counter()
REFS = {d: float(ref_one_over_x6(d)) for d in HOLDOUT}
ref_build_s = time.perf_counter() - T0
base_t0 = time.perf_counter()
for d in HOLDOUT:
    float(ref_one_over_x6(d))
BASELINE_S = time.perf_counter() - base_t0
print(f"references ready in {ref_build_s:.1f}s; baseline holdout time "
      f"{BASELINE_S*1000:.0f} ms ({BASELINE_S/200*1000:.2f} ms/value)", flush=True)

PROMPT0 = MATH_BLOCK + f"""Check points (yours must match to 1e-9 relative):
  L(2)~{float(ref_one_over_x6(2)):.9f}, L(4)~{float(ref_one_over_x6(4)):.9f},
  L(9)~{float(ref_one_over_x6(9)):.9f}, L(25)~{float(ref_one_over_x6(25)):.9f}

Requirements:
- Pure Python, standard library only (math allowed). NO mpmath, NO numpy,
  NO precomputed answer tables over a range, no file/network IO.
- Must be a general algorithm, not a lookup of the answers above.
- It will be validated on d = 1..200 (most hidden from you): relative
  error <= 1e-9 on every value.
- SCORE = speed: your function's total time over the 200 values versus the
  reference implementation's time (baseline ~{BASELINE_S*1000:.0f} ms).
  Faster is better. Float64 (math) is precise enough if you truncate wisely.

Output ONLY Python code defining eval_x6(d)."""

def extract_code(text):
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    return m.group(1) if m else text

def check_code(code):
    bad = [b for b in BLACKLIST if b.lower() in code.lower()]
    return bad

def grade(code):
    """returns (speedup, rel_errs dict sample, fail_list, err_or_None)"""
    ns = {}
    try:
        exec(code, ns)
    except Exception as ex:
        return None, {}, [], f"exec error: {ex}"
    fn = ns.get("eval_x6")
    if not callable(fn):
        return None, {}, [], "no eval_x6() defined"
    fails = []
    t0 = time.perf_counter()
    for d in HOLDOUT:
        try:
            v = float(fn(d))
        except Exception as ex:
            return None, {}, [d], f"runtime error at d={d}: {ex}"
        r = REFS[d]
        rel = abs(v - r) / abs(r)
        if rel > 1e-9:
            fails.append((d, r, v, rel))
    dt = time.perf_counter() - t0
    speedup = BASELINE_S / dt if dt > 0 else 0.0
    return speedup, fails, [], None

def feedback_text(speedup, fails, err):
    if err:
        return f"Your submission FAILED: {err}. Fix and resubmit."
    if fails:
        s = "; ".join(f"d={d}: ref={r:.9f}, yours={v:.9f} (rel {rel:.1e})"
                      for d, r, v, rel in fails[:8])
        more = f" ... ({len(fails)} failing values total)" if len(fails) > 8 else ""
        return (f"Your submission FAILED correctness on {len(fails)} hidden values "
                f"(relative error > 1e-9): {s}{more}. "
                f"Improve truncation/precision. Resubmit.")
    return (f"Your submission PASSED correctness on all 200 hidden values. "
            f"Time: {BASELINE_S/speedup*1000:.1f} ms vs baseline "
            f"{BASELINE_S*1000:.1f} ms = speedup {speedup:.1f}x. "
            f"Make it faster while staying correct. Resubmit.")

def main():
    import importlib, llm_client
    out = {"baseline_ms": round(BASELINE_S * 1000, 1), "models": {}}
    t0 = time.time()
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        prompt = PROMPT0
        best = {"speedup": 0.0}
        rounds = []
        for rnd in range(1, ROUNDS + 1):
            resp = llm_client.ask(prompt)
            code = extract_code(resp)
            bad = check_code(code)
            if bad:
                speedup, fails, _, err = None, [], [], \
                    f"ANTI-CHEAT blacklist hit: {bad}"
            else:
                speedup, fails, _, err = grade(code)
            fb = feedback_text(speedup if speedup else 0.0, fails, err)
            rounds.append({"round": rnd, "speedup": None if speedup is None
                           else round(speedup, 1),
                           "n_fail": len(fails), "err": err, "fb": fb[:300],
                           "code": code[:1200]})
            ok = speedup is not None and not fails and not err
            if ok and speedup > best["speedup"]:
                best = {"speedup": round(speedup, 1), "round": rnd}
            print(f"[{int(time.time()-t0)}s] {model} r{rnd}: "
                  f"{'PASS %.1fx' % speedup if ok else 'FAIL ' + str(err or len(fails)) + ' vals'}",
                  flush=True)
            prompt = (PROMPT0 + "\n\nYour previous submission and verifier "
                      f"feedback:\n{fb}\n\nPrevious code:\n```python\n{code}\n```\n"
                      "Output ONLY the improved full code.")
        out["models"][model] = {"rounds": rounds, "best": best}
        json.dump(out, open("p246_g3_real_task.json", "w"), indent=1)

    e1 = any(m["best"]["speedup"] > 1.0 for m in out["models"].values())
    e2 = any(any(r["err"] or r["n_fail"] for r in m["rounds"])
             for m in out["models"].values())
    summary = {"E1_generation_improves_boundary": e1,
               "E2_verifier_gated": e2,
               "best_per_model": {k: v["best"] for k, v in out["models"].items()}}
    out["summary"] = summary
    json.dump(out, open("p246_g3_real_task.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
