"""Spots-10 three-arm comparison: plain CNN / VCNet-ReLU / VCNet-kWTA.

Arms (matched params as closely as possible):
  plain         — standard convnet (conv-bn-relu x4, global pool, fc)
  vcnet-relu    — VCNet-style macro skeleton: two streams (ventral-ish
                  fine detail, dorsal-ish coarse motion), cross-stream
                  fusion, top-down predictive feedback (1x1 conv gate)
  vcnet-kwta    — same skeleton but activations replaced by adaptive
                  k-WTA (10% sparsity, MB microcircuit from flypoet)

Protocol (vcnet_x_mb_design.md):
  full data + 10% subsample arms; 3 seeds each; report test acc +
  FGSM robustness. Run one seed at a time: python train.py <arm> [seed]
"""
import argparse
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


def load_data(subsample=None, seed=0):
    Xtr, ytr = SPOT10Loader.get_data("SPOTS-10-main/dataset", kind="Train")
    Xte, yte = SPOT10Loader.get_data("SPOTS-10-main/dataset", kind="Test")
    Xtr = torch.from_numpy(np.ascontiguousarray(Xtr)).float().unsqueeze(1) / 255.0
    Xte = torch.from_numpy(np.ascontiguousarray(Xte)).float().unsqueeze(1) / 255.0
    ytr = torch.from_numpy(np.ascontiguousarray(ytr)).long()
    yte = torch.from_numpy(np.ascontiguousarray(yte)).long()
    if subsample and subsample < len(ytr):
        g = torch.Generator().manual_seed(seed)
        idx = torch.randperm(len(ytr), generator=g)[:subsample]
        Xtr, ytr = Xtr[idx], ytr[idx]
    return TensorDataset(Xtr, ytr), TensorDataset(Xte, yte)


# ---------------- flypoet's adaptive k-WTA (microcircuit) ----------------
class AdaptiveKWTA(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, k):
        kth = x.flatten(1).kthvalue(
            x.flatten(1).shape[1] - k + 1, dim=1, keepdim=True).values
        mask = (x >= kth.view(x.shape[0], *([1] * (x.dim() - 1)))).to(x.dtype)
        ctx.save_for_backward(mask)
        return x * mask

    @staticmethod
    def backward(ctx, grad):
        (mask,) = ctx.saved_tensors
        # 5% linear bypass: dead units keep a faint gradient stream
        # (pure mask blocks learning through never-selected units)
        return grad * (mask + 0.05 * (1 - mask)), None


def adaptive_kwta(x, k_frac=0.10):
    d = x.shape[1]
    k = max(1, int(d * k_frac))
    return AdaptiveKWTA.apply(x, k)


# ---------------- arms ----------------
class PlainCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.f = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1))
        self.head = nn.Linear(128, 10)

    def forward(self, x):
        return self.head(self.f(x).flatten(1))


class VCStream(nn.Module):
    """One cortical stream: conv stack, optionally k-WTA sparsified."""
    def __init__(self, kwta=False, kwta_late=True):
        super().__init__()
        act = KWTAAct(kwta)
        self.f = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), act,
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), act.clone() if False else KWTAAct(kwta),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), KWTAAct(kwta),
            nn.AdaptiveAvgPool2d(4))
        self.kwta = kwta

    def forward(self, x):
        return self.f(x)


class KWTAAct(nn.Module):
    def __init__(self, enabled):
        super().__init__()
        self.enabled = enabled

    def forward(self, x):
        if not self.enabled:
            return F.relu(x)
        b, c, h, w = x.shape
        k = max(1, int(c * 0.10))
        kth = x.kthvalue(c - k + 1, dim=1, keepdim=True).values
        mask = (x >= kth).to(x.dtype)
        return x * mask  # per-position top-k over channels


class VCNet(nn.Module):
    """Two streams + cross-stream fusion + top-down predictive gate."""
    def __init__(self, kwta):
        super().__init__()
        self.ventral = VCStream(kwta)  # fine detail
        self.dorsal = VCStream(kwta)   # coarse layout
        self.fuse = nn.Conv2d(256, 128, 1)
        # top-down predictive feedback: coarse stream predicts a gate
        # over the fused representation (refinement, not just concat)
        self.feedback = nn.Sequential(
            nn.Conv2d(128, 32, 1), nn.ReLU(inplace=True),
            nn.Conv2d(32, 1, 1))
        self.head = nn.Linear(128, 10)

    def forward(self, x):
        v = self.ventral(x)
        d = self.dorsal(x)
        f = self.fuse(torch.cat([v, d], dim=1))
        gate = torch.sigmoid(self.feedback(d.detach()))
        f = f * (1 + gate)          # predictive refinement
        return self.head(F.adaptive_avg_pool2d(f, 1).flatten(1))


ARMS = {"plain": lambda: PlainCNN(),
        "vcnet-relu": lambda: VCNet(kwta=False),
        "vcnet-kwta": lambda: VCNet(kwta=True)}


def fgsm_robust(model, loader, eps=0.03):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arm", choices=list(ARMS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--subsample", type=int, default=0,
                    help="train-set subsample size (0 = full 40k)")
    ap.add_argument("--epochs", type=int, default=12)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    train_ds, test_ds = load_data(subsample=args.subsample or None,
                                  seed=args.seed)
    train_ld = DataLoader(train_ds, batch_size=128, shuffle=True,
                          num_workers=0)
    test_ld = DataLoader(test_ds, batch_size=256, num_workers=0)

    model = ARMS[args.arm]().to(DEV)
    lr = 3e-3 if args.arm == "vcnet-kwta" else 2e-3
    opt = torch.optim.AdamW(model.parameters(), lr=lr,
                            weight_decay=5e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, args.epochs)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"arm={args.arm} seed={args.seed} params={n_params:,} "
          f"train={len(train_ds)}", flush=True)

    for ep in range(args.epochs):
        model.train()
        t0 = time.time()
        for x, y in train_ld:
            x, y = x.to(DEV), y.to(DEV)
            opt.zero_grad()
            loss = F.cross_entropy(model(x), y)
            loss.backward()
            opt.step()
        sched.step()
        model.eval()
        with torch.no_grad():
            acc = sum((model(x.to(DEV)).argmax(1) == y.to(DEV)).sum().item()
                      for x, y in test_ld) / len(test_ds)
        print(f"ep {ep+1}/{args.epochs} test_acc={acc:.4f} "
              f"({time.time()-t0:.0f}s)", flush=True)

    rob = fgsm_robust(model, test_ld)
    print(f"FINAL arm={args.arm} seed={args.seed} acc={acc:.4f} "
          f"fgsm_eps0.03={rob:.4f} params={n_params}", flush=True)


if __name__ == "__main__":
    main()
