"""repr_pricer.py — representation pricing (external review item 2, P210).
Prices the discovery-value of switching representations:
  price(r1 -> r2) = sum over architectures of [acc(r2, arch) - acc(r1, arch)]
Positive = r2 discovers more (worth switching); negative = wrong-axis penalty.
Connects to leg-1 combo-replay: each representation morphism in the replay
gets priced this way, turning replay from qualitative to scaled (bits/discovery).
"""
import json

GRID = json.load(open("p204_repr_arch_grid.json", encoding="utf-8"))
EXT = json.load(open("p204b_extended.json", encoding="utf-8"))

def acc(task, rep, arch):
    k = f"{task}/{rep}/{arch}"
    if k in GRID:
        return GRID[k]["bal_acc_mean"]
    if k in EXT:
        return EXT[k]
    if arch == "transformer" and rep == "decimal":
        return EXT.get(f"{task}/decimal/transformer")
    return None

def price(task, r1, r2, archs=("mlp", "kwta", "cnn", "transformer")):
    """discovery-value of switching r1 -> r2 on `task`, summed over architectures"""
    total, breakdown = 0.0, {}
    for a in archs:
        a1, a2 = acc(task, r1, a), acc(task, r2, a)
        if a1 is None or a2 is None:
            continue
        breakdown[a] = round(a2 - a1, 3)
        total += a2 - a1
    return {"total": round(total, 3), "verdict": ("POSITIVE: switch worth it" if total > 0.2
             else "NEGATIVE: wrong-axis penalty" if total < -0.2 else "NEUTRAL"),
            "breakdown": breakdown}

if __name__ == "__main__":
    out = {}
    print("=== representation pricing (discovery-value of switching) ===\n")
    pairs = [
        ("synthetic", "decimal", "modular"), ("synthetic", "raw", "modular"),
        ("synthetic", "decimal", "raw"),
        ("census", "decimal", "modular"), ("census", "raw", "modular"),
        ("census", "decimal", "raw"),
    ]
    for task, r1, r2 in pairs:
        p = price(task, r1, r2)
        out[f"{task}: {r1} -> {r2}"] = p
        print(f"{task:<10} {r1:>8} -> {r2:<8} total={p['total']:+.3f}  {p['verdict']}")
        for a, v in p["breakdown"].items():
            print(f"    {a:<12} {v:+.3f}")
    json.dump(out, open("repr_pricer_matrix.json", "w"), indent=1)
    print("\nsaved repr_pricer_matrix.json")
