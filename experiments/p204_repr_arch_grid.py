"""P204: representation x architecture grid — where does 'discovery' live?
Question (user hypothesis): is discovery hiding in conv nets?
Precisified: discovery lives in the MATCH between equivariance architecture
and the symmetry group of the true rule.
Task A (synthetic, mechanism test): d mod 12 in {1,5} <=> positive, d in [1,2000].
Task B (real, boundary test): census six-row labels, d in [1,1000].
Representations: decimal-4digit tokens / raw scalar / modular one-hot (d mod 12).
Architectures: CNN(1D) / MLP / k-WTA sparse (fly-style: top-k competition + linear readout).
Protocol: 3 seeds each, balanced test accuracy, thread-limited (hardware discipline).
"""
import os, json, random
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
import torch
import torch.nn as nn
torch.set_num_threads(4)

SEEDS = [0, 1, 2]
DEV = "cpu"

# ---------- data ----------
def decimal_tokens(d, L=4):
    s = f"{d:04d}"
    return [int(ch) for ch in s]

def modular_vec(d):
    v = []
    for m in (3, 4, 12):
        oh = [0.0] * m
        oh[d % m] = 1.0
        v += oh
    return v

def build_task(kind):
    """returns list of (d, label, features dict)"""
    data = []
    if kind == "synthetic":
        for d in range(1, 2001):
            y = 1 if d % 12 in (1, 5) else 0
            data.append((d, y))
    else:  # census: six rows positive
        rows = {1, 3, 5, 7, 13, 17}
        for d in range(1, 1001):
            y = 1 if d in rows else 0
            data.append((d, y))
    return data

def featurize(d, rep):
    if rep == "decimal":
        return torch.tensor(decimal_tokens(d), dtype=torch.float32)
    if rep == "raw":
        return torch.tensor([d / 1000.0], dtype=torch.float32)
    if rep == "modular":
        return torch.tensor(modular_vec(d), dtype=torch.float32)

# ---------- models ----------
class CNN1D(nn.Module):
    def __init__(self, in_dim_seq=4, vocab=10, ch=16):
        super().__init__()
        self.emb = nn.Embedding(vocab, 8)
        self.conv = nn.Conv1d(8, ch, kernel_size=3, padding=1)
        self.out = nn.Linear(ch * in_dim_seq, 2)
    def forward(self, x):
        # x: decimal token ints shape [B, 4]
        e = self.emb(x.long())              # [B,4,8]
        c = torch.relu(self.conv(e.transpose(1, 2)))  # [B,ch,4]
        return self.out(c.flatten(1))

class MLP(nn.Module):
    def __init__(self, in_dim, hid=64):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(in_dim, hid), nn.ReLU(),
                                 nn.Linear(hid, hid), nn.ReLU(), nn.Linear(hid, 2))
    def forward(self, x):
        return self.net(x)

class kWTA(nn.Module):
    """fly-style: random frozen projection -> top-k competition -> linear readout"""
    def __init__(self, in_dim, hid=200, k=20):
        super().__init__()
        g = torch.Generator().manual_seed(42)
        self.proj = torch.randn(in_dim, hid, generator=g)  # frozen random
        self.k = k
        self.out = nn.Linear(hid, 2)
    def forward(self, x):
        h = x @ (self.proj.abs() / self.proj.abs().sum(0, keepdim=True))
        topk = torch.topk(h, self.k, dim=1).indices
        mask = torch.zeros_like(h).scatter_(1, topk, 1.0)
        return self.out(h * mask)

def train_eval(model_kind, rep, data, train_dmax, seed, epochs=60, split="dmax"):
    random.seed(seed); torch.manual_seed(seed)
    if split == "dmax":
        train = [(d, y) for d, y in data if d <= train_dmax]
        test  = [(d, y) for d, y in data if d > train_dmax]
    else:  # balanced random split (same-distribution interpolation test)
        pos = [(d, y) for d, y in data if y == 1]
        neg = [(d, y) for d, y in data if y == 0]
        rng = random.Random(seed * 31 + 7)
        rng.shuffle(pos); rng.shuffle(neg)
        k_pos = max(1, int(len(pos) * 0.7)); k_neg = int(len(neg) * 0.7)
        train = pos[:k_pos] + neg[:k_neg]
        test  = pos[k_pos:] + neg[k_neg:]
    # class-balanced training via weighted loss
    n_pos = sum(y for _, y in train); n_neg = len(train) - n_pos
    w = torch.tensor([1.0, n_neg / max(n_pos, 1)])
    in_dim = {"decimal": 4, "raw": 1, "modular": 19}[rep]
    if model_kind == "cnn":
        assert rep == "decimal"
        model = CNN1D()
        fx = lambda d: torch.tensor(decimal_tokens(d))
    else:
        model = {"mlp": lambda: MLP(in_dim), "kwta": lambda: kWTA(in_dim)}[model_kind]()
        fx = lambda d: featurize(d, rep)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    lossf = nn.CrossEntropyLoss(weight=w)
    Xtr = torch.stack([fx(d) for d, _ in train])
    Ytr = torch.tensor([y for _, y in train])
    for ep in range(epochs):
        opt.zero_grad()
        loss = lossf(model(Xtr), Ytr)
        loss.backward(); opt.step()
    with torch.no_grad():
        Xte = torch.stack([fx(d) for d, _ in test])
        Yte = torch.tensor([y for _, y in test])
        pred = model(Xte).argmax(1)
        acc_all = float((pred == Yte).float().mean())
        pos_idx = Yte == 1
        recall_pos = float(pred[pos_idx].float().mean()) if pos_idx.any() else float("nan")
        pred_neg = pred[~pos_idx]
        fpr = float(pred_neg.float().mean()) if len(pred_neg) else float("nan")
        bal = (recall_pos + (1 - fpr)) / 2
    return {"bal_acc": bal, "recall_pos": recall_pos, "fpr": fpr, "acc": acc_all,
            "n_test": len(test), "n_test_pos": int(pos_idx.sum())}

def main():
    results = {}
    for task in ["synthetic", "census"]:
        data = build_task(task)
        tmax = 1200 if task == "synthetic" else 700
        split = "dmax" if task == "synthetic" else "random"
        for rep in ["decimal", "raw", "modular"]:
            for arch in ["cnn", "mlp", "kwta"]:
                if arch == "cnn" and rep != "decimal":
                    continue
                key = f"{task}/{rep}/{arch}"
                runs = [train_eval(arch, rep, data, tmax, s, split=split) for s in SEEDS]
                bal = [r["bal_acc"] for r in runs]
                results[key] = {
                    "bal_acc_mean": sum(bal) / len(bal),
                    "bal_acc_seeds": bal,
                    "recall_pos": runs[-1]["recall_pos"],
                    "fpr": runs[-1]["fpr"],
                }
                print(f"{key:<28} bal_acc={results[key]['bal_acc_mean']:.3f} "
                      f"seeds={[round(b,3) for b in bal]}")
    json.dump(results, open("p204_repr_arch_grid.json", "w"), indent=1)
    print("saved p204_repr_arch_grid.json")

if __name__ == "__main__":
    main()
