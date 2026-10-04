# -*- coding: utf-8 -*-
"""P265 single-seed worker: function-space geometry dump.
Run: python p265_fn_run.py <seed> <outdir>"""
import os, sys, json, itertools, random
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
torch.set_num_threads(1)

P = 12
SNAPS = [400, 700, 1000, 1300, 2000, 2500]

class Trans(nn.Module):
    def __init__(self, d=128, nhead=4, layers=2):
        super().__init__()
        self.emb = nn.Embedding(P, d)
        self.pos = nn.Embedding(2, d)
        enc = nn.TransformerEncoderLayer(d, nhead, 256, batch_first=True, dropout=0.0)
        self.enc = nn.TransformerEncoder(enc, layers)
        self.out = nn.Linear(d, P)
    def embed(self, ab):
        idx = torch.arange(2).unsqueeze(0).expand(ab.shape[0], -1)
        h = self.emb(ab) + self.pos(idx)
        return self.enc(h)[:, 0]
    def forward(self, ab):
        return self.out(self.embed(ab))

def main():
    seed, outdir = int(sys.argv[1]), sys.argv[2]
    torch.manual_seed(seed)
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a + b) % P for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a + b) % P for a, b in te])
    Xall = torch.tensor(list(itertools.product(range(P), range(P))))
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    logits, embeds = {}, {}
    final = None
    for ep in range(1, 2501):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
        if ep in SNAPS:
            with torch.no_grad():
                logits[ep] = model(Xall).numpy()
                embeds[ep] = model.embed(Xall).numpy()
        if ep % 100 == 0:
            with torch.no_grad():
                final = float((model(Xte).argmax(1) == Yte).float().mean())
    np.savez_compressed(os.path.join(outdir, f"seed_{seed}.npz"),
                        **{f"logits_{ep}": logits[ep] for ep in SNAPS},
                        **{f"emb_{ep}": embeds[ep] for ep in SNAPS})
    json.dump({"seed": seed, "final_test": round(final, 4)},
              open(os.path.join(outdir, f"seed_{seed}.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
