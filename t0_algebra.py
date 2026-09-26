"""T0 domain 1: algebraic identity families (surface = names/order/form).

Intuition-Mechanism Program, T0 domain 1 (research plan section T0). This
domain makes structure and surface INDEPENDENT, which the graph domain could
not: the same identity template is rendered with random variable names,
shuffled term order and LHS/RHS swaps. Prediction (registered P1, under-
compression end): with little compression the encoder copies the surface
(names), so same-template-different-name neighbours are FAR -> SD collapses
at LOW compression; mid compression forces abstraction over names -> SD
high. The graph domain could not show this end.

Run:  python t0_algebra.py [--templates 6] [--instances 20] [--relabels 3]
Then: python t0_scan.py --dataset t0_algebra.npz --bottlenecks 1,2,4,8,32,144
"""
import argparse
import json
import random

import numpy as np
import sympy as sp

POOL = list("abcdefgh")


def make_templates():
    x, y = sp.symbols("x y")
    return {
        "sq_plus": (x + y) ** 2,
        "sq_minus": (x - y) ** 2,
        "diff_squares": x ** 2 - y ** 2,
        "cube_plus": (x + y) ** 3,
        "cube_minus": (x - y) ** 3,
        "distrib2": x * (x + y) + y * (x + y),
    }


def render(expr_terms, rng):
    """Random-equivalent string: shuffled term order, +/- folded in."""
    terms = list(expr_terms)
    rng.shuffle(terms)
    parts = []
    for t in terms:
        s = sp.sstr(t)
        if s.startswith("-"):
            parts.append("- " + s[1:])
        else:
            parts.append("+ " + s)
    s = (" ".join(parts)).lstrip("+ ")
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--templates", type=int, default=6)
    ap.add_argument("--instances", type=int, default=20)
    ap.add_argument("--relabels", type=int, default=3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--width", type=int, default=64)
    ap.add_argument("--tag-len", type=int, default=0,
                    help="append a unique per-instance random surface tag of "
                         "this length (salience experiment: makes surface "
                         "signal dominate; tests the under-compression wall)")
    ap.add_argument("--out", default="t0_algebra.npz")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    tag_rng = random.Random(args.seed + 999)
    templates = list(make_templates())[: args.templates]
    alphabet = sorted(set("".join(POOL) + "0123456789()+-*=^ "))
    ch2i = {c: i for i, c in enumerate(alphabet)}
    W, V = args.width, len(alphabet)

    xs, fam, inst, rel = [], [], [], []
    for fi, name in enumerate(templates):
        x, y = sp.symbols("x y")
        expr = make_templates()[name]
        expanded = sp.Add.make_args(sp.expand(expr))
        for inst_id in range(args.instances):
            names = rng.sample(POOL, 2)
            sub = {x: sp.Symbol(names[0]), y: sp.Symbol(names[1])}
            tag = "".join(tag_rng.choice(POOL + [str(d) for d in range(10)])
                          for _ in range(args.tag_len))
            terms = [t.subs(sub) for t in expanded]
            for r in range(args.relabels):
                if r == 1:  # swap sides: LHS = expanded, RHS = compact form
                    s = (sp.sstr(expr.subs(sub)) + " = "
                         + render(terms, rng))
                elif r == 2:  # same, reversed
                    s = (render(terms, rng) + " = "
                         + sp.sstr(expr.subs(sub)))
                else:
                    s = render(terms, rng) + " = 0"
                if args.tag_len:
                    s = s + " TAG:" + tag
                s = s[: args.width].ljust(args.width)
                vec = np.zeros((W, V), dtype=np.float32)
                for pos, ch in enumerate(s):
                    if ch in ch2i:
                        vec[pos, ch2i[ch]] = 1.0
                xs.append(vec.reshape(-1))
                fam.append(fi)
                inst.append(inst_id)
                rel.append(r)
    xs = np.stack(xs).astype(np.float32)
    fam = np.array(fam, dtype=np.int32)
    inst = np.array(inst, dtype=np.int32)
    rel = np.array(rel, dtype=np.int32)
    meta = {"templates": templates, "width": W, "vocab": V,
            "instances": args.instances, "relabels": args.relabels,
            "seed": args.seed}
    np.savez(args.out, x=xs, family=fam, instance=inst, relabel=rel,
             meta=json.dumps(meta))
    print(f"dataset: {xs.shape[0]} samples, input dim {xs.shape[1]} "
          f"({W}x{V}), {len(templates)} templates -> {args.out}")
    print(f"example: {''.join(alphabet[i] for i in xs[0].reshape(W, V).argmax(1)).rstrip()}")


if __name__ == "__main__":
    main()
