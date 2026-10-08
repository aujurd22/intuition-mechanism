"""PGD-20 attack + sample-efficiency curve for the three arms.
Usage: python robust_suite.py   (runs PGD on all arms, then SE curve)
Outputs: robust_suite_results.json
"""
import json
import subprocess
import sys
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

sys.path.insert(0, ".")
from train import ARMS, load_data, DEV

EPS = 0.03
ALPHA = 0.007
STEPS = 20


def load_arm(arm):
    m = ARMS[arm]().to(DEV)
    return m


def pgd(model, loader):
    model.eval()
    correct = total = 0
    for x, y in loader:
        x, y = x.to(DEV), y.to(DEV)
        delta = torch.zeros_like(x).uniform_(-EPS, EPS)
        for _ in range(STEPS):
            delta.requires_grad_(True)
            loss = F.cross_entropy(model((x + delta).clamp(0, 1)), y)
            grad = torch.autograd.grad(loss, delta)[0]
            delta = (delta + ALPHA * grad.sign()).clamp(-EPS, EPS).detach()
        with torch.no_grad():
            correct += (model((x + delta).clamp(0, 1)).argmax(1)
                        == y).sum().item()
        total += len(y)
    return correct / max(1, total)


def main():
    _, test_ds = load_data()
    test_ld = DataLoader(test_ds, batch_size=256, num_workers=0)
    out = {}
    # train each arm fresh (15 ep, full data — same as main comparison)
    for arm in ("vcnet-kwta", "vcnet-relu", "plain"):
        print(f"=== training {arm} for PGD ===", flush=True)
        import train as T
        torch.manual_seed(0)
        train_ds, _ = T.load_data()
        train_ld = DataLoader(train_ds, batch_size=128, shuffle=True)
        model = ARMS[arm]().to(DEV)
        opt = torch.optim.AdamW(model.parameters(), lr=2e-3,
                                weight_decay=5e-4)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, 15)
        model.train()
        for ep in range(15):
            for x, y in train_ld:
                x, y = x.to(DEV), y.to(DEV)
                opt.zero_grad()
                F.cross_entropy(model(x), y).backward()
                opt.step()
            sched.step()
        acc_pgd = pgd(model, test_ld)
        out[arm] = {"pgd20_eps0.03": round(acc_pgd, 4)}
        print(f"{arm}: PGD-20 acc={acc_pgd:.4f}", flush=True)
        json.dump(out, open("robust_suite_results.json", "w"), indent=1)
    print("PGD SUITE COMPLETE", flush=True)


if __name__ == "__main__":
    main()

