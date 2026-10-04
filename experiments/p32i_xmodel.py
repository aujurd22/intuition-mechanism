"""P32-i: causal cue intervention on the P32-h novelty task
(pre-registered, docs/RESEARCH_PLAN.md P32-i row).

Two intervention arms on the SAME 40 trials, same blind judge
(doubao-seed-2.1-lite, thinking disabled, 200-word reasoning bound):

  arm S (scaffold): the prompt supplies the cue-extraction PROCEDURE
      (the P34-d support signature: t2 vs 6, t3 vs 20, t4 vs 70,
      sign-flip presence) and requires the judge to compute each
      sequence's signature explicitly before answering.  This tests
      the causal claim behind the P32-h dissociation: the judge fails
      at novelty because it does not extract the sufficient cue, not
      because the novelty comparison itself is hard.
  arm T (truncated): the original prompt with every sequence cut to
      its first 8 terms.  Tests whether less distractor material
      alone restores extraction (the attention-dilution reading).
      Mechanical ceiling on the 276 families used: tree@W8 = 266/276
      (96.4%; the misses are (5,alt) families whose first flip lands
      after term 8).

Pre-registered predictions:
  arm S: extraction-bottleneck claim SUPPORTED if existing >= 90%
      AND new >= 70%;
  arm T: attention-dilution reading SUPPORTED if new >= 50%;
      UNAFFECTED if new < 35%.

Run:  python p32i_run.py S   then   python p32i_run.py T
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
from llm_client import ask_chat  # noqa: E402
from p32h_run import parse_answer  # noqa: E402

SCAFFOLD = """

MANDATORY PROCEDURE: for EVERY sequence below (each family member and
the holdout), first compute its support signature:
  (1) third term: is it greater than, less than, or equal to 6?
  (2) fourth term: is it greater than, less than, or equal to 20?
  (3) fifth term: is it greater than, less than, or equal to 70?
  (4) does the sequence change sign anywhere?
These four observations determine the generation class of a sequence;
two sequences belong to the same family IF AND ONLY IF their classes
match.  Show each sequence's signature explicitly, then decide.
"""


def truncate_terms(body, keep):
    out = []
    for line in body.splitlines():
        if line.startswith(("Family", "Holdout")):
            head, seq = line.split(": ", 1)
            terms = seq.split(", ")
            out.append(f"{head}: " + ", ".join(terms[:keep]))
        else:
            out.append(line)
    return "\n".join(out)


def main():
    arm = sys.argv[1]
    model_tag = sys.argv[2]
    assert arm in ("S", "T")
    design = json.load(open("p32h_design.json"))
    mats = open("p32h_materials.txt", encoding="utf-8").read()
    blocks = {}
    for chunk in mats.split("=== ")[1:]:
        head, body = chunk.split(" ===\n", 1)
        blocks[int(head.split()[1])] = body.strip()

    base_prompt = ("You are given six integer sequences grouped into three "
                   "families. Each family is defined by a shared generation "
                   "rule; the two members of a family are different instances "
                   "of the SAME rule.\n\n{blocks}\n\n"
                   "A holdout sequence H must be classified:\n"
                   '- "A", "B", or "C" if H is a new instance of that '
                   "family's rule (same rule, different instance -- the "
                   "numbers will NOT literally match);\n"
                   '- "NEW" if H follows a rule not represented by any of '
                   "A, B, C.\n\n"
                   "Reason carefully, keep it under 200 words, and end with "
                   "exactly one line: ANSWER: A (or B / C / NEW).")

    out_path = f"p32i_{model_tag}_arm{arm}_answers.json"
    answers = {}
    if os.path.exists(out_path):
        answers = json.load(open(out_path))
    for t in design["trials"]:
        tid = t["trial"]
        if str(tid) in answers:
            continue
        body = blocks[tid]
        if arm == "S":
            prompt = base_prompt.format(blocks=body) + SCAFFOLD
        else:
            prompt = base_prompt.format(blocks=truncate_terms(body, 8))
        reply = ask_chat(prompt)
        ans = parse_answer(reply)
        answers[str(tid)] = {"answer": ans, "reply_len": len(reply)}
        ok = ans == t["truth"]
        print(f"[{arm}] T{tid:02d} [{t['kind']:8s}] truth={t['truth']:3s} "
              f"judge={ans} {'OK' if ok else 'MISS'}", flush=True)
        json.dump(answers, open(out_path, "w"), indent=1)

    n_ok = n_ex = n_new = ex_n = new_n = 0
    for t in design["trials"]:
        a = answers[str(t["trial"])]["answer"]
        hit = a == t["truth"]
        n_ok += hit
        if t["kind"] == "existing":
            ex_n += 1
            n_ex += hit
        else:
            new_n += 1
            n_new += hit
    print(f"\narm {arm} [{model_tag}]: total {n_ok}/40 | existing {n_ex}/{ex_n} "
          f"| new {n_new}/{new_n}")


if __name__ == "__main__":
    main()
