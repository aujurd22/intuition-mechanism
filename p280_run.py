# -*- coding: utf-8 -*-
"""P280: PROSPECTIVE test of the frozen consensus-cluster rule (P279 R2).

Three 2006 Middlebury pairs that P277 never touched (Baby2 / Cloth1 / Cloth2).
Design frozen in p280_preregistration.json:
  - 2 objects per scene, chosen by VLM bbox area, the list frozen into
    out/p280/objects.json BEFORE any disparity is computed;
  - bbox stability gate: two temperature-0 calls per object, IoU >= 0.90 or the
    object is dropped as unstable (declared);
  - R1 = median of all valid templates, R2 = largest consensus cluster (frozen
    rule), R3 = random valid template (seed 20261026);
  - validity: disparity < 0 invalid; fewer than two valid templates -> the row
    is non-evaluable.

Run:  python p280_run.py            (uses cached calls where available)
"""
import base64
import io
import json
import os
import random
import re
import statistics
import time
import urllib.error
import urllib.request

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(REPO, "out", "p280", "data")
OUT = os.path.join(REPO, "out", "p280")
CACHE = os.path.join(OUT, "cache")
RAW = os.path.join(OUT, "p280_raw.json")
OBJECTS = os.path.join(OUT, "objects.json")

SCENES = ["Baby2", "Cloth1", "Cloth2"]
TARGET_W = 1100
ORIG_W = 3072            # P277's declared assumption; cancels in relative error
B_M = 0.160
F_AT_3072 = 3740.0
HALF = 40
MAX_DISP = 520
GAP_PX = 5.0
RANDOM_SEED = 20261026
BAR = 0.15
STABILITY_IOU = 0.90
MIN_OBJECTS_PER_SCENE = 2

MODEL = "z-ai/glm-5.3-flash"
BASE = "https://api.commandcode.ai/provider/v1"
CF_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


def api_key():
    """Command Code key: env, then the repo-local file, then the DSH store."""
    for name in ("COMMANDGOAT_API_KEY", "COMMAND_CODE_API_KEY"):
        if os.environ.get(name):
            return os.environ[name]
    local = os.path.join(REPO, ".env_commandgoat")
    if os.path.exists(local):
        for line in open(local, encoding="utf-8"):
            if line.startswith("COMMANDGOAT_API_KEY="):
                return line.split("=", 1)[1].strip()
    store = os.path.join(os.path.expanduser("~"), ".dsh", ".credentials.yaml")
    if os.path.exists(store):
        for line in open(store, encoding="utf-8"):
            parts = line.strip().split(": ", 1)
            if len(parts) == 2 and parts[0] == "COMMANDGOAT_API_KEY":
                return parts[1].strip()
    raise RuntimeError("no COMMANDGOAT_API_KEY (env, .env_commandgoat or ~/.dsh/.credentials.yaml)")


