# -*- coding: utf-8 -*-
"""P240 (gap G5): validator-richness flow-rate scan — 1x / 3x / 10x arms.

P233 calibrated the production function at ONE validator working point
(1.15 bits/call). Registered prediction (pre-stated before the run):

    flow(rich10) > flow(rich3) > flow(rich1)

where flow = ambiguity-bits resolved per verifier call (P233 accounting,
bits_per_row = 2.556 from the P190 boundary dashboard).

Task (real domain, mechanical truth): the six-row landing census on the row
window R = [9, 11, 13, 15, 17, 19, 21, 25, 27, 29, 33, 37].
Truth: d lands iff 1/x6(d) is an integer (evaluator below, same as
verify_certificate.py C1) -> exactly d=13 and d=17 land; the other 10 rows
are odd non-lands (traps for "all odds land" style heuristics).

Arms (what the verifier returns per call):
  rich1 : "k/12 correct"                          (scalar only)
  rich3 : k + WHICH rows are wrong                (labels)
  rich10: k + which wrong + per-wrong-row the true
          label AND the actual 1/x6(d) value      (full evidence)

Protocol: model labels all 12 rows per call (land/no-land), verifier responds
at the arm's richness, model resubmits. Up to 6 calls. flow = 2.556 *
(errors_start - errors_final) / calls_used. 2 models x 3 row-orders x 3 arms.
"""
import os, sys, json, re, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpmath import mp, mpf, exp, pi, sqrt as msqrt
mp.dps = 30

ROWS = [9, 11, 13, 15, 17, 19, 21, 25, 27, 29, 33, 37]
BITS_PER_ROW = 2.556   # P190 ambiguity unit (P233 accounting)
MAX_CALLS = 6

def one_over_x6(d):
    q = exp(-2 * pi * msqrt(mpf(d) / 6))
    def S(k):
        s = mpf(0); n = 1
        while True:
            qn = q ** (k * n)
            if qn < mpf(10) ** -25: break
            s += mpf(n) * qn / (1 - qn); n += 1
        return s
    def eta(x):
        s = mpf(1); n = 1
        while True:
            t = x ** n
            if abs(t) < mpf(10) ** -25: break
            s *= (1 - t); n += 1
        return x ** (mpf(1) / 24) * s
    ec = 4 + 24 * (S(1) + 3 * S(3) - 2 * S(2) - 6 * S(6))
    w6 = eta(q) * eta(q ** 2) * eta(q ** 3) * eta(q ** 6)
    return ec / (4 * w6) + 2

def is_land(d):
    """Landing = 1/x6(d) within 1e-9 of an integer."""
    v = one_over_x6(d)
    return abs(v - round(v)) < mpf(10) ** -9

TRUTH = {d: ("land" if is_land(d) else "no") for d in ROWS}
print("census truth:", TRUTH, flush=True)

MODELS = ["deepseek-v4-flash", "doubao-seed-2.1-lite"]
ORDERS = [ROWS,
          ROWS[5:] + ROWS[:5],
          sorted(ROWS, reverse=True)]

def build_prompt(rows, arm, history, prev_labels=None):
    hist = "\n".join(f"Verifier: {h}" for h in history) or "(first attempt)"
    ev = {"rich1": "the verifier only tells you HOW MANY of your 12 labels are correct.",
          "rich3": "the verifier tells you HOW MANY are correct and WHICH rows are wrong.",
          "rich10": "the verifier tells you HOW MANY are correct, WHICH rows are wrong, and for each wrong row the correct label plus the actual value of f(d) = 1/x6(d) rounded to 4 decimals (f(d) is an exact integer exactly for landing rows)."}[arm]
    keep = ""
    if prev_labels:
        prev = "\n".join(f"d={d}: {prev_labels[d]}" for d in rows if d in prev_labels)
        keep = (f"\nYour previous labeling (the verifier has now scored it):\n{prev}\n"
                "\nIMPORTANT: rows the verifier did NOT flag as wrong were correct — "
                "keep those labels unchanged. Only revise the flagged rows"
                + (" and any rows your updated understanding of the rule changes"
                   if arm == "rich10" else "") + ".\n")
    return f"""A function f(d) = 1/x6(d) (defined by a q-series; you cannot compute it
yourself) has a special property: f(d) is an EXACT integer only for certain
positive integers d ("landing" values). Below are 12 candidate values of d.
Your job: label each as LAND or NO.

You iterate with a verifier: {ev}

History:
{hist}
{keep}
Give your best current labeling of all 12 rows. Answer EXACTLY one line per
row, format: "d=<number>: <LAND|NO>"

Rows: {', '.join(map(str, rows))}"""

