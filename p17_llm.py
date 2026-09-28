"""P17: LLM baseline -- memory vs mechanism discriminator
(pre-registered, docs/RESEARCH_PLAN.md P17 row, commit 32cf4b8).

Conditions (chance = 0.25, single-digit answers, temperature 0):
  A-lit          : the 17 REAL Ramanujan-Sato series (literature exists;
                   the memory route is open).
  B-counterfactual: fresh random (A,B,z) from our generator -- these exact
                   series exist in NO literature (memory route closed);
                   4 few-shot examples with different random params.
  C-control      : B queries, examples shown with WRONG labels.

Registered bands: B >= 0.70 => CONFIRMED (mechanism); 0.45-0.70 =>
PARTIAL; B < 0.45 with A >= 0.70 => MEMORY-ONLY; both < 0.45 =>
INCONCLUSIVE.

Run:  python p17_llm.py   (needs llama-server on 127.0.0.1:8080)
"""
import json
import os
import sys
import urllib.request

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p15_envelope import make_dataset, poch_cum  # noqa: E402
from p4_clean import build  # noqa: E402

URL = "http://127.0.0.1:8080/v1/chat/completions"
SIGS = (2, 3, 4, 6)


def ask(prompt):
    body = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0, "max_tokens": 768, "cache_prompt": True,
    }).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1200) as r:
        out = json.loads(r.read())
    msg = out["choices"][0]["message"]
    # Bonsai-2 is a REASONING model: content stays empty while
    # max_tokens is spent in reasoning_content
    return (msg.get("content") or "") + "\n" + (msg.get("reasoning_content")
                                                or "")


def fmt(seq, n=12):
    return ", ".join(f"{v:.6g}" for v in seq[:n])


def fewshot_prompt(examples, query, scaffold=False):
    ex = "\n".join(f"(s={s}) {fmt(e)}" for s, e in examples)
    base = ("Coefficients of infinite series follow. Each series belongs "
            "to a family labeled by its signature s in {2, 3, 4, 6}. "
            "Series of the same family share a structural constant.\n\n"
            f"{ex}\n\nNew series:\n{fmt(query)}\n\n")
    if scaffold:
        return base + (
            "TOOL -- successive ratios: compute r_n = c_n / c_{n+1} for "
            "n = 0..5 and look at how r_n changes with n.  The signature "
            "s is visible in the limit pattern of these ratios: r_n -> "
            "z*(1 - (1-1/s)/n + ...) is NOT needed; simply compute r_n "
            "for large n and identify the signature from the few-shot "
            "examples' ratio behavior.  Compute at least three ratios "
            "for the new series and compare with the examples' ratios.\n\n"
            "What is its signature s? Answer with ONE digit only.")
    return base + "What is its signature s? Answer with ONE digit only."


import re


def parse_digit(ans):
    """Answer extraction from reasoning-model output.  Priority:
    (1) 's = 6' / 'signature: 6' / 'answer: 6' patterns, last occurrence;
    (2) a STANDALONE digit token in the tail (not inside a number like
        9.91e-06 -- the reversed-scan v1 parser mistook those)."""
    tail = ans[-400:]
    m = re.findall(r'(?:s\s*=\s*|signature\s*[:=]?\s*|answer\s*[:=]?\s*)'
                   r'([2346])', tail, re.IGNORECASE)
    if m:
        return m[-1]
    m = re.findall(r'(?<![\d.eE-])([2346])(?![\d])', tail)
    if m:
        return m[-1]
    return None


def main():
    rng = np.random.default_rng(123)

    # ---- condition A: the 17 real literature series ----
    seqs, meta, _ = build()
    a_items = [(seqs[i], meta[i]["s"]) for i in range(len(seqs))]

    # ---- condition B: counterfactual queries + few-shot examples ----
    X, y, _ = make_dataset(poch_cum, seed=777)     # disjoint seed from all
    order = rng.permutation(len(X))[:20]
    examples = []
    for si, s in enumerate(SIGS):
        idx = [i for i in order[:8] if y[i] == si][:1]   # 1 ex per class
        examples.append((s, X[idx[0]]))
    b_items = [(X[i], SIGS[y[i]]) for i in order[8:8 + 20]]

    # ---- condition C: same B queries, WRONG example labels ----
    wrong = [(SIGS[(si + 1) % 4], e) for si, e in examples]

    results = {"A_lit": [], "B_counterfactual": [], "C_control": []}
    print("=== A-lit (memory route open) ===", flush=True)
    for seq, s in a_items:
        ans = ask(fewshot_prompt(examples, seq))
        # prefer the answer after reasoning: scan from the END
        d = next((ch for ch in reversed(ans) if ch in "2346"), None)
        results["A_lit"].append(int(d == str(s)))
        print(f"  true={s} ans={ans[-40:]!r} {'OK' if d == str(s) else 'X'}",
              flush=True)

    print("=== B-counterfactual (memory route closed) ===", flush=True)
    for seq, s in b_items:
        ans = ask(fewshot_prompt(examples, seq))
        d = parse_digit(ans)
        results["B_counterfactual"].append(int(d == str(s)))
        print(f"  true={s} ans={ans[-40:]!r} {'OK' if d == str(s) else 'X'}",
              flush=True)

    print("=== C-control (wrong-label examples) ===", flush=True)
    for seq, s in b_items[:10]:
        ans = ask(fewshot_prompt(wrong, seq))
        d = parse_digit(ans)
        results["C_control"].append(int(d == str(s)))
        print(f"  true={s} ans={ans[-40:]!r} {'OK' if d == str(s) else 'X'}",
              flush=True)

    accs = {k: round(float(np.mean(v)), 3) for k, v in results.items()}
    print("\n=== accuracy (chance 0.25) ===")
    for k, v in accs.items():
        print(f"  {k:16s} {v:.3f}  (n={len(results[k])})")

    a, b = accs["A_lit"], accs["B_counterfactual"]
    if b >= 0.70:
        verdict = "CONFIRMED (mechanism)"
    elif b >= 0.45:
        verdict = "PARTIAL"
    elif a >= 0.70:
        verdict = "MEMORY-ONLY"
    else:
        verdict = "INCONCLUSIVE"
    print(f"\nP17 verdict: {verdict}")
    out = {"accs": accs, "raw": results, "verdict": verdict,
           "model": "Ternary-Bonsai-2-27B (PQ2), temp 0"}
    with open("p17_llm_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("results -> p17_llm_results.json")


if __name__ == "__main__":
    main()
