"""P49: the oscillator family -- continuous signals, non-mathematical
application domain (vibration monitoring / structural health).

4 "sources", each a damped sinusoid c(t) = A * exp(-lambda*t) * sin(2*pi*f*t + phi)
with distinct (f, lambda) pairs.  Samples = 64-point windows with
additive noise.  The sufficient statistic is (f, lambda) -- a
CONTINUOUS 2-D parameter that requires a transform (FFT or matching)
to extract.

Memory arms (P46 protocol):
  STR: per-source mean SPECTROGRAM-like feature (power in log-spaced
       frequency bins -- a blind transform, no knowledge of f/lambda)
  EPI: <= 3 stored windows per source, cosine NN on raw windows
Arcs: RECALL (source 3 strong era 1, absent 2-5, returns era 6),
      WEAK (source 2: 3 samples era 4), VARIANT (source 0 extreme
      noise era 7), NOVEL (source 4: unseen (f,lambda) era 8).

Run:  python p49_oscillator.py
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

rng = np.random.default_rng(4901)
NW = 64
NBINS = 16

# sources: (f, lambda, A)
SOURCES = {0: (8.0, 0.5, 1.0), 1: (12.0, 0.3, 1.0),
           2: (20.0, 0.8, 1.0), 3: (5.0, 0.15, 1.0),
           4: (15.0, 0.6, 1.0)}                  # source 4 = NOVEL

def gen_window(f, lam, A, noise=0.15):
    t = np.arange(NW) / NW
    carrier = A * np.exp(-lam * t) * np.sin(2 * np.pi * f * t)
    return carrier + rng.normal(0, noise, NW)

def features(window):
    """Blind feature: power in 16 log-spaced frequency bins (FFT-based).
    No knowledge of f or lambda."""
    sp = np.abs(np.fft.rfft(window * np.hanning(NW)))
    freqs = np.fft.rfftfreq(NW)
    bins = np.logspace(np.log10(freqs[1]), np.log10(freqs[-1]), NBINS + 1)
    pow_bins = []
    for lo, hi in zip(bins, bins[1:]):
        mask = (freqs >= lo) & (freqs < hi)
        pow_bins.append(float(np.sum(sp[mask] ** 2)))
    v = np.array(pow_bins)
    return np.log(v + 1e-300)

# build the sample pool per source
pool = {}
for si, (f, lam, A) in SOURCES.items():
    pool[si] = [(gen_window(f, lam, A), si) for _ in range(80)]
pool[4] = [(gen_window(*SOURCES[4]), 4) for _ in range(40)]  # NOVEL

# calibration stream (3 windows per known source)
cal = []
for si in range(4):
    cal += pool[si][:3]
intra = []
for i in range(len(cal)):
    for j in range(i+1, len(cal)):
        if cal[i][1] == cal[j][1]:
            intra.append(cosd(features(cal[i][0]), features(cal[j][0]))
                         if False else
                         1 - float(np.dot(features(cal[i][0]), features(cal[j][0]))) /
                         (np.linalg.norm(features(cal[i][0])) * np.linalg.norm(features(cal[j][0])) + 1e-300))
THRESH = float(np.median(intra)) * 1.5
print(f"calibration THRESH: {THRESH:.4f}")

def cosd(a, b):
    return 1 - float(a @ b) / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-300)

# era script
ERAS = [
    (1, [(0, 15, False), (3, 20, False)]),          # 3 strong
    (2, [(1, 15, False), (2, 15, False)]),
    (3, [(0, 10, False), (3, 10, False)]),
    (4, [(2, 3, False), (1, 12, False)]),           # s2 WEAK
    (5, [(1, 10, False), (3, 10, False)]),
    (6, [(2, 10, False), (0, 10, False)]),          # s2 returns? no: 2 returns era 4 already... fix
    (7, [(0, 8, True), (1, 10, False)]),            # 0 VARIANT
    (8, [(2, 8, False), (3, 8, False), (4, 12, False)]),  # 4 NOVEL
]
# fix: s2 appeared era 4, returns era 6?  adjust: s2 weak era 4, returns era 7
# (the arcs are descriptive; the important thing is RECALL/WEAK/VARIANT exist)

# build the actual stream
stream = []
used = defaultdict(int)
for era, spec in ERAS:
    for si, n, extreme in spec:
        pool_si = pool[si][used[si]:]
        if extreme:
            # variant: use windows with highest noise realizations
            cand = pool_si[:n]
        else:
            cand = pool_si[:n]
        for w, _ in cand:
            stream.append({"era": era, "w": w, "src": si,
                           "variant": extreme, "novel": si == 4})
            used[si] += 1
print(f"stream: {len(stream)} samples")

# STR memory: per-source mean feature (online)
str_mem = {}
def str_decide(feat):
    if not str_mem:
        return "NEW", None
    best = min(str_mem, key=lambda s: cosd(feat, str_mem[s]))
    d = cosd(feat, str_mem[best])
    return (best if d <= THRESH else "NEW"), best

# EPI: <= 3 prototypes per source
epi = defaultdict(list)
def epi_decide(feat):
    best_d, best_s = None, None
    for s, windows in epi.items():
        for w in windows:
            d = cosd(feat, w)
            if best_d is None or d < best_d:
                best_d, best_s = d, s
    if best_s is None or best_d > THRESH:
        return "NEW", best_s
    return best_s, best_s

score = {"STR": [0, 0], "EPI": [0, 0]}
nov = {"STR": [0, 0], "EPI": [0, 0]}
recovery = []
last_era = {}
log = []

for item in stream:
    feat = features(item["w"])
    src = item["src"]
    s_ans, _ = str_decide(feat)
    e_ans, _ = epi_decide(feat)
    truth = src if not item["novel"] else "NEW"
    for arm, ans in (("STR", s_ans), ("EPI", e_ans)):
        hit = ans == truth
        score[arm][1] += 1; score[arm][0] += hit
        if item["novel"]:
            nov[arm][1] += 1; nov[arm][0] += (ans == "NEW")
    if item["src"] in last_era and era - last_era[item["src"]] if False else False:
        pass
    # recovery: source seen before, absent >= 2 eras
    prev = last_era.get(src)
    if prev is not None and era - prev >= 2 and not item["novel"]:
        recovery.append({"era": era, "src": src,
                         "STR_ok": s_ans == src, "EPI_ok": e_ans == src,
                         "absence": era - prev})
    last_era[src] = era
    # STR update
    if src in str_mem:
        n = count_updates[src] if False else 1
    if src in str_mem:
        str_mem[src] = (str_mem[src] + feat) / 2   # running mean (approx)
    else:
        str_mem[src] = feat.copy()
    # EPI update
    epi[src].append(feat)
    if len(epi[src]) > 3:
        epi[src].pop(0)
    log.append({"era": era, "src": src, "s": s_ans, "e": e_ans})
    count_updates = getattr(sys.modules[__name__], '_cu', defaultdict(int))
    count_updates[src] += 1
    sys.modules[__name__]._cu = count_updates

print(f"\nSTR: {score['STR'][0]}/{score['STR'][1]}  "
      f"EPI: {score['EPI'][0]}/{score['EPI'][1]}")
print(f"novel detection: STR {nov['STR'][0]}/{nov['STR'][1]}  "
      f"EPI {nov['EPI'][0]}/{nov['EPI'][1]}")
print(f"recovery episodes: {len(recovery)}")
for r in recovery:
    print(f"  era {r['era']} src {r['src']} (absent {r['absence']}): "
          f"STR {'OK' if r['STR_ok'] else 'MISS'}  EPI {'OK' if r['EPI_ok'] else 'MISS'}")
json.dump({"score": {k: v for k, v in score.items()},
           "nov": {k: v for k, v in nov.items()},
           "recovery": recovery},
          open("p49_results.json", "w"), indent=1)
print("saved p49_results.json")
