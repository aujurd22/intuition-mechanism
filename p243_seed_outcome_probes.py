# -*- coding: utf-8 -*-
"""P243 (gap G6, review round-7 restatement): WHAT DETERMINES THE SEED OUTCOME?

P237 refuted both escape levers AND showed the composite outcome is high-variance
across seeds (0.00-0.59) — the graded-difficulty and stable-local-optimum stories
are both dead. G6 is now a PATH-DEPENDENCY question: what早期 quantity predicts
where a seed lands?

Protocol: matched P219/P237 (composite (a+b) mod 12, 2500 ep, wd 5.0, lr 1e-3,
60/40 split), 10 seeds. Probes at epochs 100/200/400/800:
  overall train acc, mod-4 component acc ((pred%4)==(true%4)),
  mod-3 component acc ((pred%3)==(true%3)).
Outcome: final test acc.

Registered alternative hypotheses (both informative, no sign commitment):
  H1 (lock-in): early mod-4 accuracy NEGATIVELY correlates with final test
      (fast mod-4 lock-in consumes the capacity/gradient -> mod-3 never arrives)
  H2 (health): early overall progress POSITIVELY correlates with final test
      (early speed is generic optimization health, not competition)
Report Pearson r for each probe-outcome pair; n=10.
"""
import os, json, itertools, random
os.environ["OMP_NUM_THREADS"] = "4"
import torch
import torch.nn as nn
import torch.nn.functional as F
torch.set_num_threads(4)

P = 12
PROBE_EPOCHS = {100, 200, 400, 800}
SEEDS = list(range(10))

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

def run(seed):
    torch.manual_seed(seed)
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr);  Ytr = torch.tensor([(a + b) % P for a, b in tr])
    Ytr4 = torch.tensor([(a + b) % 4 for a, b in tr])
    Ytr3 = torch.tensor([(a + b) % 3 for a, b in tr])
    Xte = torch.tensor(te);  Yte = torch.tensor([(a + b) % P for a, b in te])
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    probes, final_test = {}, None
    for ep in range(1, 2501):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
        if ep in PROBE_EPOCHS:
            with torch.no_grad():
                pred = model(Xtr).argmax(1)
                probes[ep] = {
                    "train": float((pred == Ytr).float().mean()),
                    "mod4": float((pred % 4 == Ytr4).float().mean()),
                    "mod3": float((pred % 3 == Ytr3).float().mean()),
                }
        if ep % 100 == 0:
            with torch.no_grad():
                final_test = float((model(Xte).argmax(1) == Yte).float().mean())
    return {"seed": seed, "probes": probes, "final_test": round(final_test, 4)}

def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs)/n, sum(ys)/n
    sx = (sum((x-mx)**2 for x in xs))**0.5
    sy = (sum((y-my)**2 for y in ys))**0.5
    if sx == 0 or sy == 0:
        return 0.0
    return sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / (sx*sy)

if __name__ == "__main__":
    results = []
    for s in SEEDS:
        r = run(s)
        results.append(r)
        json.dump(results, open("p243_seed_outcome_results.json", "w"), indent=1)
        p4 = r["probes"][400]
        print(f"seed{s}: final_test={r['final_test']:.3f}  "
              f"ep400 train={p4['train']:.2f} mod4={p4['mod4']:.2f} mod3={p4['mod3']:.2f}",
              flush=True)

    ys = [r["final_test"] for r in results]
    corrs = {}
    for key, label in [("train", "H2 health"), ("mod4", "H1 lock-in"),
                       ("mod3", "H1 lock-in")]:
        corrs[key] = {}
        for ep in sorted(PROBE_EPOCHS):
            xs = [r["probes"][ep][key] for r in results]
            corrs[key][ep] = round(pearson(xs, ys), 3)
        print(f"{key} vs final_test: {corrs[key]}  ({label})")
    h1 = corrs["mod4"][400]
    verdict = {
        "correlations": corrs,
        "H1_lockin_supported": bool(h1 < -0.5),
        "H2_health_supported": bool(corrs["train"][400] > 0.5),
        "note": "n=10, exploratory correlation (no significance claim); "
                "registered as PROPOSE-level path-dependency probe",
    }
    json.dump({"results_summary": [{k: v for k, v in r.items() if k != "probes"}
                                   for r in results],
               "correlations": corrs, "verdict": verdict},
              open("p243_seed_outcome_verdict.json", "w"), indent=1)
    print(json.dumps(verdict, indent=1))
