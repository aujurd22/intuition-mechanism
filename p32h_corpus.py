"""Seed-44 corpus replay for P32-h (same generator as p32f_design.py,
verified bit-for-bit against stored 12-term prefixes)."""
import json
import os
from math import comb

import numpy as np


def make_family(step, sign_mode, weight_exp, cshift, wvar):
    def f(n):
        v = 0
        for k in range(n // step + 1):
            term = comb(n, step * k)
            base = comb(step * k, k)
            term *= base ** weight_exp
            m = n - step * k
            term *= comb(2 * m, m) if m > 0 else 1
            if wvar == 1:
                term *= comb(step * k + 1, k)
            sign = (-1) ** k if sign_mode == "alt" else 1
            term *= sign * (2 ** cshift) ** k
            v += term
        return v
    return f


CLASSES = [(2, "no"), (2, "alt"), (3, "no"), (3, "alt"),
           (4, "no"), (4, "alt"), (5, "no"), (5, "alt")]


def build_corpus():
    rng = np.random.default_rng(44)
    corpus = {}
    for (step, sign) in CLASSES:
        for rep in range(600):
            cshift = int(rng.integers(0, 4))
            wexp = int(rng.integers(1, 3))
            wvar = int(rng.integers(0, 2))
            fid = f"H{step}{'a' if sign == 'alt' else 'n'}{rep:04d}"
            f = make_family(step, sign, wexp, cshift, wvar)
            corpus[fid] = {"seq": [f(n) for n in range(12)],
                           "cls": (str(step), sign),
                           "params": (cshift, wexp, wvar)}
    # verify against stored prefixes
    d32 = json.load(open(os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "p32f_design.json")))["sequences"]
    for fid in list(d32)[:50]:
        assert corpus[fid]["seq"] == d32[fid], fid
    return corpus
