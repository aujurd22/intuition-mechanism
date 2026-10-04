# -*- coding: utf-8 -*-
"""P264 single-seed worker: trajectory dump + full-task probe.
Run: python p264_traj_run.py <seed> <outdir>"""
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

def linear_probe(H, y):
    idx = torch.randperm(len(y))
    ntr = int(len(y) * 0.7)
    tr, te = idx[:ntr], idx[ntr:]
    clf = nn.Linear(H.shape[1], int(y.max()) + 1)
    opt = torch.optim.Adam(clf.parameters(), lr=1e-2)
    with torch.enable_grad():
        for _ in range(300):
            opt.zero_grad()
            F.cross_entropy(clf(H[tr]), y[tr]).backward()
            opt.step()
    with torch.no_grad():
        return float((clf(H[te]).argmax(1) == y[te]).float().mean())

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
    y12 = torch.tensor([(a + b) % P for a, b in Xall.tolist()])
    y3 = torch.tensor([(a + b) % 3 for a, b in Xall.tolist()])
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    snaps, embeds = {}, {}
    final = None
    for ep in range(1, 2501):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
        if ep in SNAPS:
            with torch.no_grad():
                H = model.embed(Xall)
            torch.manual_seed(0)
            p12 = linear_probe(H, y12)
            torch.manual_seed(0)
            p3 = linear_probe(H, y3)
            embeds[ep] = H.numpy()
            with torch.no_grad():
                test_acc = float((model(Xte).argmax(1) == Yte).float().mean())
            snaps[ep] = {"probe_full12": round(p12, 4), "probe_mod3": round(p3, 4),
                         "test": round(test_acc, 4)}
        if ep % 100 == 0:
            with torch.no_grad():
                final = float((model(Xte).argmax(1) == Yte).float().mean())
    # representation displacement per window (mean L2 over 144 embeddings,
    # normalized per epoch)
    disp = {}
    for a, b in zip(SNAPS[:-1], SNAPS[1:]):
        d = float(np.linalg.norm(embeds[b] - embeds[a], axis=1).mean())
        disp[f"{a}_{b}"] = round(d / (b - a), 5)
    np.savez_compressed(os.path.join(outdir, f"seed_{seed}.npz"),
                        **{f"emb_{ep}": embeds[ep] for ep in SNAPS})
    json.dump({"seed": seed, "snaps": snaps, "disp": disp,
               "final_test": round(final, 4)},
              open(os.path.join(outdir, f"seed_{seed}.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
