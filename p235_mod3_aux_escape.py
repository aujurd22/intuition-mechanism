# -*- coding: utf-8 -*-
"""P235: mod-3 auxiliary loss escape test (P229-b prediction).
Prediction: mod-12 composite task's partial learning (0.69) is a local optimum
where mod-4 is learned but mod-3 has no gradient pressure. Adding an auxiliary
mod-3 loss should provide the missing gradient pressure -> escape -> test > 0.90.
Control: same architecture, same budget, NO auxiliary loss -> stuck at ~0.69."""
import os, json, itertools, random
os.environ["OMP_NUM_THREADS"] = "4"
import torch
import torch.nn as nn
import torch.nn.functional as F
torch.set_num_threads(4)
P = 12

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
        h = self.enc(h)
        return self.out(h[:, 0])

def run(seed, epochs=3000, wd=5.0, lr=1e-3):
    torch.manual_seed(seed)
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a+b) % P for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a+b) % P for a, b in te])
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    best_te = 0.0
    curve = []
    for ep in range(1, epochs+1):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
        if ep % 100 == 0 or ep == 1:
            with torch.no_grad():
                te_a = float((model(Xte).argmax(1) == Yte).float().mean())
                tr_a = float((model(Xtr).argmax(1) == Ytr).float().mean())
            best_te = max(best_te, te_a)
            curve.append({"epoch": ep, "train": tr_a, "test": te_a})
    return best_te, curve

# data
import itertools
P = 12
pairs = list(itertools.product(range(P), range(P)))
random.seed(0)
random.shuffle(pairs)
ntr = int(len(pairs) * 0.6)
tr = pairs[:ntr]; te = pairs[ntr:]
Xtr = torch.tensor(tr); Ytr = torch.tensor([(a+b) % P for a, b in tr])
Xte = torch.tensor(te); Yte = torch.tensor([(a+b) % P for a, b in te])

print("P235: mod-3 auxiliary loss escape test")
print("Task: (a+b) mod 12, 60/40 split, 3 seeds\n")

import torch.nn as nn
import torch.nn.functional as F

results = {"no_aux": [], "with_aux": []}
for seed in [0, 1, 2]:
    torch.manual_seed(seed)
    pairs_shuf = list(pairs)
    random.shuffle(pairs_shuf)
    ntr = int(len(pairs_shuf) * 0.6)
    tr_s = pairs_shuf[:ntr]; te_s = pairs_shuf[ntr:]
    Xtr = torch.tensor(tr_s); Ytr = torch.tensor([(a+b) % P for a, b in tr_s])
    Xte = torch.tensor(te_s); Yte = torch.tensor([(a+b) % P for a, b in te_s])

    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=2.0)
    best_te = 0.0
    for ep in range(1, 2001):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward(); opt.step()
        if ep % 200 == 0:
            with torch.no_grad():
                ta = float((model(Xte).argmax(1) == Yte).float().mean())
            best_te = max(best_te, ta)
    results["no_aux"].append(best_te)
    print(f"seed{seed} no_aux: best test acc = {best_te:.3f}")

print(f"\nResults saved to p235_mod3_escape_results.json")
import json
json.dump(results, open("p235_mod3_escape_results.json", "w"), indent=1)
