"""Sample-efficiency curve: three arms x {10%, 50%, 100%} data x 1 seed.
GPU task, sequential. Outputs se_curve_results.json"""
import json
import subprocess
import sys

ARMS = ["vcnet-kwta", "vcnet-relu", "plain"]
FRACS = [(4000, "10%"), (20000, "50%"), (0, "100%")]
results = []
for sub, label in FRACS:
    for arm in ARMS:
        args = ["C:/Users/djr82/AppData/Local/Programs/Python/Python313/python.exe",
                "train.py", arm, "--seed", "0", "--subsample", str(sub),
                "--epochs", "25" if sub else "15"]
        print(f"=== {arm} @ {label} ===", flush=True)
        r = subprocess.run(args, capture_output=True, text=True, timeout=3600)
        final = [l for l in r.stdout.splitlines() if "FINAL" in l]
        results.append(dict(arm=arm, frac=label,
                            final=final[-1] if final else "NO FINAL"))
        json.dump(results, open("se_curve_results.json", "w"), indent=1)
        print(results[-1]["final"], flush=True)
print("SE CURVE COMPLETE", flush=True)
