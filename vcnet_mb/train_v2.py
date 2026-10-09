"""Spots-10 three-arm training with RSIGym-compliant contract.

v2 changes (addressing OpenRSI #197 review round 2):
  1. DEV/TEST SEPARATION: Work feedback (per-epoch accuracy) uses a
     holdout carved from the TRAIN split only. The official test set is
     loaded exclusively by the Judge. `--eval-test` is a Judge-only flag.
  2. DECLARATIVE CANDIDATE: the agent submits candidate/manifest.json
     (hyperparameters) + candidate/alignment.py (optional architecture
     tweak). Judge reads the manifest and runs the pinned training code
     with those values — the agent cannot edit the training script.
  3. WORK TIME BUDGET: mandatory per-cycle Work time declared
     (RSI_WORK_HOURS, default 1.5h).

Usage:
  Work (agent):   python train.py --arm <arm> --manifest candidate/manifest.json
                  (uses train holdout for feedback, never touches test)
  Judge:          python train.py --arm <arm> --manifest <...> --eval-test
                  (loads official test set, runs FGSM/PGD, writes reward)
"""
import argparse
import json
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader

sys.path.insert(0, "SPOTS-10-main/utilities")
from spots_10_loader import SPOT10Loader

DEV = "cuda" if torch.cuda.is_available() else "cpu"


def load_splits():
    """Returns (train, dev_holdout, test) as TensorDatasets.
    dev_holdout is carved from TRAIN (5k) — the official test set is
    reserved for Judge-only final evaluation."""
    Xtr, ytr = SPOT10Loader.get_data("SPOTS-10-main/dataset", kind="Train")
    Xte, yte = SPOT10Loader.get_data("SPOTS-10-main/dataset", kind="Test")
    Xtr = torch.from_numpy(np.ascontiguousarray(Xtr)).float().unsqueeze(1) / 255.0
    ytr = torch.from_numpy(np.ascontiguousarray(ytr)).long()
    Xte = torch.from_numpy(np.ascontiguousarray(Xte)).float().unsqueeze(1) / 255.0
    yte = torch.from_numpy(np.ascontiguousarray(yte)).long()
    # deterministic dev holdout: last 5k of the shuffled-by-loader order
    g = torch.Generator().manual_seed(20261005)
    idx = torch.randperm(len(ytr), generator=g)
    dev_idx, tr_idx = idx[:5000], idx[5000:]
    return (TensorDataset(Xtr[tr_idx], ytr[tr_idx]),
            TensorDataset(Xtr[dev_idx], ytr[dev_idx]),
            TensorDataset(Xte, yte))


class AdaptiveKWTA(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, k):
        kth = x.kthvalue(x.shape[1] - k + 1, dim=1, keepdim=True).values
        mask = (x >= kth).to(x.dtype)
        ctx.save_for_backward(mask)
        return x * mask

    @staticmethod
    def backward(ctx, grad):
        (mask,) = ctx.saved_tensors
        return grad * (mask + 0.05 * (1 - mask)), None


def adaptive_kwta(x, k_frac=0.10):
    d = x.shape[1]
    k = max(1, int(d * k_frac))
    return AdaptiveKWTA.apply(x, k)


class KWTAAct(nn.Module):
    """Per-position channel top-k (keep top-10% channels at each spatial
    location) — NOT channel-wise whole-map masking."""

    def __init__(self, enabled):
        super().__init__()
        self.enabled = enabled

    def forward(self, x):
        if not self.enabled:
            return F.relu(x)
        return adaptive_kwta(x, 0.10)


class VCStream(nn.Module):
    def __init__(self, kwta):
        super().__init__()
        act = KWTAAct(kwta)
        self.f = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), act,
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), act,
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128),
            KWTAAct(kwta),  # sparse only at stream top
            nn.AdaptiveAvgPool2d(4))

    def forward(self, x):
        return self.f(x)


class PlainCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.f = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1))
        self.head = nn.Linear(128, 10)

    def forward(self, x):
        return self.head(self.f(x).flatten(1))


class VCNet(nn.Module):
    def __init__(self, kwta):
        super().__init__()
        self.ventral = VCStream(kwta)
        self.dorsal = VCStream(kwta)
        self.fuse = nn.Conv2d(256, 128, 1)
        self.feedback = nn.Sequential(
            nn.Conv2d(128, 32, 1), nn.ReLU(inplace=True),
            nn.Conv2d(32, 1, 1))
        self.head = nn.Linear(128, 10)

    def forward(self, x):
        v = self.ventral(x)
        d = self.dorsal(x)
        f = self.fuse(torch.cat([v, d], dim=1))
        gate = torch.sigmoid(self.feedback(d.detach()))
        f = f * (1 + gate)
        return self.head(F.adaptive_avg_pool2d(f, 1).flatten(1))


