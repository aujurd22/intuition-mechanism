# -*- coding: utf-8 -*-
"""P276: stacking-chain probe on the P275 synthetic stereo rig.

Chain depth is determined by free palette colors (4 table objects -> 2
layers stacked on the tallest host; 5 -> 1 layer; 6 -> none), so depth
0/1/2 appear across the scene set and become the independent variable.
Zero LLM calls: this scores the geometry module only.

Run:  python p276_spatial_stack.py     -> out/p276/ + p276_verdict.json
"""
import json
import math
import os

import numpy as np

import p275_spatial_env as env
import p275_spatial_geometry as geo

OUT = "out/p276"


def box_faces_z(pos, w, d, h, z0):
    """env.box_faces sitting on an arbitrary base height z0."""
    cx, cy = pos[0], pos[1]
    x0, x1 = cx - w / 2, cx + w / 2
    y0, y1 = cy - d / 2, cy + d / 2
    zb, zt = z0, z0 + h
    return [
        ([(x0, y1, zt), (x1, y1, zt), (x1, y0, zt), (x0, y0, zt)], (0, 0, 1)),
        ([(x0, y0, zb), (x1, y0, zb), (x1, y0, zt), (x0, y0, zt)], (0, -1, 0)),
        ([(x1, y0, zb), (x1, y1, zb), (x1, y1, zt), (x1, y0, zt)], (1, 0, 0)),
        ([(x0, y1, zb), (x0, y0, zb), (x0, y0, zt), (x0, y1, zt)], (-1, 0, 0)),
        ([(x0, y1, zb), (x1, y1, zb), (x1, y1, zt), (x0, y1, zt)], (0, 1, 0)),
    ]


def make_chain_scene(seed, n_table):
    """P275 scene generation minus the P275 probe, plus a stacking chain."""
    rng = np.random.default_rng(seed)
    combos = [env.COMBOS[i] for i in rng.choice(len(env.COMBOS), n_table, replace=False)]
    objects, placed = [], []
    for color, kind in combos:
        for _ in range(400):
            x = rng.uniform(-0.22, 0.22)
            y = rng.uniform(0.35, 0.85)
            if all(math.hypot(x - px, y - py) >= g for px, py, g in placed):
                break
        else:
            continue
        if kind == "cylinder":
            r = rng.uniform(0.028, 0.042)
            h = rng.uniform(0.055, 0.09)
            size, faces = {"r": round(r, 4), "h": round(h, 4)}, env.cyl_faces((x, y), r, h)
            g = 2 * r + 0.04
        else:
            w = rng.uniform(0.06, 0.09)
            h = rng.uniform(0.045, 0.075)
            size, faces = {"w": round(w, 4), "h": round(h, 4)}, env.box_faces((x, y), w, w, h)
            g = w * 0.9 + 0.05
        placed.append((x, y, g))
        objects.append({"name": f"{color}_{kind}", "kind": kind, "color": color,
                        "pos": [round(float(x), 4), round(float(y), 4), 0.0],
                        "size": size, "rgb": env.PALETTE[color], "_faces": faces})
    free = [c for c, _ in env.COMBOS if c not in {o["color"] for o in objects}]
    hosts = [o for o in objects if o["pos"][2] == 0.0]
    chain_depth = min(len(free), 2)
    if hosts and chain_depth > 0:
        host = max(hosts, key=lambda o: o["size"]["h"])
        hx, hy = host["pos"][0], host["pos"][1]
        z = host["size"]["h"]
        if chain_depth >= 1:                      # layer 1: cylinder on host
            r, h = 0.018, 0.055
            objects.append({
                "name": f"{free[0]}_cylinder", "kind": "cylinder", "color": free[0],
                "pos": [hx, hy, round(z, 4)], "size": {"r": r, "h": h},
                "rgb": env.PALETTE[free[0]], "_faces": env.cyl_faces((hx, hy), r, h, z0=z),
                "stacked_on": host["name"], "layer": 1})
            z += h
        if chain_depth >= 2:                      # layer 2: small box on layer 1
            w, h = 0.028, 0.028
            objects.append({
                "name": f"{free[1]}_box", "kind": "box", "color": free[1],
                "pos": [hx, hy, round(z, 4)], "size": {"w": w, "h": h},
                "rgb": env.PALETTE[free[1]], "_faces": box_faces_z((hx, hy), w, w, h, z0=z),
                "stacked_on": f"{free[0]}_cylinder", "layer": 2})
    return {"seed": seed, "objects": objects,
            "chain_depth": chain_depth}


