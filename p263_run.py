# -*- coding: utf-8 -*-
"""P263 single-seed worker: G6 window-lever test (review round-9, second move).

P254/P258 located the winner/loser difference at representation->output
consolidation during ep1000-2500. This run INTERVENES in that window:
  control      : standard 2500 ep
  readout_only : ep 1000-2000 zero the trunk gradients (only the readout
                 head trains) — direct causal test: if winners = readout
                 wiring and the representation is already there (P254:
                 both groups hold mod-3 information), forced readout-only
                 training should convert losers into winners
  reweight     : ep 1000-2000 reweight CE to equalize mod-3 classes
                 (replay-composition analogue; full-batch GD makes pure
                 data-ORDER interventions no-ops, so the review's "data
                 order" arm is realized as composition reweighting)
Run: python p263_run.py <arm> <seed> <outfile>
"""
import os, sys, json, itertools, random
os.environ["OMP_NUM_THREADS"] = "1"
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
    arm, seed, out_path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    torch.manual_seed(seed)
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a + b) % P for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a + b) % P for a, b in te])
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    out_ids = {id(p_) for p_ in model.out.parameters()}
    counts = torch.bincount(Ytr % 3, minlength=3).float()
    w3 = (counts.sum() / (3 * counts)).clamp(max=5.0)
    final = None
    for ep in range(1, 2501):
        opt.zero_grad()
        logits = model(Xtr)
        if arm == "reweight" and 1000 <= ep <= 2000:
            per = F.cross_entropy(logits, Ytr, reduction="none")
            w = w3[Ytr % 3]
            loss = (per * w / w.sum() * len(w)).sum()
        else:
            loss = F.cross_entropy(logits, Ytr)
        loss.backward()
        if arm == "readout_only" and 1000 <= ep <= 2000:
            for p_ in model.parameters():
                if id(p_) not in out_ids and p_.grad is not None:
                    p_.grad = None   # trunk receives no update in-window
        opt.step()
        if ep % 100 == 0:
            with torch.no_grad():
                final = float((model(Xte).argmax(1) == Yte).float().mean())
    json.dump({"arm": arm, "seed": seed, "final_test": round(final, 4)},
              open(out_path, "w"), indent=1)

if __name__ == "__main__":
    main()
