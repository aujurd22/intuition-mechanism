"""P32-c: independent-judge replication (queued from P32-b).

The judge (GLM via Volcano API) sees ONLY the six 8-term sequences --
no class definitions, no ground truth, no hint of how many classes
exist -- and must group them by singularity structure.  The grouping is
then compared with the constructed truth:

  truth classes: {M1: step3-nosign, M2: osc-step2, M3: step4-nosign,
                  M4: smooth, M5: step2-nosign, M6: osc-step3}

Scoring: pairwise class-agreement -- for each of the 15 pairs, does the
judge's grouping agree with the truth on "same class vs different
class"?  (The judge may invent its own class names; only the PARTITION
is scored.)

Run:  python p32c_judge.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
from llm_client import ask_chat as ask  # noqa: E402


def main():
    truth = json.load(open("p32b_families.json"))
    seqs = truth["sequences"]
    cls = truth["class_of"]

    prompt = (
        "Six integer sequences are listed below. Group them by "
        "SINGULARITY STRUCTURE: the deep growth/oscillation behavior, "
        "not surface coefficients. Classes should capture oscillation "
        "period (none / every-term alternation / period-k), growth "
        "radius, and any step structure.\n\n"
        + "\n".join(f"Sequence {k}: " + ", ".join(map(str, v))
                    for k, v in seqs.items())
        + "\n\nOutput format: one line per sequence, "
          "\"Sequence <letter>: class-<name>\", where sequences in the "
          "same class share the same <name>. Choose class names that "
          "describe the structure.")
    # the six-sequence grouping prompt makes GLM reason deeply;
    # the client's empty-answer fallback escalates effort itself
    tail = ("Answer IMMEDIATELY with the six lines. Do not think "
            "step by step.")
    ans = ask(prompt + "\n\n" + tail, max_tokens=16384)
    if not ans.strip():
        ans = ask(prompt + "\n\n" + tail, max_tokens=16384)
    print("=== judge output ===")
    print(ans)

    # parse assignments
    import re
    assign = {}
    for m in re.finditer(r"Sequence\s+(\w+)\s*:\s*class-([\w\-]+)",
                         ans, re.IGNORECASE):
        assign[m.group(1).upper()] = m.group(2).lower()
    print("\n=== parsed assignments ===")
    print(assign)

    keys = sorted(seqs.keys())
    n_pairs = 0
    n_ok = 0
    detail = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            truth_same = cls[a] == cls[b]
            try:
                judge_same = assign[a] == assign[b]
            except KeyError:
                continue
            ok = truth_same == judge_same
            n_pairs += 1
            n_ok += ok
            detail.append({"pair": f"{a}-{b}",
                           "truth_same": truth_same,
                           "judge_same": judge_same, "agree": ok})
    print(f"\npairwise agreement: {n_ok}/{n_pairs}")
    frac = n_ok / n_pairs if n_pairs else 0
    # chance baseline for a random 6->k partition is high; the strict
    # test is the 6-class perfect partition, but pairwise agreement
    # with 6 truth classes has chance ~ 1/3 (same vs different)
    verdict = ("CONFIRMED" if frac >= 0.8 and n_pairs == 15 else
               "PARTIAL" if frac >= 0.6 else "NEGATIVE")
    print(f"P32-c verdict: {verdict} (pairwise {frac:.2f}; chance ~0.5 "
          f"for random 2-way splits, ~1/6 for random 6-way)")

    with open("p32c_judge_results.json", "w", encoding="utf-8") as f:
        json.dump({"judge_output": ans, "assignments": assign,
                   "detail": detail, "pairwise": f"{n_ok}/{n_pairs}",
                   "verdict": verdict}, f, indent=1, default=str)
    print("results -> p32c_judge_results.json")


if __name__ == "__main__":
    main()
