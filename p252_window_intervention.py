# -*- coding: utf-8 -*-
"""P252: G6 in-window intervention (P247's follow-up — what pushes seeds apart?).

P247 located the bifurcation window (ep 400-1000). If mod-3 representation
formation is the event, then TRANSIENT scaffolding inside the window should
help where permanent scaffolding from step 0 hurt (P237: 0.183 vs control
0.290). Arms (matched P237 protocol, 10 seeds):

  control      : CE only, 2500 ep
  step0_aux    : CE + mod-3 aux from step 0 (replicates P237's harmful arm)
  window_aux   : CE + mod-3 aux ONLY during ep 700-1000, then removed
  early_aux    : CE + mod-3 aux ONLY during ep 100-400 (before the window)

Pre-stated readings:
  H-window : window_aux mean > control + 0.15 AND > step0_aux
             -> the 400-1000 window is causally the mod-3 formation window
  H-null   : window_aux ~ control -> the window is real (P247) but gradient
             scaffolding is not the lever; formation is spontaneous
Runtime ~30 min CPU (30 runs x 2500-2800 ep).
"""
import os, json, itertools, random, time
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
        self.aux = nn.Linear(d, 3)
    def forward(self, ab):
        idx = torch.arange(2).unsqueeze(0).expand(ab.shape[0], -1)
        h = self.emb(ab) + self.pos(idx)
        h = self.enc(h)
        h0 = h[:, 0]
        return self.out(h0), self.aux(h0)

def make_split(seed):
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a + b) % P for a, b in tr])
    Ytr3 = torch.tensor([(a + b) % 3 for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a + b) % P for a, b in te])
    return Xtr, Ytr, Ytr3, Xte, Yte

def run(arm, seed, epochs=2500):
    torch.manual_seed(seed)
    Xtr, Ytr, Ytr3, Xte, Yte = make_split(seed)
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    final = None
    for ep in range(1, epochs + 1):
        opt.zero_grad()
        logits, aux_logits = model(Xtr)
        loss = F.cross_entropy(logits, Ytr)
        if arm == "step0_aux":
            loss = loss + F.cross_entropy(aux_logits, Ytr3)
        elif arm == "window_aux" and 700 <= ep <= 1000:
            loss = loss + F.cross_entropy(aux_logits, Ytr3)
        elif arm == "early_aux" and 100 <= ep <= 400:
            loss = loss + F.cross_entropy(aux_logits, Ytr3)
        loss.backward()
        opt.step()
        if ep % 100 == 0:
            with torch.no_grad():
                final = float((model(Xte)[0].argmax(1) == Yte).float().mean())
    return {"arm": arm, "seed": seed, "final_test": round(final, 4)}

ARMS = ["control", "step0_aux", "window_aux", "early_aux"]

if __name__ == "__main__":
    t0 = time.time()
    results = []
    for arm in ARMS:
        for seed in range(10):
            r = run(arm, seed)
            results.append(r)
            json.dump(results, open("p252_window_intervention_results.json", "w"),
                      indent=1)
            print(f"[{int(time.time()-t0)}s] {arm} seed{seed}: "
                  f"{r['final_test']:.3f}", flush=True)
    summary = {}
    for arm in ARMS:
        accs = [r["final_test"] for r in results if r["arm"] == arm]
        mean = sum(accs) / len(accs)
        var = sum((a - mean) ** 2 for a in accs) / (len(accs) - 1)
        summary[arm] = {"mean": round(mean, 4), "std": round(var ** 0.5, 4),
                        "gen_ratio": round(sum(a >= 0.5 for a in accs) / len(accs), 2)}
        print(f"{arm}: {mean:.3f} +/- {var**0.5:.3f}  "
              f"gen>=0.5: {sum(a >= 0.5 for a in accs)}/10")
    wa = summary["window_aux"]["mean"]
    ctl = summary["control"]["mean"]
    verdict = {
        "summary": summary,
        "h_window": ("CONFIRMED" if wa > ctl + 0.15 and
                     wa > summary["step0_aux"]["mean"] + 0.15 else "NOT CONFIRMED"),
    }
    json.dump(verdict, open("p252_window_intervention_verdict.json", "w"), indent=1)
    print(json.dumps(verdict, indent=1))
