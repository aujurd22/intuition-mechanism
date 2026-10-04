"""P32-h runner: blind API judge on the balanced novelty-detection
design (p32h_design.json).  Judge = doubao-seed-2.1-lite, thinking
disabled (reasoning effort minimal), reasoning-before-answer per the
P32-g registered fixes.  Answer format: last line "ANSWER: A|B|C|NEW".
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
from llm_client import ask_chat as ask  # noqa: E402

PROMPT = """You are given six integer sequences grouped into three families. Each family is defined by a shared generation rule; the two members of a family are different instances of the SAME rule.

{blocks}

A holdout sequence H must be classified:
- "A", "B", or "C" if H is a new instance of that family's rule (same rule, different instance -- the numbers will NOT literally match);
- "NEW" if H follows a rule not represented by any of A, B, C.

Reason carefully about the generation rule of each family (how later terms are built from earlier structure), then reason about H. Give your reasoning FIRST. End your reply with exactly one line:
ANSWER: A
or ANSWER: B or ANSWER: C or ANSWER: NEW

IMPORTANT: keep the reasoning under 200 words total. Do NOT attempt exhaustive term-by-term formula derivation; compare structural patterns (growth rate, sign pattern, prefix shape) at a high level. Then end with the ANSWER line.
"""


def build_prompt(trial_blocks):
    return PROMPT.format(blocks=trial_blocks)


def parse_answer(text):
    m = re.findall(r"ANSWER:\s*(A|B|C|NEW)", text, flags=re.I)
    return m[-1].upper() if m else None


def main():
    design = json.load(open("p32h_design.json"))
    mats = open("p32h_materials.txt", encoding="utf-8").read()
    blocks = {}
    for chunk in mats.split("=== ")[1:]:
        head, body = chunk.split(" ===\n", 1)
        blocks[int(head.split()[1])] = body.strip()

    answers = {}
    for t in design["trials"]:
        tid = t["trial"]
        if str(tid) in answers:
            continue
        prompt = build_prompt(blocks[tid])
        reply = ask(prompt)
        ans = parse_answer(reply)
        answers[str(tid)] = {"answer": ans, "reply_len": len(reply)}
        ok = ans == t["truth"]
        print(f"T{tid:02d} [{t['kind']:8s}] truth={t['truth']:3s} "
              f"judge={ans} {'OK' if ok else 'MISS'}", flush=True)
        with open("p32h_judge_answers.json", "w") as f:
            json.dump(answers, f, indent=1)

    # score
    n_ok = n_new_ok = n_ex_ok = 0
    for t in design["trials"]:
        a = answers[str(t["trial"])]["answer"]
        if a == t["truth"]:
            n_ok += 1
            if t["kind"] == "new":
                n_new_ok += 1
            else:
                n_ex_ok += 1
    print(f"\nTOTAL {n_ok}/40 | existing {n_ex_ok}/20 | new {n_new_ok}/20")


if __name__ == "__main__":
    main()
