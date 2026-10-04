"""P190: boundary-pricing dashboard v1 (L4-5).
Metric per review: discovery cost = binary boundary queries consumed per
accepted rule. v1 accounting from the P186-c/d formal runs:
  per (model, seed) run: 1 law call + 4 apply calls (the fixed cost),
  boundary probes = probes with >=1 error across runs (where a human/LLM
  binary tiebreak would be spent), ambiguity = err count across runs.
"""
import json

d = json.load(open("p186c_math_fixed.json", encoding="utf-8"))
probes = 32
rows = []
all_err = {}
for model, v in d["models"].items():
    for seed, acc in zip([0, 1, 2], v["seed_accs"]):
        errs = sum(v["err_counts"].values())
        rows.append({"model": model, "seed": seed, "acc": acc,
                     "law_calls": 1, "apply_calls": 4,
                     "rule_len": len(d["rules"].get(f"{model}/seed{seed}", ""))})
    for pid, cnt in v["err_counts"].items():
        all_err[pid] = all_err.get(pid, 0) + cnt

n_runs = len(rows)
boundary = {p: c for p, c in sorted(all_err.items(), key=lambda kv: -kv[1])}
total_boundary = sum(1 for c in boundary.values())
bits = sum(c for c in boundary.values())
print(f"runs: {n_runs}  probes/run: {probes}")
print(f"boundary probes (>=1 err in 9 runs): {total_boundary}/{probes}")
print(f"total error-bits: {bits}  -> tiebreak cost if 1 bit each: {bits} queries")
print(f"accepted rules: {n_runs} (one per run)  -> bits/rule = {bits / n_runs:.1f}")
print("\nper-probe ambiguity (err count across 9 runs):")
for p, c in boundary.items():
    print(f"  d={p}: {c}")
print("\nrun ledger:")
for r in rows:
    print(f"  {r['model']} seed{r['seed']}: acc={r['acc']}%  rule_len={r['rule_len']}  cost=5 calls")

json.dump({"rows": rows, "boundary": boundary, "bits_per_rule": bits / n_runs},
          open("p190_boundary_dashboard.json", "w"), indent=1)
print("saved p190_boundary_dashboard.json")
