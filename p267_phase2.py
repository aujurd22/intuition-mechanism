# -*- coding: utf-8 -*-
"""P267 phase 2: resume from the ep1000 checkpoint, apply the arm's window
policy (ep1000-2000), standard to 2500. Re-measures train-alignment over the
window's last 100 epochs (mediation check).
Run: python p267_phase2.py <arm> <seed> <median> <dir>
Arms: control | all_lrdrop | screen_lrdrop (drop iff screen_align < median)
"""
import os, sys, json, itertools, random
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
torch.set_num_threads(1)

P = 12
DROP_LR = 2e-4   # lr / 5
BASE_LR = 1e-3

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

def train_align(model, Xtr, Ytr, opt, n=100):
    with torch.no_grad():
        f0 = model(Xtr).numpy()
    for _ in range(n):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
    with torch.no_grad():
        f1 = model(Xtr).numpy()
    df = (f1 - f0).flatten()
    e = np.exp(f0 - f0.max(axis=1, keepdims=True))
    sm = e / e.sum(axis=1, keepdims=True)
    yoh = np.zeros_like(sm)
    yoh[np.arange(len(Ytr)), Ytr.numpy()] = 1.0
    needed = (yoh - sm).flatten()
    return float(df @ needed / ((np.linalg.norm(df) * np.linalg.norm(needed)) + 1e-9))

def main():
    arm, seed, median, d = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    torch.manual_seed(seed + 10000)  # distinct stream from phase 1 bookkeeping
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a + b) % P for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a + b) % P for a, b in te])
    ck = torch.load(os.path.join(d, f"ckpt_{seed}.pt"), weights_only=True)
    model = Trans(); model.load_state_dict(ck["model"])
    opt = torch.optim.AdamW(model.parameters(), lr=BASE_LR, weight_decay=5.0)
    opt.load_state_dict(ck["opt"])
    ph1 = json.load(open(os.path.join(d, f"phase1_{seed}.json")))
    screen_align = ph1["screen_align"]
    drop = (arm == "all_lrdrop") or (arm == "screen_lrdrop" and screen_align < median)
    final = post_align = None
    for ep in range(1001, 2501):
        if ep == 1001 and drop:
            for g in opt.param_groups:
                g["lr"] = DROP_LR
        if ep == 2001 and drop:
            for g in opt.param_groups:
                g["lr"] = BASE_LR
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
        if ep == 1900:
            post_align = train_align(model, Xtr, Ytr, opt, n=100)
        if ep % 100 == 0 or ep == 2000:
            with torch.no_grad():
                final = float((model(Xte).argmax(1) == Yte).float().mean())
    json.dump({"arm": arm, "seed": seed, "screen_align": screen_align,
               "dropped": drop, "post_align": round(post_align, 4),
               "final_test": round(final, 4)},
              open(os.path.join(d, f"phase2_{arm}_{seed}.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
