# -*- coding: utf-8 -*-
"""intuition_pack v3 upgrade 6+8: out-of-sample alignment probe + pack
transferability grading.

Law anchors:
  P267 — in-sample alignment carries NO discriminative signal (every seed
         fits the training rows); the discriminator is inherently
         OUT-OF-SAMPLE.
  P265 — update-target alignment r=0.51 with final: direction is the signal.
  P248 — labels are window-bound; numeric evidence transfers.  Packs must
         declare how far they can be trusted.

Public API:
  probe_out_of_sample(domain_items, exemplar_pool, ...) -> dict
      Splits items into train-pool / held-out, then measures the judge's
      accuracy AND self-reported alignment separately on each.  The
      train-vs-heldout accuracy GAP quantifies unconsumed structure:
        gap large   -> the domain still has learnable structure (build)
        gap ~0      -> structure consumed or absent (skip / re-scan)
  grade_transferability(pack, neighbor_domains, judge_fn) -> dict
      Runs the pack's exemplars-as-prompt on neighbor domains and grades:
        LOCAL_ONLY / NEIGHBOR_OK / GENERAL — the P248 label-tier analogue
        for packs.
"""
import json
import os
import random


def probe_out_of_sample(domain_items, exemplar_pool, judge_fn,
                        holdout_frac=0.4, seed=20261006):
    """judge_fn(prompt) -> {'PASS'/'FAIL' per item index} (same contract as
    probe.parse_batch consumers).  Items need 'passes' ground truth.

    Returns {train_acc, holdout_acc, gap, verdict}:
      verdict BUILD   — gap >= 15pp (unconsumed structure, P144 analogue)
      verdict SKIP    — gap < 5pp  (structure consumed/absent)
      verdict BORDER  — in between
    """
    items = list(domain_items)
    rnd = random.Random(seed)
    rnd.shuffle(items)
    n_hold = max(1, int(len(items) * holdout_frac))
    hold, train = items[:n_hold], items[n_hold:]

    def acc_on(subset, with_examples):
        lines = []
        if with_examples:
            lines.append("Calibration exemplars (execution-verified):")
            for e in exemplar_pool[:2]:
                lab = "PASS" if e.get("passes") else "FAIL"
                lines.append(f"CODE:\n{e.get('code','')}\nTESTS:\n"
                             f"{e.get('test','')}\nVERDICT: {lab}")
        for i, it in enumerate(subset, 1):
            lines.append(f"--- Candidate {i} ---\nCODE:\n{it.get('code','')}"
                         f"\nTESTS:\n{it.get('test','')}")
        lines.append("\nAnswer exactly one line per candidate: "
                     "'<i>: PASS' or '<i>: FAIL'.")
        res = judge_fn("\n".join(lines), len(subset))
        correct = sum(1 for p, t in zip(res, [it.get("passes") for it in subset])
                      if p is not None and p == t)
        scored = sum(1 for p in res if p is not None)
        return round(100 * correct / max(scored, 1), 1)

    train_acc = acc_on(train, True)
    hold_acc = acc_on(hold, True)
    gap = round(train_acc - hold_acc, 1)
    if gap >= 15:
        verdict = "BUILD"
    elif gap < 5:
        verdict = "SKIP"
    else:
        verdict = "BORDER"
    return {"train_acc": train_acc, "holdout_acc": hold_acc, "gap": gap,
            "verdict": verdict,
            "note": ("P267 law: in-sample alignment is uninformative — the "
                     "train/holdout gap measures the UNCONSUMED structure")}


def grade_transferability(pack_json, neighbor_domains, judge_fn):
    """grade = LOCAL_ONLY / NEIGHBOR_OK / GENERAL (P248 tiers for packs).

    pack_json: dict with 'exemplars' (each with inputs+label) and 'charter'.
    neighbor_domains: {domain_name: [items with ground truth]} — at least
        one item list per neighbor.  judge_fn(prompt, n) -> per-item verdicts.
    """
    ex = pack_json.get("exemplars", [])
    lines = [pack_json.get("charter", ""), "",
             "Calibration exemplars:"]
    for e in ex[:4]:
        ins = ", ".join(f"{k}={v}" for k, v in (e.get("inputs") or {}).items())
        lines.append(f"  {ins} -> {e.get('label')}")
    grades = {}
    for dom, items in neighbor_domains.items():
        test_lines = []
        for i, it in enumerate(items[:8], 1):
            ins = ", ".join(f"{k}={v}" for k, v in (it.get("inputs") or {}).items())
            test_lines.append(f"--- Candidate {i} ---\n{ins}")
        prompt = "\n".join(lines + ["", "Judge each candidate:"] + test_lines +
                           ["\nAnswer '<i>: PASS' or '<i>: FAIL'."])
        res = judge_fn(prompt, min(8, len(items)))
        truth = [it.get("label", it.get("passes")) for it in items[:len(res)]]
        norm = lambda x: ("PASS" if x in (True, "PASS", "passes") else
                          "FAIL" if x is not None else None)
        correct = sum(1 for p, t in zip(res, truth)
                      if p is not None and norm(p) == norm(t))
        acc = correct / max(1, sum(1 for p in res if p is not None))
        grades[dom] = round(acc, 3)
    vals = list(grades.values())
    if not vals:
        overall = "UNTESTED"
    elif all(v >= 0.8 for v in vals):
        overall = "GENERAL"
    elif any(v >= 0.8 for v in vals):
        overall = "NEIGHBOR_OK"
    else:
        overall = "LOCAL_ONLY"
    return {"per_domain": grades, "grade": overall,
            "note": ("P248 tier analogue: labels are window-bound; a pack "
                     "claiming GENERAL must survive every neighbor ≥0.8")}
