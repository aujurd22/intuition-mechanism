"""P221-b: P219's registered prediction test — mod-3-only vs mod-4-only grokking.
P219 found: on (a+b) mod 12, the mod-4 component is learned (real chars) and
mod-3 is not (complex chars). Prediction: a mod-4-only task groks faster/
better than a mod-3-only task."""
import os, json
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
        return self.out(self.enc(h)[:, 0])

def run(component, seed, epochs=2500, wd=5.0):
    import itertools, random
    torch.manual_seed(seed)
    comp = {3: 3, 4: 4}[component]
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a + b) % comp for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a + b) % comp for a, b in te])
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=wd)
    curve = []
    for ep in range(1, epochs + 1):
        opt.zero_grad(); F.cross_entropy(model(Xtr), Ytr).backward(); opt.step()
        if ep % 100 == 0:
            with torch.no_grad():
                curve.append({"epoch": ep,
                              "train": float((model(Xtr).argmax(1) == Ytr).float().mean()),
                              "test": float((model(Xte).argmax(1) == Yte).float().mean())})
    final = curve[-1]
    # grok epoch: test >= 0.9 first time AFTER train >= 0.99
    tr100 = next((c["epoch"] for c in curve if c["train"] >= 0.99), None)
    te90 = next((c["epoch"] for c in curve if c["test"] >= 0.9), None)
    return {"final_test": final["test"], "final_train": final["train"],
            "tr99_epoch": tr100, "te90_epoch": te90, "curve": curve}

def main():
    out = {}
    for comp in [4, 3]:
        runs = [run(comp, s) for s in (0, 1)]
        fin = [r["final_test"] for r in runs]
        out[f"mod{comp}"] = {"final_test": fin, "mean": sum(fin)/len(fin)}
        print(f"mod-{comp}-only: final test = {[round(f,3) for f in fin]}")
    d4, d3 = out["mod4"]["mean"], out["mod3"]["mean"]
    print(f"\nP219 prediction check: mod-4 groks better than mod-3? "
          f"{d4:.3f} vs {d3:.3f} -> {'CONFIRMED' if d4 > d3 + 0.1 else 'NOT CONFIRMED'}")
    json.dump(out, open("p221b_mod3_vs_mod4.json", "w"), indent=1)
    print("saved p221b_mod3_vs_mod4.json")

import json
if __name__ == "__main__":
    main()
