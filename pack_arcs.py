# -*- coding: utf-8 -*-
"""pack_arcs.py — the intuition-pack arm for P270 (ARC-AGI-3).

Flow:
  1. exemplars: every P270 gate/nogate step is a free labeled sample —
     (frame features, action) -> actual frame diff from the game engine
     (verifier-backed: the game IS the verifier, cost 0).
     Positive = the action's diff was "productive" (large or new-cell
     diff); negative = low-yield repeat diff.
  2. pack_build("arc-action", ...) via intuition_pack.
  3. In-game: pack score ranks the available actions; GLM is consulted
     only when the pack abstains (insufficient confidence) — cutting
     expensive vision calls.

Usage:
  python pack_arcs.py build  <p270_log.jsonl>...        # build pack from logs
  python pack_arcs.py probe  <p270_log.jsonl>...        # is ARC a compression domain?
"""
import json
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PACK_DOMAIN = "arc-action"


def load_steps(paths):
    """Extract step records from P270 jsonl logs."""
    steps = []
    for p in paths:
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("event"):        # glm_error / unparseable / env_error
                continue
            if "action" in r and "actual_n" in r:
                steps.append(r)
    return steps


def step_features(r):
    """Compact frame-independent features for the exemplar input."""
    return {
        "action": r.get("action"),
        "actual_n": r.get("actual_n", 0),
        "actual_sample": r.get("actual_sample", [])[:8],
        "avail": r.get("avail", []),
        "step_parity": r.get("step", 0) % 4,
    }


def label_of(r):
    """Productive action = large diff (state transitions in ARC games
    show up as 52-cell screen changes; 2-cell diffs are no-ops)."""
    n = r.get("actual_n", 0)
    return "RATIONAL" if n >= 20 else "NOT"


def build(paths):
    from intuition_pack.pack import build_pack
    from intuition_pack.server import get_store
    steps = load_steps(paths)
    if not steps:
        print("no steps found in", paths)
        return
    exemplars = []
    for i, r in enumerate(steps):
        f = step_features(r)
        f["id"] = i
        exemplars.append(dict(
            d=i,
            inputs={"action": f["action"], "actual_n": f["actual_n"],
                    "actual_sample": f["actual_sample"],
                    "step_parity": f["step_parity"]},
            label=label_of(r),
            note=("large-diff transition" if f["actual_n"] >= 20
                  else "low-yield repeat diff")))
    charter = ("ARC-AGI-3 action selection: a single evidence source — "
               "the actual frame diff reported by the game engine after "
               "the action executes. An action is RATIONAL when it "
               "produces a large state transition (actual_n >= 20 cells) "
               "and NOT when it repeats a low-yield small diff. The game "
               "engine is the only evidence source; no model opinion.")
    verifier_rule = ("execution: replay/check the action's actual frame "
                     "diff against the recorded actual_n (game-engine "
                     "ground truth)")
    pack = build_pack(PACK_DOMAIN, charter, exemplars,
                      {"name": "frame-diff-execution",
                       "rule": verifier_rule},
                      "p270 logs")
    get_store().put(PACK_DOMAIN, pack.to_json())
    pos = sum(1 for e in exemplars if e["label"] == "RATIONAL")
    print(f"pack built: domain={PACK_DOMAIN} exemplars={len(exemplars)} "
          f"(RATIONAL {pos} / NOT {len(exemplars)-pos})")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd, paths = sys.argv[1], sys.argv[2:]
    if cmd == "build":
        build(paths)
    elif cmd == "probe":
        steps = load_steps(paths)
        print(f"{len(steps)} steps; RATIO productive:",
              sum(1 for r in steps if r.get("actual_n", 0) >= 20),
              "/", len(steps))
    else:
        print(__doc__)