ARMS = {"plain": lambda: PlainCNN(),
        "vcnet-relu": lambda: VCNet(kwta=False),
        "vcnet-kwta": lambda: VCNet(kwta=True)}


def fgsm(model, loader, eps=0.03):
    model.eval()
    correct = total = 0
    for x, y in loader:
        x, y = x.to(DEV), y.to(DEV)
        x.requires_grad_(True)
        loss = F.cross_entropy(model(x), y)
        model.zero_grad()
        loss.backward()
        x_adv = (x + eps * x.grad.sign()).detach().clamp(0, 1)
        with torch.no_grad():
            correct += (model(x_adv).argmax(1) == y).sum().item()
        total += len(y)
    return correct / max(1, total)


def pgd20(model, loader, eps=0.03, alpha=0.007, steps=20):
    model.eval()
    correct = total = 0
    for x, y in loader:
        x, y = x.to(DEV), y.to(DEV)
        delta = torch.zeros_like(x).uniform_(-eps, eps)
        for _ in range(steps):
            delta.requires_grad_(True)
            loss = F.cross_entropy(model((x + delta).clamp(0, 1)), y)
            grad = torch.autograd.grad(loss, delta)[0]
            delta = (delta + alpha * grad.sign()).clamp(-eps, eps).detach()
        with torch.no_grad():
            correct += (model((x + delta).clamp(0, 1)).argmax(1)
                        == y).sum().item()
        total += len(y)
    return correct / max(1, total)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arm", choices=list(ARMS))
    ap.add_argument("--manifest", default=None,
                    help="declarative candidate: candidate/manifest.json")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--eval-test", action="store_true",
                    help="Judge-only: evaluate on the official test set")
    args = ap.parse_args()

    # manifest hyperparameters (declarative candidate interface)
    hp = dict(lr=2e-3, weight_decay=5e-4, batch_size=128)
    if args.arm == "vcnet-kwta":
        hp["lr"] = 3e-3
    if args.manifest:
        with open(args.manifest, encoding="utf-8") as f:
            m = json.load(f)
        for k in ("lr", "weight_decay", "batch_size"):
            if k in m:
                hp[k] = m[k]

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    train_ds, dev_ds, test_ds = load_splits()
    if args.eval_test:
        eval_ds = test_ds       # Judge-only
    else:
        eval_ds = dev_ds        # Work feedback: train-split holdout
    train_ld = DataLoader(train_ds, batch_size=hp["batch_size"],
                          shuffle=True)
    eval_ld = DataLoader(eval_ds, batch_size=256)

    model = ARMS[args.arm]().to(DEV)
    opt = torch.optim.AdamW(model.parameters(), lr=hp["lr"],
                            weight_decay=hp["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, args.epochs)

    tag = f"{args.arm}_s{args.seed}" + ("_judge" if args.eval_test else "_dev")
    print(f"arm={args.arm} seed={args.seed} mode={'TEST' if args.eval_test else 'DEV'} "
          f"hp={hp}", flush=True)

    for ep in range(args.epochs):
        model.train()
        for x, y in train_ld:
            x, y = x.to(DEV), y.to(DEV)
            opt.zero_grad()
            F.cross_entropy(model(x), y).backward()
            opt.step()
        sched.step()
        model.eval()
        with torch.no_grad():
            acc = sum((model(x.to(DEV)).argmax(1) == y.to(DEV)).sum().item()
                      for x, y in eval_ld) / len(eval_ds)
        print(f"ep {ep+1}/{args.epochs} {'test' if args.eval_test else 'dev'}"
              f"_acc={acc:.4f}", flush=True)

    torch.save(model.state_dict(), f"{tag}.pt")
    if args.eval_test:
        fg = fgsm(model, eval_ld)
        p20 = pgd20(model, eval_ld)
        print(f"FINAL arm={args.arm} seed={args.seed} test_acc={acc:.4f} "
              f"fgsm={fg:.4f} pgd20={p20:.4f}", flush=True)
        import json
        json.dump(dict(arm=args.arm, seed=args.seed, test_acc=acc,
                       fgsm=fg, pgd20=p20),
                  open(f"{tag}_scores.json", "w"), indent=1)


if __name__ == "__main__":
    main()