def build_all(n_scenes=12, seed0=27600):
    return [make_chain_scene(seed0 + i, 4 + i % 3) for i in range(n_scenes)]


def main():
    os.makedirs(OUT, exist_ok=True)
    scenes = build_all()
    per_layer = {}                     # layer -> list of error dicts
    for i, sc in enumerate(scenes):
        p1, p2 = f"{OUT}/s{i}_cam1.png", f"{OUT}/s{i}_cam2.png"
        env.render(sc, env.CAM_BASE, p1)
        env.render(sc, env.CAM_BASE + np.array([env.BASELINE, 0, 0]), p2)
        g2 = geo.build_scene_graph(sc, p1, p2)
        g1 = geo.build_scene_graph(sc, p1, None, single_view=True)
        e2, z2, _ = geo.graph_errors(g2, sc)
        e1, z1, _ = geo.graph_errors(g1, sc)
        for o in sc["objects"]:
            if "layer" not in o:
                continue
            slot = per_layer.setdefault((o["layer"], i), {})
            slot.update(depth=o["layer"], scene=i,
                        two_xy=e2.get(o["name"]), two_z=z2.get(o["name"]),
                        one_xy=e1.get(o["name"]), one_z=z1.get(o["name"]))
        print(f"[scene {i}] chain_depth={sc['chain_depth']} "
              f"two_z(cm)={ {k: round(v.get('two_z', float('nan'))*100, 1)
                             for k, v in per_layer.items() if v['scene'] == i} }", flush=True)
    json.dump({"per_layer": [v for v in per_layer.values()]},
              open(f"{OUT}/p276_raw.json", "w", encoding="utf-8"), indent=1)

    # ---------------- verdict from pre-registered predictions
    raw = json.load(open(f"{OUT}/p276_raw.json", encoding="utf-8"))["per_layer"]
    med = lambda xs: float(np.median(xs)) if xs else float("nan")
    by = lambda d, k: [r[k] for r in d if r[k] is not None]
    d1 = [r for r in raw if r["depth"] == 1]
    d2 = [r for r in raw if r["depth"] == 2]
    verdict = {"id": "P276", "n_layer_instances": len(raw),
               "depth1_n": len(d1), "depth2_n": len(d2), "predictions": []}

    two_z1, two_z2 = med(by(d1, "two_z")), med(by(d2, "two_z"))
    p1_ok = (two_z1 < 0.02) and ((not d2) or (two_z2 < 0.02))
    verdict["predictions"].append({
        "id": "P-stack-1", "verdict": "PASS" if p1_ok else "FAIL",
        "two_view_z_median_cm": {"layer1": round(two_z1 * 100, 2),
                                 "layer2": round(two_z2 * 100, 2) if d2 else None}})

    one_z1, one_z2 = med(by(d1, "one_z")), med(by(d2, "one_z"))
    one_xy1, one_xy2 = med(by(d1, "one_xy")), med(by(d2, "one_xy"))
    two_xy1, two_xy2 = med(by(d1, "two_xy")), med(by(d2, "two_xy"))
    p2_ok = (one_z1 > 0.03) and ((not d2) or (one_z2 > 0.03)) \
        and ((not d2) or (one_xy2 > one_xy1)) and (two_xy2 <= two_xy1 * 1.5)
    verdict["predictions"].append({
        "id": "P-stack-2", "verdict": "PASS" if p2_ok else "FAIL",
        "one_view_z_median_cm": {"layer1": round(one_z1 * 100, 2),
                                 "layer2": round(one_z2 * 100, 2) if d2 else None},
        "one_view_xy_median_cm": {"layer1": round(one_xy1 * 100, 2),
                                  "layer2": round(one_xy2 * 100, 2) if d2 else None},
        "two_view_xy_median_cm": {"layer1": round(two_xy1 * 100, 2),
                                  "layer2": round(two_xy2 * 100, 2) if d2 else None}})

    p3_ok = (two_xy1 < 0.02) and ((not d2) or (two_xy2 < 0.02))
    verdict["predictions"].append({
        "id": "P-stack-3", "verdict": "PASS" if p3_ok else "FAIL",
        "two_view_xy_median_cm": {"layer1": round(two_xy1 * 100, 2),
                                  "layer2": round(two_xy2 * 100, 2) if d2 else None}})
    verdict["overall"] = "PASS" if all(p["verdict"] == "PASS"
                                       for p in verdict["predictions"]) else "MIXED"
    json.dump(verdict, open("p276_verdict.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(verdict, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
