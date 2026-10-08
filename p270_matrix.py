"""Sequential driver for the P270 comparison matrix.
Runs every (game, arm) plan entry; writes one summary json per run and
a combined matrix.json at the end. Designed for background execution:
robust to per-run failures (failures recorded, loop continues)."""
import json
import subprocess
import sys
import time

PLAN = json.load(open("p270_matrix_plan.json", encoding="utf-8"))
PY = PLAN[0][0]
results = []
for i, entry in enumerate(PLAN):
    cmd = [PY] + entry[1:]
    game, arm = entry[3], entry[2]
    print(f"=== [{i+1}/{len(PLAN)}] {arm} {game} ===", flush=True)
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=7200)  # 2h cap per run
        tail = [l for l in r.stdout.splitlines() if l.startswith("[")][-3:]
        for l in tail:
            print("   ", l, flush=True)
        results.append(dict(game=game, arm=arm, exit=r.returncode,
                            secs=round(time.time()-t0, 1),
                            tail=tail[-1] if tail else ""))
    except subprocess.TimeoutExpired:
        results.append(dict(game=game, arm=arm, exit="TIMEOUT",
                            secs=round(time.time()-t0, 1), tail=""))
    except Exception as e:
        results.append(dict(game=game, arm=arm, exit=f"ERR {e!r}"[:80],
                            secs=round(time.time()-t0, 1), tail=""))
    json.dump(results, open("p270_matrix_results.json", "w"), indent=1)
print("MATRIX COMPLETE", flush=True)
