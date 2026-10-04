# -*- coding: utf-8 -*-
"""P254: G6 representation probe — is the mod-3 information in the hidden
representation BEFORE it shows in the output? (P252 excluded the gradient
lever; this asks what the winners have that losers don't, when the outcome
is already decidable.)

12 seeds, matched protocol, checkpoints at ep400 and ep1000: extract the
trunk embedding h0 for all 144 pairs, fit linear probes (3-way mod-3,
4-way mod-4; 60/40 pair split), record probe accuracy + output component
accuracy. Classify seeds by final test (winner >= 0.5).

Pre-stated:
  H-rep : mod-3 PROBE acc at ep1000 predicts final with r > 0.63 AND better
          than output-level mod3 (P247: 0.279) — representation leads output.
  H-early: mod-3 probe at ep400 already predicts (representation forms before
           output divergence; output-level r at 400 was -0.055).
"""
import os, json, itertools, random, time
os.environ["OMP_NUM_THREADS"] = "4"
import torch
import torch.nn as nn
import torch.nn.functional as F
torch.set_num_threads(4)

P = 12
CHECKPOINTS = [400, 1000]
SEEDS = list(range(12))

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

def linear_probe(H, y, iters=300):
    """multinomial logistic probe, 70/30 split; returns eval acc"""
    idx = torch.randperm(len(y))
    ntr = int(len(y) * 0.7)
    tr, te = idx[:ntr], idx[ntr:]
    clf = nn.Linear(H.shape[1], int(y.max()) + 1)
    opt = torch.optim.Adam(clf.parameters(), lr=1e-2)
    with torch.enable_grad():   # probe runs inside the caller's no_grad block
        for _ in range(iters):
            opt.zero_grad()
            F.cross_entropy(clf(H[tr]), y[tr]).backward()
            opt.step()
    with torch.no_grad():
        return float((clf(H[te]).argmax(1) == y[te]).float().mean())

def run(seed):
    torch.manual_seed(seed)
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a + b) % P for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a + b) % P for a, b in te])
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    probes, final = {}, None
    for ep in range(1, 2501):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
        if ep in CHECKPOINTS:
            with torch.no_grad():
                # probe the FULL pair set (representation knowledge, not task train)
                Xall = torch.tensor(list(itertools.product(range(P), range(P))))
                with torch.no_grad():
                    H = model.embed(Xall)
                y3 = torch.tensor([(a + b) % 3 for a, b in Xall.tolist()])
                y4 = torch.tensor([(a + b) % 4 for a, b in Xall.tolist()])
                torch.manual_seed(0)   # probe split fixed across seeds
                p3 = linear_probe(H, y3)
                torch.manual_seed(0)
                p4 = linear_probe(H, y4)
                pred = model(Xte).argmax(1)
                probes[ep] = {"probe_mod3": round(p3, 4),
                              "probe_mod4": round(p4, 4),
                              "out_mod3": float((pred % 3 ==
                                 torch.tensor([(a+b) % 3 for a, b in te])).float().mean()),
                              "test": float((pred == Yte).float().mean())}
        if ep % 100 == 0:
            with torch.no_grad():
                final = float((model(Xte).argmax(1) == Yte).float().mean())
    return {"seed": seed, "probes": probes, "final_test": round(final, 4)}

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
        json.dump(results, open("p254_rep_probe_results.json", "w"), indent=1)
        print(f"[{int(time.time()-t0)}s] seed{s}: final={r['final_test']:.3f} "
              f"p3@400={r['probes'][400]['probe_mod3']:.3f} "
              f"p3@1000={r['probes'][1000]['probe_mod3']:.3f}", flush=True)
    ys = [r["final_test"] for r in results]
    corrs = {}
    for key in ["probe_mod3", "probe_mod4", "out_mod3", "test"]:
        for ep in CHECKPOINTS:
            xs = [r["probes"][ep][key] for r in results]
            corrs[f"{key}@{ep}"] = round(pearson(xs, ys), 3)
    print(json.dumps(corrs, indent=1))
    winners = [r for r in results if r["final_test"] >= 0.5]
    losers = [r for r in results if r["final_test"] < 0.5]
    comp = {
        "n_win": len(winners), "n_lose": len(losers),
        "mod3_probe@1000 winners": round(sum(w["probes"][1000]["probe_mod3"]
                                             for w in winners) / max(1, len(winners)), 3),
        "mod3_probe@1000 losers": round(sum(l["probes"][1000]["probe_mod3"]
                                            for l in losers) / max(1, len(losers)), 3),
    }
    verdict = {"correlations": corrs, "winner_vs_loser": comp,
               "H_rep": bool(corrs["probe_mod3@1000"] > 0.63),
               "H_early": bool(corrs["probe_mod3@400"] > 0.63)}
    json.dump(verdict, open("p254_rep_probe_verdict.json", "w"), indent=1)
    print(json.dumps(verdict, indent=1))
