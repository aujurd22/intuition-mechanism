# -*- coding: utf-8 -*-
"""P237 (gap G6): mod-3 escape test — three arms x 5 seeds, matched P219/P221-b
protocol (2500 epochs, wd 5.0, lr 1e-3, 60/40 split, final_test primary metric).

P229-b registered prediction (pre-registered before this run): the mod-12
composite's partial learning (P219: test 0.690, mod-4 learned / mod-3 not,
probes at chance) is a LOCAL OPTIMUM — mod-3 gets no gradient pressure.
Adding an auxiliary mod-3 loss (weight 1.0) should supply the missing
pressure -> escape -> final_test > 0.90.

Arms:
  control : CE only, 2500 epochs            (expect ~0.69 partial, P219)
  aux     : CE + 1.0 * CE_mod3 aux head, 2500 epochs (prediction: > 0.90)
  long    : CE only, 25000 epochs           (review round-6 alternative:
                                             "more training alone" escapes?)

Verdict logic (pre-stated):
  aux > 0.90 (and control reproduces ~0.69 partial) -> local-optimum CONFIRMED
  long also > 0.90 -> alternative "just train longer" ALSO sufficient
  neither escapes  -> local optimum robust; aux hypothesis REFUTED
Protocol: 5 seeds (registry-eligible per the P229-b 2->5 seed rule).
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
        self.aux = nn.Linear(d, 3)   # mod-3 auxiliary head (shares trunk)

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
    Xtr = torch.tensor(tr);  Ytr = torch.tensor([(a + b) % P for a, b in tr])
    Ytr3 = torch.tensor([(a + b) % 3 for a, b in tr])
    Xte = torch.tensor(te);  Yte = torch.tensor([(a + b) % P for a, b in te])
    return Xtr, Ytr, Ytr3, Xte, Yte

def run(arm, seed, epochs):
    torch.manual_seed(seed)
    Xtr, Ytr, Ytr3, Xte, Yte = make_split(seed)
    model = Trans()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=5.0)
    curve = []
    for ep in range(1, epochs + 1):
        opt.zero_grad()
        logits, aux_logits = model(Xtr)
        loss = F.cross_entropy(logits, Ytr)
        if arm == "aux":
            loss = loss + F.cross_entropy(aux_logits, Ytr3)
        loss.backward()
        opt.step()
        if ep % 100 == 0:
            with torch.no_grad():
                curve.append({"epoch": ep,
                              "train": float((model(Xtr)[0].argmax(1) == Ytr).float().mean()),
                              "test": float((model(Xte)[0].argmax(1) == Yte).float().mean())})
    final = curve[-1]
    tr99 = next((c["epoch"] for c in curve if c["train"] >= 0.99), None)
    te90 = next((c["epoch"] for c in curve if c["test"] >= 0.9), None)
    return {"arm": arm, "seed": seed, "final_test": final["test"],
            "final_train": final["train"], "tr99_epoch": tr99,
            "te90_epoch": te90, "curve": curve}

ARMS = [("control", 2500), ("aux", 2500), ("long", 25000)]

if __name__ == "__main__":
    t0 = time.time()
    results = {name: [] for name, _ in ARMS}
    for arm, epochs in ARMS:
        for seed in range(5):
            r = run(arm, seed, epochs)
            results[arm].append({k: v for k, v in r.items() if k != "curve"})
            json.dump(results, open("p237_mod3_escape_results.json", "w"), indent=1)
            print(f"[{int(time.time()-t0)}s] {arm} seed{seed}: final_test="
                  f"{r['final_test']:.3f} (train {r['final_train']:.2f})", flush=True)

    summary = {}
    for arm, _ in ARMS:
        accs = [r["final_test"] for r in results[arm]]
        mean = sum(accs) / len(accs)
        var = sum((a - mean) ** 2 for a in accs) / (len(accs) - 1)
        summary[arm] = {"mean": round(mean, 4), "std": round(var ** 0.5, 4),
                        "final_test": accs}
        print(f"{arm}: {mean:.3f} +/- {var**0.5:.3f}  {accs}")

    verdict = {
        "control_partial_reproduced": summary["control"]["mean"] < 0.80,
        "aux_escapes": summary["aux"]["mean"] > 0.90,
        "aux_gap": round(summary["aux"]["mean"] - summary["control"]["mean"], 4),
        "long_escapes": summary["long"]["mean"] > 0.90,
    }
    if verdict["aux_escapes"] and verdict["control_partial_reproduced"]:
        verdict["p229b_local_optimum"] = "CONFIRMED" if not verdict["long_escapes"] \
            else "CONFIRMED_WEAKENED (long training also escapes)"
    else:
        verdict["p229b_local_optimum"] = "REFUTED"
    out = {"config": {"P": P, "split": "60/40", "wd": 5.0, "lr": 1e-3,
                      "epochs": dict(ARMS), "seeds": [0, 1, 2, 3, 4],
                      "protocol": "matched P219/P221-b (final_test primary)"},
           "summary": summary, "verdict": verdict}
    json.dump(out, open("p237_mod3_escape_verdict.json", "w"), indent=1)
    print(json.dumps(verdict, indent=1))
