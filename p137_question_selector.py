"""P137: mechanized problem selection v1 — the P136 greedy loop, actually run.

State store: docs/RESEARCH_PLAN.md (108 rows) + open_questions.json.
Value function (zero LLM calls, all mechanical):

  score(q) = w_f * feasibility(q)
           + w_g * info_gain(q)          [registry graph: how many closed
                                           rows the question touches]
           + w_s * taste_surprise(q)     [does it open a NEW axis?]
           + w_u * taste_utility(q)      [how close to published results?]

v1 weights equal; feasibility from verifier type; info_gain = fraction
of registry rows sharing a key term with the question's unlocks;
surprise/utility from the open_questions.json flags + registry evidence.

DEVICE-VALIDITY TEST: compare the selector's ranking against the order
a human researcher (me) actually picked over the last session — the
human ran OQ-analogues in the order: census extension (P121) ->
staleness detector (P126/P130-b) -> calibration matrix (P128-131) ->
chain write-out (P135).  If the selector's top-1 is locally executable,
RUN IT.
"""
import json, re, os
from collections import Counter

# ---------------------------------------------------------------- registry
text = open("docs/RESEARCH_PLAN.md", encoding="utf-8").read()
rows = re.findall(r"^\| (P\d+[a-z]?(?:-[a-z0-9]+)?) \|(.*?)\|$", text, re.M | re.S)
row_bodies = {}
for pid, body in rows:
    row_bodies.setdefault(pid.split("-")[0], []).append(body)
n_rows = len(row_bodies)
retracted = sum(1 for bodies in row_bodies.values()
                if any(("RETRACT" in b.upper() or "SUPERSEDED" in b.upper())
                       for b in bodies))
print(f"registry: {n_rows} unique P-numbers, {retracted} with retraction/supersession markers")

STOP = set("the a an and or of to in on at for with by from as is are was were be "
           "been not no all its his her their this that these those it into over "
           "under than then when where which who whom whose what why how can may "
           "will would should could per vs via plus but if only same new".split())


def tokens(s):
    return Counter(w for w in re.findall(r"[a-zA-Z][a-zA-Z_-]{2,}", s.lower())
                   if w not in STOP)


reg_tokens = {pid: tokens(" ".join(bodies)) for pid, bodies in row_bodies.items()}
DF = Counter()
for tc in reg_tokens.values():
    DF.update(set(tc))

# ---------------------------------------------------------------- scoring
oq = json.load(open("open_questions.json", encoding="utf-8"))["open_questions"]
FEAS = {"local_data": 1.0, "numeric": 0.9, "enumeration": 0.8,
        "api_llm": 0.55, "human": 0.2, "proof": 0.3}

results = []
for q in oq:
    qtok = tokens(q["title"] + " " + q["description"] + " "
                  + " ".join(q["unlocks"]))
    # info gain: registry coverage of the question's vocabulary (idf-weighted)
    hits = [p for p, tc in reg_tokens.items()
            if len(set(qtok) & set(tc)) >= 2]
    gain = len(hits) / n_rows
    feas = FEAS[q["verifier"]]
    surprise = 1.0 if q["new_axis"] else 0.3
    utility = 1.0 if q["near_published"] else 0.4
    score = feas + gain + surprise + utility      # equal weights v1
    results.append({"id": q["id"], "title": q["title"], "score": round(score, 3),
                    "feasibility": feas, "info_gain": round(gain, 3),
                    "surprise": surprise, "utility": utility,
                    "registry_hits": len(hits), "verifier": q["verifier"]})

results.sort(key=lambda r: -r["score"])
print("\n=== v1 greedy ranking (equal weights) ===")
for i, r in enumerate(results, 1):
    print(f"{i}. [{r['id']}] score={r['score']}  feas={r['feasibility']} "
          f"gain={r['info_gain']} S={r['surprise']} U={r['utility']}  "
          f"({r['verifier']})\n   {r['title'][:90]}")

json.dump({"ranking": results,
           "human_order_analogue": ["census [1,300] (done, =OQ2 class)",
                                    "staleness detector (done, =OQ1 class)",
                                    "calibration matrix (done)",
                                    "chain write-out (done, =P135)"],
           "weights": "equal v1"},
          open("p137_selector_output.json", "w"), indent=1)

top = results[0]
print(f"\nTOP-1: [{top['id']}] {top['title'][:100]}")
print("verifier:", top["verifier"], "=> locally executable, running it now."
      if top["verifier"] in ("local_data", "numeric") else "=> needs API/human, dispatching design only.")