def parse(text):
    out = {}
    for m in re.finditer(r"d\s*=\s*(\d+)\s*[:\-]\s*\**\s*(LAND|NO)\b", text, re.I):
        out[int(m.group(1))] = m.group(2).upper()
    return out

def verifier(d, arm, wrong):
    if arm == "rich1":
        return f"{12 - len(wrong)}/12 correct."
    wrong_list = ", ".join(f"d={d}" for d in wrong)
    if arm == "rich3":
        return f"{12 - len(wrong)}/12 correct. Wrong rows: {wrong_list or 'none'}."
    parts = []
    for d in wrong:
        v = one_over_x6(d)
        parts.append(f"d={d}: true={TRUTH[d]}, f(d)={float(v):.4f}")
    return (f"{12 - len(wrong)}/12 correct. Wrong rows: {wrong_list or 'none'}. "
            f"Evidence: " + "; ".join(parts) + ".")

def main():
    def trial2(model, arm, rows):
        import importlib, llm_client
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        history, labels, calls = [], {}, 0
        errs_start = None

        def errs_of(cur):
            return [d for d in rows
                    if d not in cur or (cur[d] == "LAND") != (TRUTH[d] == "land")]

        for _ in range(MAX_CALLS):
            ans = llm_client.ask(build_prompt(rows, arm, history, labels or None))
            calls += 1
            cur = parse(ans)
            for d, v in labels.items():      # resubmit safety net
                if d not in cur:
                    cur[d] = v
            if len(cur) < len(rows):
                history.append(f"unparseable ({len(cur)}/{len(rows)}); resubmit")
                continue
            wrong = errs_of(cur)
            if errs_start is None:
                errs_start = len(wrong)
            if not wrong:
                labels = cur
                break
            history.append(verifier(None, arm, sorted(wrong)))
            labels = cur
        errs_final = len(errs_of(labels)) if labels else len(rows)
        errs_start = errs_start if errs_start is not None else len(rows)
        bits = BITS_PER_ROW * (errs_start - errs_final)
        flow = bits / calls if calls else 0.0
        return {"arm": arm, "model": model, "calls": calls,
                "errs_start": errs_start, "errs_final": errs_final,
                "bits": round(bits, 3), "flow": round(flow, 3),
                "labels": {str(k): v for k, v in labels.items()}}

    t0 = time.time()
    results = []
    for arm in ["rich1", "rich3", "rich10"]:
        for model in MODELS:
            for oi, rows in enumerate(ORDERS):
                r = trial2(model, arm, rows)
                results.append(r)
                json.dump(results, open("p240_richness_results.json", "w"), indent=1)
                print(f"[{int(time.time()-t0)}s] {arm} {model} order{oi}: "
                      f"calls={r['calls']} errs {r['errs_start']}->{r['errs_final']} "
                      f"flow={r['flow']}", flush=True)

    summary = {}
    for arm in ["rich1", "rich3", "rich10"]:
        rs = [r for r in results if r["arm"] == arm]
        mf = sum(r["flow"] for r in rs) / len(rs)
        mc = sum(r["calls"] for r in rs) / len(rs)
        summary[arm] = {"mean_flow": round(mf, 3), "mean_calls": round(mc, 2),
                        "n": len(rs)}
        print(f"{arm}: mean flow {mf:.3f} bits/call, mean calls {mc:.1f}")
    mono = (summary["rich10"]["mean_flow"] > summary["rich3"]["mean_flow"]
            > summary["rich1"]["mean_flow"])
    out = {"prediction": "flow(rich10) > flow(rich3) > flow(rich1)",
           "summary": summary,
           "verdict": "CONFIRMED" if mono else "NOT CONFIRMED",
           "config": {"rows": ROWS, "truth": TRUTH, "bits_per_row": BITS_PER_ROW,
                      "max_calls": MAX_CALLS}}
    json.dump(out, open("p240_richness_verdict.json", "w"), indent=1)
    print(json.dumps({"summary": summary, "verdict": out["verdict"]}, indent=1))

if __name__ == "__main__":
    main()
