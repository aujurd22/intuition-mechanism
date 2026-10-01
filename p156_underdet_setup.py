"""P156: UNDERDETERMINATION RESOLUTION for sci_data (P155's open finding).

P155 measured residual H=0.357 (only 50% unanimous) on the sci-data
domain while doubao reads 93.8% accurate — at least two DIFFERENT
transferable structures fit the discovery set.

Protocol:
  1. ELICIT  — each model states its anomaly rule on the SAME regime-A
               discovery set (the p153 setup).
  2. DISCRIMINATE — probes constructed so a SURFACE sign rule ("negative
               window t~[1,2.25] => anomalous") and the SEMANTIC rule
               ("phase inversion relative to the series' own oscillation")
               give OPPOSITE verdicts:
                 T4-normal:   neg window present, NOT anomalous
                 T4-inverted: neg window absent (flipped to pos), IS anomalous
                 T6-normal / T6-inverted: same pair at T=6
  3. ADJUDICATE — generator truth vs each model's verdicts; classify each
     model as surface-rule follower or semantic-rule follower.
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("HF_HUB_OFFLINE", "1")

# ---- series generation (same law as sdb/domain_scidata) ----
def gen_series(T, gamma, A=1.0, n=40, dt=0.25, anomaly=False):
    xs = []
    for i in range(n):
        t = i * dt
        v = A * math.exp(-gamma * t) * math.sin(2 * math.pi * t / T)
        if anomaly and (i // 5) % 2 == 1:
            v = -v
        xs.append(round(v, 4))
    return xs


import math
DISC_REGIME = (2.0, 0.10)
rng_seed = 20261001
import random
rng = random.Random(rng_seed)
disc = []
for anom in (False, True):
    for rep in range(5):
        A = round(1.0 + 0.5 * (rep % 3), 2)
        disc.append({"series": gen_series(DISC_REGIME[0], DISC_REGIME[1],
                                          A=A, anomaly=anom),
                     "anomalous": anom})
# discovery set: 6 normal + 4 anomalous (as p153)

DISCRIM = []
for T in (4.0, 6.0):
    for anom in (False, True):
        DISCRIM.append({"T": T, "series": gen_series(T, 0.10, A=1.2,
                                                     anomaly=anom),
                        "anomalous": anom})
# surface-sign truth per discriminator: is window t~[1.0,2.25] negative?
for p in DISCRIM:
    w = p["series"][4:10]          # t = 0.75..2.25 window
    p["neg_window"] = sum(1 for v in w if v < 0) >= 3
print("discriminators:")
for p in DISCRIM:
    print(f"  T={p['T']} anomalous={p['anomalous']} neg_window={p['neg_window']} "
          f"series[:8]={p['series'][:8]}")

json.dump({"disc": disc, "discrim": DISCRIM},
          open("p156_underdet_setup.json", "w"), indent=1)
print("setup saved")