def ask_image(image_bytes, prompt, tag):
    """One temperature-0 vision call, cached on disk by tag."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, tag + ".json")
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    b64 = base64.b64encode(image_bytes).decode()
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}],
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        BASE + "/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Accept": "application/json",
                 "User-Agent": CF_UA,
                 "Authorization": "Bearer " + api_key()})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            resp = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{tag}: HTTP {e.code} {e.read()[:200]}")
    text = resp["choices"][0]["message"]["content"]
    out = {"raw": text, "model": MODEL}
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    time.sleep(0.5)
    return out


def parse_objects(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return []
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    objs = d.get("objects") if isinstance(d, dict) else None
    if not isinstance(objs, list):
        return []
    out = []
    for o in objs:
        if not isinstance(o, dict):
            continue
        b = o.get("bbox")
        if not (isinstance(b, list) and len(b) == 4
                and all(isinstance(v, (int, float)) for v in b)):
            continue
        x1, y1, x2, y2 = [float(v) for v in b]
        if x2 <= x1 or y2 <= y1:
            continue
        out.append({"label": str(o.get("label", ""))[:60],
                    "bbox": [x1, y1, x2, y2]})
    return out


def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    ua = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / ua if ua > 0 else 0.0


def load_view(scene, view):
    im = Image.open(os.path.join(DATA, scene, view + ".png")).convert("RGB")
    r = TARGET_W / im.width
    im2 = im.resize((TARGET_W, round(im.height * r)), Image.LANCZOS)
    buf = io.BytesIO()
    im2.save(buf, "JPEG", quality=90)
    return buf.getvalue(), im2


def gray(im):
    return np.asarray(im.convert("L"), dtype=float)


def ncc_match(gL, gR, cx, cy):
    y0, y1 = max(0, cy - HALF), min(gL.shape[0], cy + HALF)
    x0, x1 = max(0, cx - HALF), min(gL.shape[1], cx + HALF)
    if y1 - y0 < 20 or x1 - x0 < 20:
        return None, 0.0
    T = gL[y0:y1, x0:x1]
    Tz = T - T.mean()
    tnorm = np.sqrt((Tz ** 2).sum()) + 1e-9
    best_d, best_n = None, -2.0
    for d in range(-40, min(MAX_DISP, x0) + 1, 2):
        if x0 - d < 0 or x1 - d > gR.shape[1]:
            continue
        P = gR[y0:y1, x0 - d:x1 - d]
        Pz = P - P.mean()
        ncc = float((Tz * Pz).sum() / (tnorm * np.sqrt((Pz ** 2).sum()) + 1e-9))
        if ncc > best_n:
            best_n, best_d = ncc, d
    if best_d is None:
        return None, best_n
    for d in range(max(best_d - 3, -40), min(best_d + 4, x0 + 1)):
        if x0 - d < 0 or x1 - d > gR.shape[1]:
            continue
        P = gR[y0:y1, x0 - d:x1 - d]
        Pz = P - P.mean()
        ncc = float((Tz * Pz).sum() / (tnorm * np.sqrt((Pz ** 2).sum()) + 1e-9))
        if ncc > best_n:
            best_n, best_d = ncc, d
    return best_d, best_n


def template_set(gL, gR, bbox):
    x1, y1, x2, y2 = bbox
    out = []
    for fx in (0.25, 0.50, 0.75):
        for fy in (0.25, 0.50, 0.75):
            cx = int(round(x1 + fx * (x2 - x1)))
            cy = int(round(y1 + fy * (y2 - y1)))
            if not (cx - HALF >= x1 and cx + HALF <= x2
                    and cy - HALF >= y1 and cy + HALF <= y2):
                continue
            d, n = ncc_match(gL, gR, cx, cy)
            if d is not None:
                out.append({"fx": fx, "fy": fy, "disp": int(d),
                            "ncc": round(float(n), 3)})
    return out


def cluster_pick(templates):
    vals = sorted(t["disp"] for t in templates if t["disp"] >= 0)
    if not vals:
        return None
    groups = [[vals[0]]]
    for v in vals[1:]:
        if v - groups[-1][-1] <= GAP_PX:
            groups[-1].append(v)
        else:
            groups.append([v])
    scored = []
    for g in groups:
        members = [t for t in templates if t["disp"] in g and t["disp"] >= 0]
        scored.append((len(g), sum(m["ncc"] for m in members) / len(members),
                       statistics.median(g), g))
    scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
    return {"median": scored[0][2], "size": scored[0][0],
            "mean_ncc": round(scored[0][1], 3), "members": scored[0][3]}


def gt_depth(scene, W, cx, cy):
    disp = np.asarray(Image.open(os.path.join(DATA, scene, "disp1.png")), dtype=float)
    scale = disp.shape[1] / W
    fx, fy = int(cx * scale), int(cy * scale)
    win = disp[max(0, fy - 20):fy + 21, max(0, fx - 20):fx + 21]
    vals = win[win > 0]
    if len(vals) < 30:
        return None
    d_full = float(np.median(vals))
    f_full = F_AT_3072 * W / ORIG_W
    return f_full * B_M / d_full


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(RANDOM_SEED)
    objects = {}
    if os.path.exists(OBJECTS):
        objects = json.load(open(OBJECTS, encoding="utf-8"))
    rows = []

    for scene in SCENES:
        jpg, im = load_view(scene, "view1")
        W, H = im.size
        prompt = (f"Image size: {W} x {H} px. List up to 5 prominent physical objects "
                  f"(not background regions, not the table/wall itself). For each give a "
                  f"short label and a tight bounding box in pixel coordinates of this image. "
                  f'Reply JSON only: {{"objects":[{{"label":"...","bbox":[x1,y1,x2,y2]}}]}}')
        if scene not in objects:
            replies = [ask_image(jpg, prompt, f"{scene}_list_a"),
                       ask_image(jpg, prompt, f"{scene}_list_b")]
            lists = [parse_objects(r["raw"]) for r in replies]
            matched = []
            for a in lists[0]:
                best, best_iou = None, 0.0
                for b in lists[1]:
                    v = iou(a["bbox"], b["bbox"])
                    if v > best_iou:
                        best, best_iou = b, v
                if best is not None and best_iou >= 0.5:
                    merged = [(a["bbox"][i] + best["bbox"][i]) / 2 for i in range(4)]
                    matched.append({
                        "label": a["label"] or best["label"],
                        "bbox": merged, "iou_two_calls": round(best_iou, 3),
                        "area_px": round((merged[2] - merged[0]) * (merged[3] - merged[1])),
                    })
            matched.sort(key=lambda o: -o["area_px"])
            objects[scene] = {
                "image_wh": [W, H],
                "candidates_stable": [m for m in matched if m["iou_two_calls"] >= STABILITY_IOU],
                "candidates_all": matched,
                "chosen": [m for m in matched if m["iou_two_calls"] >= STABILITY_IOU][:2],
            }
            json.dump(objects, open(OBJECTS, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
        chosen = objects[scene]["chosen"]
        if len(chosen) < MIN_OBJECTS_PER_SCENE:
            print(f"[{scene}] only {len(chosen)} stable objects (needs {MIN_OBJECTS_PER_SCENE})")
        jpgR, imR = load_view(scene, "view5")
        gL, gR = gray(im), gray(imR)
        for o in chosen:
            bbox = o["bbox"]
            templates = template_set(gL, gR, bbox)
            valid = [t for t in templates if t["disp"] >= 0]
            if len(valid) < 2:
                rows.append({"scene": scene, "label": o["label"], "evaluable": False,
                             "n_templates": len(templates), "n_valid": len(valid)})
                continue
            r1 = statistics.median([t["disp"] for t in valid])
            r2 = cluster_pick(valid)
            r3 = rng.choice(valid)["disp"]
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            z_gt = gt_depth(scene, W, cx, cy)
            f_full = F_AT_3072 * W / ORIG_W
            rel = lambda d: round(abs(f_full * B_M / d - z_gt) / z_gt, 4)
            rows.append({
                "scene": scene, "label": o["label"], "evaluable": True,
                "bbox": bbox, "iou_two_calls": o["iou_two_calls"],
                "n_templates": len(templates), "n_valid": len(valid),
                "templates": templates,
                "d_R1": r1, "rel_R1": rel(r1),
                "d_R2": r2["median"], "cluster_size": r2["size"],
                "cluster_members": r2["members"], "rel_R2": rel(r2["median"]),
                "d_R3": r3, "rel_R3": rel(r3),
                "z_gt": round(z_gt, 4), "f_full": round(f_full, 2),
            })
            print(f"[{scene}] {o['label'][:28]:28s} n={len(templates):2d} "
                  f"R1 {r1:6.1f} ({rows[-1]['rel_R1']:.3f})  "
                  f"R2 {r2['median']:6.1f} ({rows[-1]['rel_R2']:.3f})  "
                  f"R3 {r3:4d} ({rows[-1]['rel_R3']:.3f})", flush=True)

    json.dump(rows, open(RAW, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved", RAW, "rows", len(rows))


if __name__ == "__main__":
    main()
