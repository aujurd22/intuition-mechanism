# -*- coding: utf-8 -*-
"""P258 single-seed worker: train composite mod-12 to 2500 ep; at ep 400/1000
snapshot the READOUT weight (out.weight) and trunk probe; dump one JSON.
Run: python p258_run.py <seed> <outfile>"""
import os, sys, json, itertools, random
os.environ["OMP_NUM_THREADS"] = "1"
import torch
import torch.nn as nn
import torch.nn.functional as F
torch.set_num_threads(1)

P = 12
SNAP = [400, 1000]

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

def wiring_index(W, m):
    """readout alignment with mod-m class structure: W is P x d, rows grouped by
    c % m; return mean pairwise cosine DISTANCE between group centroids
    (higher = the readout separates mod-m classes more strongly)."""
    cents = []
    for j in range(m):
        rows = [c for c in range(P) if c % m == j]
        v = W[rows].mean(0)
        cents.append(v / (v.norm() + 1e-9))
    ds = []
    for i in range(m):
        for j in range(i + 1, m):
            ds.append(float(1 - (cents[i] * cents[j]).sum()))
    return sum(ds) / len(ds)

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
    seed = int(sys.argv[1])
    out_path = sys.argv[2]
    torch.manual_seed(seed)
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a + b) % P for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a + b) % P for a, b in te])
    Xall = torch.tensor(list(itertools.product(range(P), range(P))))
    y3 = torch.tensor([(a + b) % 3 for a, b in Xall.tolist()])
    y4 = torch.tensor([(a + b) % 4 for a, b in Xall.tolist()])
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    snaps, final = {}, None
    for ep in range(1, 2501):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
        if ep in SNAP:
            W = model.out.weight.detach()
            torch.manual_seed(0)
            with torch.no_grad():
                H = model.embed(Xall)
            torch.manual_seed(0)
            p3 = linear_probe(H, y3)
            snaps[ep] = {"wiring3": round(wiring_index(W, 3), 4),
                         "wiring4": round(wiring_index(W, 4), 4),
                         "probe_mod3": round(p3, 4)}
        if ep % 100 == 0:
            with torch.no_grad():
                final = float((model(Xte).argmax(1) == Yte).float().mean())
    json.dump({"seed": seed, "snaps": snaps, "final_test": round(final, 4)},
              open(out_path, "w"), indent=1)

if __name__ == "__main__":
    main()
