"""Full-data three-arm x 3-seed comparison, sequential (GPU discipline)."""
import subprocess, sys, json, time
ARMS = ["vcnet-kwta", "vcnet-relu", "plain"]
SEEDS = [0, 1, 2]
results = []
for arm in ARMS:
    for seed in SEEDS:
        t0 = time.time()
        r = subprocess.run(["C:/Users/djr82/AppData/Local/Programs/Python/Python313/python.exe",
                            "train.py", arm, "--seed", str(seed),
                            "--epochs", "15"],
                           capture_output=True, text=True, timeout=3600)
        final = [l for l in r.stdout.splitlines() if "FINAL" in l]
        results.append(dict(arm=arm, seed=seed,
                            final=final[-1] if final else "NO FINAL",
                            secs=round(time.time()-t0)))
        json.dump(results, open("spots10_full_results.json", "w"), indent=1)
        print(results[-1], flush=True)
print("FULL COMPARISON COMPLETE", flush=True)
