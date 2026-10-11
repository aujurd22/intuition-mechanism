# -*- coding: utf-8 -*-
"""P269: fine-grid curvature retraining (round-11 attractor hypothesis).
50 checkpoints x 10 seeds on LOCAL GPU (RTX 4070 SUPER, ~2GB VRAM/seed).
Curvature = angle between consecutive embedding displacement vectors
(fine grid makes this a real second-order measure, unlike P268's 6-point).
Also: per-checkpoint output-accuracy trajectory at full resolution.
Run: python p269_curvature_grid.py [seeds=10]
"""
import os, sys, json, itertools, random
os.environ["OMP_NUM_THREADS"] = "2"
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
torch.set_num_threads(2)
dev = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", dev, flush=True)

P = 12
CKPT = list(range(100, 2501, 50))   # 50 checkpoints

class Trans(nn.Module):
    def __init__(self, d=128, nhead=4, layers=2):
        super().__init__()
        self.emb = nn.Embedding(P, d)
        self.pos = nn.Embedding(2, d)
        enc = nn.TransformerEncoderLayer(d, nhead, 256, batch_first=True, dropout=0.0)
        self.enc = nn.TransformerEncoder(enc, layers)
        self.out = nn.Linear(d, P)
    def embed(self, ab):
        idx = torch.arange(2, device=ab.device).unsqueeze(0).expand(ab.shape[0], -1)
        h = self.emb(ab) + self.pos(idx)
        return self.enc(h)[:, 0]
    def forward(self, ab):
        return self.out(self.embed(ab))

def angle(d1, d2):
    c = float(d1 @ d2 / ((np.linalg.norm(d1) * np.linalg.norm(d2)) + 1e-9))
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))

def run(seed):
    torch.manual_seed(seed)
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr).to(dev); Ytr = torch.tensor([(a+b) % P for a, b in tr]).to(dev)
    Xte = torch.tensor(te).to(dev); Yte = torch.tensor([(a+b) % P for a, b in te]).to(dev)
    model = Trans().to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    embs, tests = {}, {}
    ckset = set(CKPT)
    for ep in range(1, 2501):
        opt.zero_grad()
        F.cross_entropy(model(Xtr), Ytr).backward()
        opt.step()
        if ep in ckset:
            with torch.no_grad():
                embs[ep] = model.embed(Xtr[:64]).cpu().numpy()  # fixed 64 rows
                tests[ep] = float((model(Xte).argmax(1) == Yte).float().mean())
        if ep % 500 == 0:
            print(f"  seed{seed} ep{ep} test={tests[ep]:.3f}", flush=True)
    # curvature between consecutive 50-ep displacements
    curv = {}
    for i in range(len(CKPT) - 1):
        d1 = (embs[CKPT[i+1]] - embs[CKPT[i]]).flatten()
        d2 = (embs[CKPT[i+2]] - embs[CKPT[i+1]]).flatten() if i+2 < len(CKPT) else None
        if d2 is not None:
            curv[f"{CKPT[i]}_{CKPT[i+1]}_{CKPT[i+2]}"] = round(angle(d1, d2), 2)
    return {"seed": seed, "final_test": round(tests[2500], 4),
            "test_traj": {str(k): round(v, 4) for k, v in tests.items()},
            "curvature": curv}

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else n
    outdir = os.path.dirname(os.path.abspath(__file__))
    results = []
    existing = []
    if os.path.exists("p269_curvature_results.json"):
        existing = json.load(open("p269_curvature_results.json", encoding="utf-8"))
        existing = [r for r in existing if existing and lo <= r["seed"] < lo + n] if False else existing
    for s in range(lo, hi):
        r = run(s)
        results.append(r)
        disk_f = "p269_curvature_results.json"
        disk = json.load(open(disk_f, encoding="utf-8"))             if os.path.exists(disk_f) else []
        md = {r["seed"]: r for r in disk}
        md[r["seed"]] = r
        json.dump(list(md.values()), open(disk_f, "w", encoding="utf-8"), indent=1)
        trj = r["test_traj"]
        late = [v for k, v in trj.items() if 1000 <= int(k) <= 2500]
        print(f"seed{s}: final={r['final_test']:.3f} late_min={min(late):.3f}", flush=True)
    allr = json.load(open("p269_curvature_results.json", encoding="utf-8"))
    seen_seeds = {r["seed"]: r for r in allr}
    rows = list(seen_seeds.values())
    wins = [r for r in rows if r["final_test"] >= 0.5]
    lose = [r for r in rows if r["final_test"] < 0.5]
    print(f"total seeds on disk: {len(rows)} (win {len(wins)} / lose {len(lose)})")
    cmp_ = {}
    all_keys = sorted(results[0]["curvature"].keys())
    for k in all_keys:
        cmp_[k] = {"win": round(float(np.mean([r["curvature"][k] for r in wins])) if wins else 0, 2),
                   "lose": round(float(np.mean([r["curvature"][k] for r in lose])) if lose else 0, 2)}
    verdict = {"n": len(rows), "n_win": len(wins),
               "curvature_win_vs_lose": cmp_,
               "note": "fine grid (50 ep) — angles now measure true directional persistence"}
    json.dump(verdict, open("p269_curvature_verdict.json", "w"), indent=1)
    print(json.dumps(cmp_, indent=1))
