# -*- coding: utf-8 -*-
"""P275 environment: synthetic tabletop scenes rendered from two pinhole
cameras with EXACT ground-truth geometry.

The renderer is the only source of truth: it emits per-scene
  - two RGB images (cam1 center, cam2 shifted 15 cm along +x)  -> model input
  - ground truth scene table (positions/sizes in meters)       -> scorer ONLY

Objects: cylinders and boxes in 6 saturated colors; color+kind pairs are
unique per scene so natural-language reference ("red cylinder") resolves to
exactly one object.  This bakes in the premise "recognition is solved" --
what we test is METRIC spatial language, not detection.

Run:  python p275_spatial_env.py            # render 2 demo scenes to out/p275/
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

W, H = 960, 720
FX = FY = 900.0
CX, CY = W / 2.0, H / 2.0

# camera poses (world frame: +x right, +y away from camera, +z up)
CAM_BASE = np.array([0.0, 0.0, 0.45])
BASELINE = 0.15
LOOK_AT = np.array([0.0, 0.55, 0.0])
LIGHT = np.array([-0.3, -0.4, 0.85]) / math.sqrt(0.3**2 + 0.4**2 + 0.85**2)

# color name -> base RGB (saturated, hue-separated for the segmenter)
PALETTE = {
    "red": (210, 40, 40), "blue": (40, 70, 210), "green": (40, 170, 60),
    "yellow": (230, 200, 30), "purple": (150, 50, 200), "orange": (240, 130, 20),
}
# unique color+kind combos => unambiguous reference
COMBOS = [("red", "cylinder"), ("blue", "cylinder"), ("green", "cylinder"),
          ("yellow", "box"), ("purple", "box"), ("orange", "box")]

TABLE_HALF = 0.32          # objects constrained to |x|<=0.22, y in [0.35,0.85]


def look_at(cam_pos, target):
    fwd = target - cam_pos
    fwd = fwd / np.linalg.norm(fwd)
    up_w = np.array([0.0, 0.0, 1.0])
    right = np.cross(fwd, up_w)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return right, up, fwd           # camera basis vectors in world coords


def project(P, cam_pos, basis):
    right, up, fwd = basis
    d = P - cam_pos
    z = d @ fwd
    if z <= 0.05:
        return None
    u = CX + FX * (d @ right) / z
    v = CY - FY * (d @ up) / z
    return u, v, z


def shade(normal):
    n = normal / (np.linalg.norm(normal) + 1e-9)
    if n[2] < 0:
        n = -n
    lam = max(0.0, float(n @ LIGHT))
    return 0.25 + 0.75 * lam


def cyl_faces(pos, r, h, z0=0.0):
    cx, cy = pos[0], pos[1]
    n = 24
    faces = []
    pts_b = [(cx + r * math.cos(2 * math.pi * i / n),
              cy + r * math.sin(2 * math.pi * i / n), z0) for i in range(n)]
    pts_t = [(x, y, z0 + h) for x, y, _ in pts_b]
    for i in range(n):
        j = (i + 1) % n
        nx, ny = math.cos(2 * math.pi * (i + 0.5) / n), math.sin(2 * math.pi * (i + 0.5) / n)
        faces.append(([pts_b[i], pts_b[j], pts_t[j], pts_t[i]], (nx, ny, 0.0)))
    faces.append((pts_t, (0.0, 0.0, 1.0)))       # top cap (single polygon)
    return faces


def box_faces(pos, w, d, h):
    cx, cy = pos[0], pos[1]
    x0, x1 = cx - w / 2, cx + w / 2
    y0, y1 = cy - d / 2, cy + d / 2
    z0, z1 = 0.0, h
    return [
        ([(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)], (0, 0, 1)),   # top
        ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], (0, -1, 0)),  # near side
        ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], (1, 0, 0)),   # +x side
        ([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], (-1, 0, 0)),  # -x side
        ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], (0, 1, 0)),   # far side
    ]


def render(scene, cam_pos, path):
    basis = look_at(cam_pos, LOOK_AT)
    img = Image.new("RGB", (W, H), (235, 235, 235))
    dr = ImageDraw.Draw(img)

    # floor + 5 cm metric grid (gives the direct-VLM arm a scale reference)
    for g in np.arange(-0.4, 1.01, 0.05):
        a = (g, -0.2, 0.0); b = (g, 1.1, 0.0); c = (-0.4, g, 0.0); d = (0.4, g, 0.0)
        major = abs(round(g / 0.05) % 4) < 1
        col = (120, 120, 125) if major else (190, 190, 193)
        for p, q in ((a, b), (c, d)):
            pp, qq = project(np.array(p), cam_pos, basis), project(np.array(q), cam_pos, basis)
            if pp and qq:
                dr.line([pp[:2], qq[:2]], fill=col, width=2 if major else 1)

    # collect faces across objects, painter's algorithm on mean cam depth
    faces = []
    for obj in scene["objects"]:
        for pts, nrm in obj["_faces"]:
            proj = [project(np.array(p), cam_pos, basis) for p in pts]
            if any(p is None for p in proj):
                continue
            depth = float(np.mean([p[2] for p in proj]))
            faces.append((depth, proj, obj["rgb"], nrm))
    faces.sort(key=lambda f: -f[0])
    for _, proj, rgb, nrm in faces:
        s = shade(np.array(nrm, dtype=float))
        col = tuple(int(min(255, c * s)) for c in rgb)
        dr.polygon([p[:2] for p in proj], fill=col,
                   outline=tuple(int(c * 0.75) for c in col))
    img.save(path)
    return path


def make_scene(seed, n_objects):
    rng = np.random.default_rng(seed)
    combos = [COMBOS[i] for i in rng.choice(len(COMBOS), n_objects, replace=False)]
    objects, placed = [], []
    for color, kind in combos:
        for _ in range(400):                      # rejection sampling, min gap
            x = rng.uniform(-0.22, 0.22)
            y = rng.uniform(0.35, 0.85)
            if all(math.hypot(x - px, y - py) >= g for px, py, g in placed):
                break
        else:
            continue
        if kind == "cylinder":
            r = rng.uniform(0.028, 0.042)
            h = rng.uniform(0.055, 0.09)
            size = {"r": round(r, 4), "h": round(h, 4)}
            faces = cyl_faces((x, y), r, h)
            g = 2 * r + 0.04
        else:
            w = rng.uniform(0.06, 0.09)
            h = rng.uniform(0.045, 0.075)
            size = {"w": round(w, 4), "h": round(h, 4)}
            faces = box_faces((x, y), w, w, h)
            g = w * 0.9 + 0.05
        placed.append((x, y, g))
        name = f"{color}_{kind}"
        objects.append({"name": name, "kind": kind, "color": color,
                        "pos": [round(float(x), 4), round(float(y), 4), 0.0],
                        "size": size, "rgb": PALETTE[color], "_faces": faces})
    # stacked probe object (P-spatial-2): a cylinder on TOP of the tallest
    # host, OFF the table plane.  Its true z = host height.  Commands never
    # involve it; only the scene-graph reconstruction is scored on it.
    used = {o["color"] for o in objects}
    free = [c for c, _ in COMBOS if c not in used]
    hosts = [o for o in objects if o["pos"][2] == 0.0]
    if free and hosts:
        host = max(hosts, key=lambda o: o["size"]["h"])
        color = free[0]
        r = 0.018
        h = 0.05
        z0 = host["size"]["h"]
        faces = cyl_faces((host["pos"][0], host["pos"][1]), r, h, z0=z0)
        objects.append({"name": f"{color}_cylinder", "kind": "cylinder",
                        "color": color,
                        "pos": [host["pos"][0], host["pos"][1], round(z0, 4)],
                        "size": {"r": r, "h": h}, "rgb": PALETTE[color],
                        "_faces": faces, "stacked_on": host["name"]})
    return {"seed": seed, "objects": objects}


def clear_target(objs, p, margin=0.06):
    return all(math.hypot(p[0] - o["pos"][0], p[1] - o["pos"][1])
               > margin + (o["size"]["r"] if o["kind"] == "cylinder"
                           else o["size"]["w"] / 2) for o in objs)


def make_commands(scene, rng):
    """Two commands per scene; ground-truth target computed by the harness's
    own table (relation -> world direction), never by either arm.
    Commands only involve table-level objects (never the stacked probe)."""
    objs = [o for o in scene["objects"] if "stacked_on" not in o]
    cmds = []
    templates = ["right_of", "front_of", "midpoint"]
    rng.shuffle(templates)
    for rel in templates[:3]:
        tries = 0
        for _ in range(6):
            if rel == "midpoint":
                if len(objs) < 3:
                    break
                idx = rng.choice(len(objs), 3, replace=False)
                a, b, src = objs[idx[0]], objs[idx[1]], objs[idx[2]]
                tgt = [(a["pos"][0] + b["pos"][0]) / 2, (a["pos"][1] + b["pos"][1]) / 2]
                refs = [a["name"], b["name"]]
                phrase = f"把{cn(src['name'])}放到{cn(a['name'])}和{cn(b['name'])}的中间（两者连线中点）"
            else:
                idx = rng.choice(len(objs), 2, replace=False)
                src, ref = objs[idx[0]], objs[idx[1]]
                off = 0.10 if rel == "right_of" else 0.08
                d = [off, 0.0] if rel == "right_of" else [0.0, off]
                tgt = [ref["pos"][0] + d[0], ref["pos"][1] + d[1]]
                refs = [ref["name"]]
                word = "右边" if rel == "right_of" else "前方"
                phrase = f"把{cn(src['name'])}移到{cn(ref['name'])}的{word} {int(off*100)} cm 处"
            if not (abs(tgt[0]) <= TABLE_HALF and 0.28 <= tgt[1] <= 0.95
                    and clear_target(objs, tgt)):
                continue
            cmds.append({"relation": rel, "source": src["name"], "refs": refs,
                         "offset_m": 0.10 if rel == "right_of" else (0.08 if rel == "front_of" else 0.0),
                         "target_true": [round(tgt[0], 4), round(tgt[1], 4)],
                         "command": phrase})
            break
    return cmds


_CN = {"red": "红色", "blue": "蓝色", "green": "绿色",
       "yellow": "黄色", "purple": "紫色", "orange": "橙色",
       "cylinder": "圆柱", "box": "盒子"}


def cn(obj):
    c, k = obj.split("_")
    return _CN[c] + _CN[k]


def build_all(n_scenes=12, seed0=27400):
    rng = np.random.default_rng(seed0)
    out = []
    for i in range(n_scenes):
        n = 4 + i % 3                              # complexity 4/5/6 objects
        sc = make_scene(seed0 + i, n)
        sc["commands"] = make_commands(sc, rng)
        if len(sc["commands"]) >= 2:
            sc["commands"] = sc["commands"][:2]
        out.append(sc)
    return [s for s in out if s["commands"]]


if __name__ == "__main__":
    os.makedirs("out/p275", exist_ok=True)
    scenes = build_all()
    for i, sc in enumerate(scenes[:2]):
        render(sc, CAM_BASE, f"out/p275/demo{i}_cam1.png")
        render(sc, CAM_BASE + np.array([BASELINE, 0, 0]), f"out/p275/demo{i}_cam2.png")
        gt = {k: v for k, v in sc.items() if k != "_faces"}
        for o in gt["objects"]:
            o.pop("_faces", None)
        json.dump(gt, open(f"out/p275/demo{i}_gt.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"scene {i}: {len(sc['objects'])} objects, "
              f"{len(sc['commands'])} commands -> out/p275/demo{i}_*.png")
    print(f"total {len(scenes)} scenes with >=2 commands")
