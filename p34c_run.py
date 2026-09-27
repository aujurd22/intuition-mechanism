import json

d = json.load(open('p34c_corpus.json'))
truth = d['truth']
fams = d['families']

def my_answer(seq, w):
    s = seq[:w]
    neg = [i for i, x in enumerate(s) if x < 0]
    if not neg:
        r = [abs(s[i+1]/s[i]) if s[i] else 0 for i in range(len(s)-1)]
        if len(r) >= 4 and r[3] > 6:
            return (2, 'no')
        if len(r) >= 4 and r[2] > 5 and r[3] <= 6:
            return (3, 'no')
        if len(r) >= 5 and max(r[3:5]) < 4.5:
            return (5, 'no')
        return (4, 'no')
    f = neg[0]
    if f <= 2:
        return (2, 'alt')
    if f == 3:
        return (3, 'alt')
    if f == 4:
        return (4, 'alt')
    return (5, 'alt')

score_ok = 0
score_tot = 0
per_w = {}
rows = []
for w in (4, 5, 6, 7, 10, 12, 16):
    wok = 0
    wtot = 0
    for t in d['design'][f'w{w}']:
        seq = fams[t['holdout']]
        tc = tuple(t['truth'])
        my = my_answer(seq, w)
        ok = my == tc
        wok += ok
        score_ok += ok
        score_tot += 1
        wtot += 1
        rows.append({"window": w, "trial": t['trial'],
                     "holdout": t['holdout'], "truth": list(tc),
                     "answer": list(my), "correct": ok})
    per_w[w] = f"{wok}/{wtot}"
    print(f"window {w:2d}: {wok}/{wtot} ({wok/wtot:.0%})", flush=True)

print(f"TOTAL: {score_ok}/{score_tot} ({score_ok/score_tot:.1%})")
acc = score_ok/score_tot
from math import comb
pval = sum(comb(score_tot, k)*0.125**k*0.875**(score_tot-k)
           for k in range(score_ok, score_tot+1))
print(f"binomial p (chance 0.125): {pval:.2e}")
verdict = ("CONFIRMED" if acc >= 0.70 else
           "PARTIAL" if acc >= 0.50 else "NEGATIVE")
print(f"P34-c verdict: {verdict}")
json.dump({"rows": rows, "per_window": per_w, "pvalue": pval,
           "verdict": verdict,
           "note": "native blind subject (calling LLM), "
                   "appearance-verified corpus"},
          open('p34c_results.json', 'w'), indent=1)
print("-> p34c_results.json")
