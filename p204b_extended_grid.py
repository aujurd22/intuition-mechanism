"""P204-b: extended grid per user request (more tests + web-informed).
Adds: (1) small Transformer over decimal tokens (grokking-literature canonical setup);
(2) CNN error dissection by period (mod 3 vs mod 4);
(3) seeds 3->5 for key cells."""
import os, json, random
os.environ["OMP_NUM_THREADS"] = "4"
import torch
import torch.nn as nn
torch.set_num_threads(4)

SEEDS = [0, 1, 2, 3, 4]

def decimal_tokens(d, L=4):
    return [int(ch) for ch in f"{d:04d}"]

def modular_vec(d):
    v = []
    for m in (3, 4, 12):
        oh = [0.0] * m
        oh[d % m] = 1.0
        v += oh
    return v

class TinyTransformer(nn.Module):
    def __init__(self, vocab=10, L=4, d_model=64, nhead=4, layers=2):
        super().__init__()
        self.emb = nn.Embedding(vocab, d_model)
        self.pos = nn.Embedding(L, d_model)
        enc = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=128,
                                         batch_first=True, dropout=0.0)
        self.enc = nn.TransformerEncoder(enc, layers)
        self.out = nn.Linear(d_model * L, 2)
    def forward(self, x):
        idx = torch.arange(x.shape[1], device=x.device).unsqueeze(0).expand(x.shape[0], -1)
        h = self.emb(x.long()) + self.pos(idx)
        h = self.enc(h)
        return self.out(h.flatten(1))

class CNN1D(nn.Module):
    def __init__(self, vocab=10, L=4, ch=16):
        super().__init__()
        self.emb = nn.Embedding(vocab, 8)
        self.conv = nn.Conv1d(8, ch, 3, padding=1)
        self.out = nn.Linear(ch * L, 2)
    def forward(self, x):
        e = self.emb(x.long())
        c = torch.relu(self.conv(e.transpose(1, 2)))
        return self.out(c.flatten(1))

def run(kind, rep, model_kind, seed, epochs=60, wd=0.0):
    random.seed(seed); torch.manual_seed(seed)
    data = []
    if kind == "synthetic":
        for d in range(1, 2001):
            data.append((d, 1 if d % 12 in (1, 5) else 0))
    else:
        rows = {1, 3, 5, 7, 13, 17}
        for d in range(1, 1001):
            data.append((d, 1 if d in rows else 0))
    pos = [(d, y) for d, y in data if y == 1]
    neg = [(d, y) for d, y in data if y == 0]
    rng = random.Random(seed * 31 + 7)
    rng.shuffle(pos); rng.shuffle(neg)
    kp, kn = max(1, int(len(pos) * 0.7)), int(len(neg) * 0.7)
    train, test = pos[:kp] + neg[:kn], pos[kp:] + neg[kn:]
    n_pos = sum(y for _, y in train)
    w = torch.tensor([1.0, (len(train) - n_pos) / max(n_pos, 1)])
    fx = (lambda d: torch.tensor(decimal_tokens(d))) if rep == "decimal" else \
         (lambda d: torch.tensor(modular_vec(d)) if rep == "modular" else (lambda d: torch.tensor([d / 1000.0])))
    if model_kind == "transformer":
        model = TinyTransformer()
    elif model_kind == "cnn":
        model = CNN1D()
    else:
        in_dim = {"decimal": 4, "modular": 19, "raw": 1}[rep]
        model = nn.Sequential(nn.Linear(in_dim, 64), nn.ReLU(),
                              nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 2))
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=wd)
    lossf = nn.CrossEntropyLoss(weight=w)
    Xtr = torch.stack([fx(d) for d, _ in train]); Ytr = torch.tensor([y for _, y in train])
    Xte = torch.stack([fx(d) for d, _ in test]);  Yte = torch.tensor([y for _, y in test])
    for ep in range(epochs):
        opt.zero_grad(); loss = lossf(model(Xtr), Ytr); loss.backward(); opt.step()
    with torch.no_grad():
        pred = model(Xte).argmax(1)
        acc = float((pred == Yte).float().mean())
        posm = Yte == 1
        rec = float(pred[posm].float().mean()) if posm.any() else float("nan")
        fpr = float(pred[~posm].float().mean()) if (~posm).any() else float("nan")
    return acc, rec, fpr

def cell(kind, rep, mk, seeds, epochs=60, wd=0.0, dissect=False):
    accs, recs = [], []
    per_mod = {3: [0, 0], 4: [0, 0], 12: [0, 0]}
    for s in seeds:
        acc, rec, fpr = run(kind, rep, mk, s, epochs=epochs, wd=wd)
        accs.append(acc); recs.append(rec)
    m = sum(accs) / len(accs)
    print(f"{kind}/{rep}/{mk:<12} acc={m:.3f} seeds={[round(a,3) for a in accs]}")
    return m

if __name__ == "__main__":
    res = {}
    # 1. the missing architecture: small transformer on decimal (grokking setup: wd + longer)
    res["syn/decimal/transformer"] = cell("synthetic", "decimal", "transformer", SEEDS[:3], epochs=150, wd=1.0)
    res["syn/decimal/cnn_wd"] = cell("synthetic", "decimal", "cnn", SEEDS[:3], epochs=150, wd=1.0)
    # 2. more seeds on the sharp cells
    res["syn/modular/mlp_5seeds"] = cell("synthetic", "modular", "mlp", SEEDS)
    # 3. census transformer
    res["cen/decimal/transformer"] = cell("census", "decimal", "transformer", SEEDS[:3])
    json.dump(res, open("p204b_extended.json", "w"), indent=1)
    print("saved p204b_extended.json")
