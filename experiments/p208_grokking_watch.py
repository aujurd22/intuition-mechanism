"""P208: grokking watch — TinyTransformer on the synthetic modular rule,
weight-decay + long training (grokking literature setup), monitoring:
  (1) delayed-generalization phase transition (test acc vs epoch)
  (2) after transition: do representations align by genus components?
      class-mean distance structure vs (mod3, mod4) prediction (Mantel)."""
import os, json, random
os.environ["OMP_NUM_THREADS"] = "4"
import torch
import torch.nn as nn
torch.set_num_threads(4)

def decimal_tokens(d, L=4):
    return [int(ch) for ch in f"{d:04d}"]

class TinyTransformer(nn.Module):
    def __init__(self, vocab=10, L=4, d_model=64, nhead=4, layers=2):
        super().__init__()
        self.emb = nn.Embedding(vocab, d_model)
        self.pos = nn.Embedding(L, d_model)
        enc = nn.TransformerEncoderLayer(d_model, nhead, 128, batch_first=True, dropout=0.0)
        self.enc = nn.TransformerEncoder(enc, layers)
        self.out = nn.Linear(d_model * L, 2)
        self.last_h = None
        self.enc.layers[-1].register_forward_hook(
            lambda m, i, o: setattr(self, 'last_h', o))
    def forward(self, x):
        idx = torch.arange(x.shape[1]).unsqueeze(0).expand(x.shape[0], -1)
        h = self.emb(x.long()) + self.pos(idx)
        h = self.enc(h)
        self.last_h = h
        return self.out(h.flatten(1))

def main():
    random.seed(0); torch.manual_seed(0)
    data = [(d, 1 if d % 12 in (1, 5) else 0) for d in range(1, 2001)]
    train = [x for x in data if x[0] <= 1200]
    test = [x for x in data if x[0] > 1200]
    n_pos = sum(y for _, y in train)
    w = torch.tensor([1.0, (len(train) - n_pos) / n_pos])
    fx = lambda d: torch.tensor(decimal_tokens(d))
    Xtr = torch.stack([fx(d) for d, _ in train]); Ytr = torch.tensor([y for _, y in train])
    Xte = torch.stack([fx(d) for d, _ in test]);  Yte = torch.tensor([y for _, y in test])
    model = TinyTransformer()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=2.0)
    lossf = nn.CrossEntropyLoss(weight=w)
    curve = []
    EPOCHS = 2000
    for ep in range(1, EPOCHS + 1):
        opt.zero_grad()
        lossf(model(Xtr), Ytr).backward(); opt.step()
        if ep % 50 == 0 or ep in (1, 10, 20, 50, 100):
            with torch.no_grad():
                acc = float((model(Xte).argmax(1) == Yte).float().mean())
            curve.append({"epoch": ep, "test_acc": acc})
            if ep % 200 == 0 or ep in (10, 50, 100, 200, 400, 600, 800, 1000):
                print(f"epoch {ep:>5}: test acc = {acc:.3f}")
    json.dump(curve, open("p208_grokking_curve.json", "w"))
    with torch.no_grad():
        acc = float((model(Xte).argmax(1) == Yte).float().mean())
    print(f"final test acc = {acc:.4f}")

    # (2) class-mean distance structure analysis
    model(Xtr[:2])  # trigger hook
    means = {}
    with torch.no_grad():
        for c in range(12):
            ds = [d for d, _ in train if d % 12 == c][:60]
            Xc = torch.stack([fx(d) for d in ds])
            model(Xc)
            means[c] = model.last_h.flatten(1).mean(0)
    def dist(a, b):
        return float(torch.norm(a - b))
    import itertools
    D_obs, D_pred = [], []
    for (c1, m1), (c2, m2) in itertools.combinations(means.items(), 2):
        D_obs.append(dist(m1, m2))
        # predicted: different mod 3 AND different mod 4 => far; same components => near
        d3 = 0 if c1 % 3 == c2 % 3 else 1
        d4 = 0 if c1 % 4 == c2 % 4 else 1
        D_pred.append(d3 + d4)
    n = len(D_obs)
    mo = sum(D_obs) / n; mp_ = sum(D_pred) / n
    cov = sum((o - mo) * (p - mp_) for o, p in zip(D_obs, D_pred))
    so = (sum((o - mo) ** 2 for o in D_obs)) ** 0.5
    sp = (sum((p - mp_) ** 2 for p in D_pred)) ** 0.5
    r = cov / (so * sp) if so * sp else 0
    print(f"\nclass-mean distance vs (mod3,mod4) separation: r = {r:.3f}  (n={n} pairs)")
    json.dump({"final_acc": acc, "mantel_r": r,
               "curve": curve}, open("p208_grokking_watch.json", "w"), indent=1)
    print("saved p208_grokking_watch.json")

if __name__ == "__main__":
    main()
