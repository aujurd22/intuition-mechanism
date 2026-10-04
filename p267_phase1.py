# -*- coding: utf-8 -*-
"""P267 phase 1: train to ep1000, then screen — update-target alignment over
60 epochs computed on TRAIN pairs only (zero test leakage).
Run: python p267_phase1.py <seed> <dir>"""
import os, sys, json, itertools, random
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
torch.set_num_threads(1)

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
        return self.out(self.enc(h)[:, 0])

def main():
    seed, d = int(sys.argv[1]), sys.argv[2]
    torch.manual_seed(seed)
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a + b) % P for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a + b) % P for a, b in te])
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    test1000 = None
    for ep in range(1, 1001):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
        if ep == 1000:
            with torch.no_grad():
                test1000 = float((model(Xte).argmax(1) == Yte).float().mean())
    # ---- screen: alignment of the next 60 epochs' updates, TRAIN pairs only ----
    with torch.no_grad():
        f0 = model(Xtr).numpy()
    for _ in range(60):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
    with torch.no_grad():
        f1 = model(Xtr).numpy()
    df = f1 - f0
    e = np.exp(f0 - f0.max(axis=1, keepdims=True))
    sm = e / e.sum(axis=1, keepdims=True)
    yoh = np.zeros_like(sm)
    yoh[np.arange(len(Ytr)), Ytr.numpy()] = 1.0
    needed = (yoh - sm).flatten()
    dfl = df.flatten()
    screen_align = float(dfl @ needed / ((np.linalg.norm(dfl) * np.linalg.norm(needed)) + 1e-9))
    torch.save({"model": model.state_dict(), "opt": opt.state_dict()},
               os.path.join(d, f"ckpt_{seed}.pt"))
    json.dump({"seed": seed, "screen_align": round(screen_align, 4),
               "test@1000": round(test1000, 4)},
              open(os.path.join(d, f"phase1_{seed}.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
