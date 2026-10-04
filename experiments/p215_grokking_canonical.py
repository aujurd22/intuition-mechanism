"""P215: grokking canonical setup (small transformer, full-table modular addition).
Task: (a+b) mod 12 over the full table (12^2 = 144 samples), 60/40 split —
the classic grokking regime (small data, heavy weight decay, delayed
generalization). After convergence/phase change: Fourier + mod-component
probes on the embedding (Nanda-style), connecting to the P188 character
table (class-group Fourier features)."""
import os, json, random
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
    def forward(self, ab):            # ab: [B, 2] token ids
        idx = torch.arange(2).unsqueeze(0).expand(ab.shape[0], -1)
        h = self.emb(ab) + self.pos(idx)
        h = self.enc(h)
        return self.out(h[:, 0])       # read out at position 0

def main():
    import itertools
    torch.manual_seed(0)
    pairs = list(itertools.product(range(P), range(P)))
    random.Random(0).shuffle(pairs)
    ntr = int(len(pairs) * 0.6)
    tr, te = pairs[:ntr], pairs[ntr:]
    Xtr = torch.tensor(tr); Ytr = torch.tensor([(a + b) % P for a, b in tr])
    Xte = torch.tensor(te); Yte = torch.tensor([(a + b) % P for a, b in te])
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    curve = []
    EPOCHS = 4000
    for ep in range(1, EPOCHS + 1):
        opt.zero_grad()
        loss = F.cross_entropy(model(Xtr), Ytr)
        loss.backward(); opt.step()
        if ep % 25 == 0 or ep == 1:
            with torch.no_grad():
                tr_acc = float((model(Xtr).argmax(1) == Ytr).float().mean())
                te_acc = float((model(Xte).argmax(1) == Yte).float().mean())
            curve.append({"epoch": ep, "train": tr_acc, "test": te_acc})
            json.dump(curve, open("p215_grokking_curve.json", "w"))
            if ep % 200 == 0:
                print(f"ep {ep:>5}: train {tr_acc:.3f}  test {te_acc:.3f}")
    json.dump(curve, open("p215_grokking_curve.json", "w"))
    with torch.no_grad():
        print(f"final: train {float((model(Xtr).argmax(1)==Ytr).float().mean()):.3f} "
              f"test {float((model(Xte).argmax(1)==Yte).float().mean()):.3f}")
    # grokking detection: did test acc jump from <=0.5 to >=0.9 after train hit 1.0?
    tr100 = next((c["epoch"] for c in curve if c["train"] >= 0.999), None)
    te90_after = next((c["epoch"] for c in curve if c["epoch"] >= (tr100 or 0) and c["test"] >= 0.9), None)
    grok = tr100 is not None and te90_after is not None and te90_after > tr100
    print(f"train hit 1.0 at epoch {tr100}; test reached 0.9 after at epoch {te90_after}; "
          f"grokking = {grok}")
    # Fourier probe: embedding norm per frequency (Nanda-style, on token embeddings)
    E = model.emb.weight.detach()
    freqs = {}
    for k in range(1, P):
        c = torch.cos(torch.arange(P) * 2 * torch.pi * k / P)
        s = torch.sin(torch.arange(P) * 2 * torch.pi * k / P)
        freqs[k] = float(((E.T @ c) ** 2).sum() + ((E.T @ s) ** 2).sum())
    tot = float((E ** 2).sum())
    top = sorted(freqs.items(), key=lambda kv: -kv[1])[:3]
    print("embedding Fourier top frequencies:", [(k, round(v / tot, 3)) for k, v in top])
    json.dump({"grokking": grok, "tr100": tr100, "te90_after": te90_after,
               "fourier_top": {str(k): round(v / tot, 3) for k, v in top},
               "embed_energy_frac": {str(k): round(v / tot, 3) for k, v in freqs.items()}},
              open("p215_grokking_fourier.json", "w"), indent=1)
    print("saved p215_grokking_fourier.json")

if __name__ == "__main__":
    main()
