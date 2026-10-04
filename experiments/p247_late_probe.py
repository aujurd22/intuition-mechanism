# -*- coding: utf-8 -*-
"""P247: late-window path-dependency probes (P243's registered refinement).

P243 showed: all seeds memorize by ~ep200, bifurcation is late, early probes
(<=800) have no predictive power. Registered refinement: probe the LATE window.

Seeds: 12 (extension of P243's 10). Probes at ep 1000/1500/2000/2500 (test-set):
  overall test acc, mod-4 component test acc, mod-3 component test acc,
  total weight L2 norm.
Early anchor at ep 400 for continuity with P243.

Pre-stated hypotheses (no sign commitment for norm):
  H-late: final test acc is predictable from ep1000-1500 probes, |r| > 0.63
          (n=12 approximate significance bar)
  H-null: still unpredictable -> outcome decided only at the very end
"""
import os, json, itertools, random, time
os.environ["OMP_NUM_THREADS"] = "4"
import torch
import torch.nn as nn
import torch.nn.functional as F
torch.set_num_threads(4)

P = 12
PROBE_EPOCHS = [400, 1000, 1500, 2000, 2500]
SEEDS = list(range(12))

class Trans(nn.Module):
    def __init__(self, d=128, nhead=4, layers=2):
        super().__init__()
        self.emb = nn.Embedding(P, d)
        self.pos = nn.Embedding(2, d)
        enc = nn.TransformerEncoderLayer(d, nhead, 256, batch_first=True, dropout=0.0)
        self.enc = nn.TransformerEncoder(enc, layers)
        self.out = nn.Linear(d, P)
    def forward(self, ab):
        idx = torch.arange(2).unsqueeze(0).expand(ab.shape[0], -1)
        h = self.emb(ab) + self.pos(idx)
        return self.out(self.enc(h)[:, 0])

def wnorm(model):
    return float(sum((p.detach() ** 2).sum() for p in model.parameters()) ** 0.5)

def run(seed):
    torch.manual_seed(seed)
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a + b) % P for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a + b) % P for a, b in te])
    Yte4 = torch.tensor([(a + b) % 4 for a, b in te])
    Yte3 = torch.tensor([(a + b) % 3 for a, b in te])
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    probes = {}
    for ep in range(1, 2501):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
        if ep in PROBE_EPOCHS:
            with torch.no_grad():
                pred = model(Xte).argmax(1)
                probes[ep] = {
                    "test": float((pred == Yte).float().mean()),
                    "mod4": float((pred % 4 == Yte4).float().mean()),
                    "mod3": float((pred % 3 == Yte3).float().mean()),
                    "wnorm": wnorm(model),
                }
    return {"seed": seed, "probes": probes,
            "final_test": probes[2500]["test"]}

def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
    sy = (sum((y - my) ** 2 for y in ys)) ** 0.5
    if sx == 0 or sy == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)

if __name__ == "__main__":
    t0 = time.time()
    results = []
    for s in SEEDS:
        r = run(s)
        results.append(r)
        json.dump(results, open("p247_late_probe_results.json", "w"), indent=1)
        print(f"[{int(time.time()-t0)}s] seed{s}: final={r['final_test']:.3f} "
              f"ep1000 test={r['probes'][1000]['test']:.3f} "
              f"mod3={r['probes'][1000]['mod3']:.3f} "
              f"wnorm={r['probes'][1000]['wnorm']:.1f}", flush=True)

    ys = [r["final_test"] for r in results]
    corrs = {}
    for key in ["test", "mod4", "mod3", "wnorm"]:
        corrs[key] = {ep: round(pearson([r["probes"][ep][key] for r in results], ys), 3)
                      for ep in PROBE_EPOCHS}
        print(f"{key}: {corrs[key]}")
    late_best = max(abs(v) for key in ["test", "mod4", "mod3", "wnorm"]
                    for ep, v in corrs[key].items() if ep >= 1000)
    verdict = {"correlations": corrs,
               "late_predictable": bool(late_best > 0.63),
               "late_best_abs_r": round(late_best, 3),
               "bar": "n=12 approx significance |r|>0.63"}
    json.dump({"correlations": corrs, "verdict": verdict,
               "finals": ys}, open("p247_late_probe_verdict.json", "w"), indent=1)
    print(json.dumps(verdict, indent=1))
