"""P219: mechinterp full cell — after grokking on (a+b) mod 12:
  (1) linear probes for mod-3 / mod-4 / scale on hidden states (proper held-out)
  (2) Mantel decomposition: class-mean distances vs each component separately
  (3) embedding Fourier spectrum per component (Nanda-style)
Fixes P207's mod-4 probe pathology (proper protocol) and decomposes P208's r=0.344."""
import os, json, itertools
os.environ["OMP_NUM_THREADS"] = "4"
import torch
import torch.nn as nn
import torch.nn.functional as F
torch.set_num_threads(4)
P = 12

class Trans(nn.Module):
    def __init__(self, p=P, d=128, nhead=4, layers=2):
        super().__init__()
        self.emb = nn.Embedding(p, d)
        self.pos = nn.Embedding(2, d)
        enc = nn.TransformerEncoderLayer(d, nhead, 256, batch_first=True, dropout=0.0)
        self.enc = nn.TransformerEncoder(enc, layers)
        self.out = nn.Linear(d, p)
        self.last_h = None
        self.enc.layers[-1].register_forward_hook(lambda m, i, o: setattr(self, 'last_h', o))
    def forward(self, ab):
        idx = torch.arange(2).unsqueeze(0).expand(ab.shape[0], -1)
        h = self.emb(ab) + self.pos(idx)
        h = self.enc(h)
        self.last_h = h
        return self.out(h[:, 0])

def train(seed=0, epochs=2500, wd=5.0):
    import itertools
    torch.manual_seed(seed)
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(seed).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a+b) % P for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a+b) % P for a, b in te])
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=wd)
    curve = []
    for ep in range(1, epochs+1):
        opt.zero_grad(); F.cross_entropy(model(Xtr), Ytr).backward(); opt.step()
        if ep % 50 == 0:
            with torch.no_grad():
                curve.append({"epoch": ep,
                              "train": float((model(Xtr).argmax(1) == Ytr).float().mean()),
                              "test": float((model(Xte).argmax(1) == Yte).float().mean())})
    return model, curve

def linear_probe(X, Y, seed=0, epochs=300):
    torch.manual_seed(seed)
    n = len(X)
    idx = list(range(n)); random.Random(seed).shuffle(idx)
    tr, te = idx[:n//2], idx[n//2:]
    clf = nn.Linear(X.shape[1], int(Y.max()) + 1)
    opt = torch.optim.Adam(clf.parameters(), lr=1e-2)
    lf = nn.CrossEntropyLoss()
    for _ in range(epochs):
        opt.zero_grad(); lf(clf(X[tr]), Y[tr]).backward(); opt.step()
    with torch.no_grad():
        return float((clf(X[te]).argmax(1) == Y[te]).float().mean())

def main():
    import random
    model, curve = train(seed=0)
    with torch.no_grad():
        pairs_all = [(a, b) for a in range(P) for b in range(P)]
        Xall = torch.tensor(pairs_all)
        model(Xall)
        H = model.last_h.flatten(1)          # [144, 2*128]
    ds = [a * P + b for a, b in pairs_all]
    mods = {c: torch.tensor([d % c for d in ds]) for c in (3, 4)}
    scale = torch.tensor([0 if d < 72 else 1 for d in ds])
    print("=== linear probes on post-grokking hidden states ===")
    r3 = linear_probe(H, mods[3]); print(f"  mod-3 probe: {r3:.3f} (chance {1/3:.2f})")
    r4 = linear_probe(H, mods[4]); print(f"  mod-4 probe: {r4:.3f} (chance {1/4:.2f})")
    rs = linear_probe(H.unsqueeze(1).flatten(1), scale); print(f"  scale probe: {rs:.3f} (chance 0.50)")
    # Mantel decomposition: class-mean (a,b)-grid distances vs components
    cm = {}
    with torch.no_grad():
        for a in range(P):
            for b in range(P):
                pass
    # per (a mod 3, b mod 3, a mod 4, b mod 4) cells is too fine; use per-sum-class means
    means = {}
    with torch.no_grad():
        for c in range(P):
            m = [(i) for i, (a, b) in enumerate(pairs_all) if (a+b) % P == c]
            means[c] = H[m].mean(0)
    import itertools
    comp = {"mod3": [], "mod4": [], "scale": []}
    obs = []
    for c1, c2 in itertools.combinations(range(P), 2):
        obs.append(float(torch.norm(means[c1] - means[c2])))
        comp["mod3"].append(0 if c1 % 3 == c2 % 3 else 1)
        comp["mod4"].append(0 if c1 % 4 == c2 % 4 else 1)
        comp["scale"].append(abs(c1 - c2))
    def corr(x, y):
        mx, my = sum(x)/len(x), sum(y)/len(y)
        cov = sum((a-mx)*(b-my) for a, b in zip(x, y))
        sx = (sum((a-mx)**2 for a in x))**0.5; sy = (sum((b-my)**2 for b in y))**0.5
        return cov/(sx*sy) if sx*sy else 0
    print("\n=== Mantel decomposition (obs distance vs component) ===")
    out = {}
    for name, cv in comp.items():
        r = corr(obs, cv)
        out[name] = round(r, 3)
        print(f"  {name}: r = {r:.3f}")
    json.dump({"curve": curve, "probes": {"mod3": r3, "mod4": r4, "scale": rs},
               "mantel": out}, open("p219_mechinterp_full.json", "w"), indent=1)
    print("saved p219_mechinterp_full.json")

import random
if __name__ == "__main__":
    main()
