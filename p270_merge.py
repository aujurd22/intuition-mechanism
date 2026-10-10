# -*- coding: utf-8 -*-
"""P270 merge: paired verdict for gate vs nogate on ls20.
Usage: python p270_merge.py   (reads p270_*_ls20.jsonl + p270_*_final.json)
"""
import json, glob, os, math

def load_jsonl(f):
    rows = []
    for line in open(f, encoding="utf-8"):
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def main():
    out = {}
    for cond in ["nogate", "gate"]:
        rows = load_jsonl(f"p270_{cond}_ls20.jsonl") if os.path.exists(
            f"p270_{cond}_ls20.jsonl") else []
        fin = {}
        if os.path.exists(f"p270_{cond}_final.json"):
            fin = json.load(open(f"p270_{cond}_final.json", encoding="utf-8"))
        sc = fin.get("scorecard") or {}
        if isinstance(sc, str):
            try:
                sc = json.loads(sc)
            except Exception:
                sc = {}
        envs = sc.get("environments", [])
        levels = actions = 0
        score = 0.0
        completed = 0
        for e in envs:
            levels += e.get("levels_completed", 0)
            actions += e.get("actions", 0)
            score += e.get("score", 0.0)
            completed += int(e.get("completed", False))
        out[cond] = {"steps_logged": len(rows),
                     "levels_completed": levels, "actions": actions,
                     "score": round(score, 3), "games_completed": completed,
                     "final_state": (envs[0].get("runs", [{}])[-1].get("state")
                                     if envs and envs[0].get("runs") else None)}
    for cond in ["nogate", "gate"]:
        if isinstance(out[cond].get("scorecard"), str):
            try:
                out[cond]["scorecard"] = json.loads(out[cond]["scorecard"])
            except Exception:
                out[cond]["scorecard"] = {}
    # gate arm claim precision trajectory
    gate_rows = load_jsonl("p270_gate_ls20.jsonl") if os.path.exists(
        "p270_gate_ls20.jsonl") else []
    precs = [r["precision"] for r in gate_rows if r.get("precision") is not None]
    n = len(precs)
    if n >= 4:
        h1 = sum(precs[:n//2]) / (n//2)
        h1_late = sum(precs[n//2:]) / (n - n//2)
        out["H1_precision_early_vs_late"] = {
            "early": round(h1, 3), "late": round(h1_late, 3),
            "improved": bool(h1_late > h1)}
    out["H1_refuted_count"] = sum(1 for r in gate_rows
                                  if r.get("verdict") == "REFUTED")
    out["H1_total_claimed_steps"] = n
    # headline comparison
    cmp_ = {}
    for k in ("levels_completed", "actions", "score"):
        cmp_[k] = {"nogate": out["nogate"].get(k), "gate": out["gate"].get(k)}
    out["H2_headline"] = cmp_
    json.dump(out, open("p270_verdict.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
