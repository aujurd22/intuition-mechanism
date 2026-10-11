# -*- coding: utf-8 -*-
"""P277: real-world stereo OOD on Middlebury 2006 pairs.

Arm SL     : VLM bbox in each view independently -> mechanical disparity
             (rectified stereo: d = x_left - x_right) -> Z = f*B/d.
Arm Direct : VLM reads depth straight off the left view.

GT: disparity ground truth sampled at the left-bbox center.

Run:  python p277_real_stereo.py [--smoke]
"""
import base64
import io
import json
import os
import re
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if not os.environ.get("ARK_API_KEY"):
    for ln in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                ".env_ark"), encoding="utf-8"):
        ln = ln.strip()
        if ln.startswith("ARK_API_KEY="):
            os.environ["ARK_API_KEY"] = ln.split("=", 1)[1].strip()
            break
from llm_client import BASE, KEY
import urllib.request

DATA = "out/p277"
TARGET_W = 1100                       # resize width (payload + VLM sanity)
B_M = 0.160                           # baseline view1<->view5, meters
ORIG_W = 3072                         # assumed original resolution (declared)
MODEL = os.environ.get("P277_VLM_MODEL", "doubao-seed-2.1-lite")

OBJECTS = [
    ("Bowling1", "green bowling ball"),
    ("Bowling1", "right white bowling pin with red crown marking"),
    ("Lampshade1", "yellow flat board"),
    ("Lampshade1", "cardboard box with red arrows printed on it"),
    ("Lampshade1", "green patterned cylindrical canister"),
    ("Lampshade1", "white plaster cap shape"),
    ("Monopoly", "wooden block standing in the middle of the Monopoly board"),
    ("Monopoly", "Monopoly game board standing upright"),
    ("Flowerpots", "the most centrally located flowerpot"),
    ("Aloe", "the dark brown plant pot at the bottom right, in front of the aloe plant"),
    ("Baby1", "the baby doll sitting on the green dotted box"),
    ("Baby1", "the green dotted box the baby doll sits on"),
    ("Bowling2", "the large green ball"),
    ("Bowling2", "the white bowling pin with red stripes in the middle"),
    ("Lampshade2", "the teddy bear in the wicker basket at the right"),
    ("Lampshade2", "the gray knit beanie hat with MIDDLEBURY band at the front center"),
    ("Midd2", "the blue plastic box with letter N printed on it, front center"),
    ("Midd2", "the bright yellow angular plastic object at the right center"),
    ("Plastic", "the white plaster cap shape in front center"),
    ("Wood1", "the vertical wooden post in the center"),
]

BBOX_PROMPT = """Image size: width {W} px, height {H} px. Locate this object: "{obj}".
Output its bounding box in PIXEL coordinates of THIS image as JSON:
{{"bbox": [x1, y1, x2, y2]}}
Only output JSON."""


def ask_image(prompt: str, jpg_bytes: bytes) -> str:
    b64 = base64.b64encode(jpg_bytes).decode()
    body = json.dumps({
        "model": MODEL,
        "input": [{"role": "user", "content": [
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"},
        ]}],
        "temperature": 0.0, "max_output_tokens": 512,
        "reasoning": {"effort": "minimal"},
    }).encode()
    req = urllib.request.Request(BASE + "/responses", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {KEY}"})
    r = json.loads(urllib.request.urlopen(req, timeout=180).read())
    parts = []
    for item in r.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    parts.append(c["text"])
    return "\n".join(parts)


def parse_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def load_view(scene, view):
    """Load, resize to TARGET_W, return (jpg_bytes, np_gray_float, W, H)."""
    sub = f"{DATA}/{scene}/Illum2Exp1/{view}.png"
    root = f"{DATA}/{scene}/{view}.png"
    path = sub if os.path.exists(sub) else root     # Aloe ships unversioned
    im = Image.open(path).convert("RGB")
    r = TARGET_W / im.width
    im2 = im.resize((TARGET_W, round(im.height * r)), Image.LANCZOS)
    buf = io.BytesIO()
    im2.save(buf, "JPEG", quality=88)
    return buf.getvalue(), im2, im2.width, im2.height


def bbox_center(rep):
    """Returns (cx, cy, bbox, None) on success, (None, None, None, err) on failure."""
    out = parse_json(rep)
    if not isinstance(out, dict) or "bbox" not in out:
        return None, None, None, "parse"
    b = out["bbox"]
    if not (isinstance(b, list) and len(b) == 4
            and all(isinstance(v, (int, float)) for v in b)):
        return None, None, None, "bad_bbox"
    x1, y1, x2, y2 = b
    if not (0 <= x1 < x2 <= 3000 and 0 <= y1 < y2 <= 3000):
        return None, None, None, "out_of_range"
    if x1 < 3 or x2 > 2997 or y1 < 3 or y2 > 2997:
        # touching an image edge = the object may be clipped by the stereo
        # overlap; its two views cannot be trusted to correspond
        return None, None, None, "edge_clipped"
    return (x1 + x2) / 2, (y1 + y2) / 2, [x1, y1, x2, y2], None


def match_disparity(imL, imR, bbox, max_disp=520, half=40):
    """Mechanical NCC template matching: template = a small window at the
    LEFT-bbox CENTER (pure object content; the full bbox would mix depth
    layers and pollute the match), searched in the right view over
    horizontal disparity.  Returns (disparity_px, ncc) in the resized frame."""
    gL = np.array(imL.convert("L"), dtype=float)
    gR = np.array(imR.convert("L"), dtype=float)
    x1, y1, x2, y2 = [int(v) for v in bbox]
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    ty0, ty1 = max(0, cy - half), min(gL.shape[0], cy + half)
    tx0, tx1 = max(0, cx - half), min(gL.shape[1], cx + half)
    if ty1 - ty0 < 20 or tx1 - tx0 < 20:
        return None, 0.0
    T = gL[ty0:ty1, tx0:tx1]
    Tz = T - T.mean()
    tnorm = np.sqrt((Tz**2).sum()) + 1e-9
    best_d, best_n = None, -2.0
    for d in range(-40, min(max_disp, tx0) + 1, 2):    # right-view x = x - d
        if tx0 - d < 0 or tx1 - d > gR.shape[1]:
            continue
        P = gR[ty0:ty1, tx0 - d:tx1 - d]
        Pz = P - P.mean()
        ncc = float((Tz * Pz).sum() / (tnorm * np.sqrt((Pz**2).sum()) + 1e-9))
        if ncc > best_n:
            best_n, best_d = ncc, d
    if best_d is None:
        return None, best_n
    for d in range(max(best_d - 3, -40), min(best_d + 4, tx0 + 1)):  # refine
        if tx0 - d < 0 or tx1 - d > gR.shape[1]:
            continue
        P = gR[ty0:ty1, tx0 - d:tx1 - d]
        Pz = P - P.mean()
        ncc = float((Tz * Pz).sum() / (tnorm * np.sqrt((Pz**2).sum()) + 1e-9))
        if ncc > best_n:
            best_n, best_d = ncc, d
    return best_d, best_n


def gt_depth(scene, W, cx, cy):
    """GT depth from the reference disparity map.  dmin is NOT added: the
    disparity in disp1.png IS the view1<->view5 pixel offset in the shipped
    (cropped) coordinates -- cross-checked by NCC template matching within
    3% (150 px measured vs 154 px map at the same region)."""
    disp = np.array(Image.open(f"{DATA}/{scene}/disp1.png"), dtype=float)
    scale = disp.shape[1] / W
    fx, fy = int(cx * scale), int(cy * scale)
    win = disp[max(0, fy - 20):fy + 21, max(0, fx - 20):fx + 21]
    vals = win[win > 0]
    if len(vals) < 30:
        return None, float("nan")
    d_full = float(np.median(vals))
    f_full = 3740.0 * disp.shape[1] / ORIG_W
    return f_full * B_M / d_full, d_full


def main(smoke=False):
    rows = []
    raw_path = f"{DATA}/p277_raw.json"
    if os.path.exists(raw_path) and not smoke:      # resume: keep finished pairs
        try:
            rows = json.load(open(raw_path, encoding="utf-8"))
        except Exception:
            rows = []
    done = {(r["scene"], r["obj"], r["arm"]) for r in rows}
    pairs = OBJECTS if not smoke else OBJECTS[:1]
    for scene, obj in pairs:
        if ("SL" in {a for (s, o, a) in done if s == scene and o == obj}
                and "Direct" in {a for (s, o, a) in done if s == scene and o == obj}):
            print(f"[{scene}] {obj[:30]}: already done, skip", flush=True)
            continue
        jpgL, imL, W, H = load_view(scene, "view1")
        jpgR, imR, _, _ = load_view(scene, "view5")
        prompt = BBOX_PROMPT.format(W=W, H=H, obj=obj)
        f_full = 3740.0 * W / ORIG_W

        # ---- Arm SL: VLM bbox in the LEFT view (coarse localization),
        # then the geometry module matches the template in the right view
        repL = ask_image(prompt, jpgL)
        cL, cy_L, bL, errL = bbox_center(repL)
        row = {"scene": scene, "obj": obj, "arm": "SL", "bboxL": bL}
        if cL is None:
            row.update(attribution=f"bbox_{errL}", Z_est=None, rel_err=None,
                       pass_=False)
            rows.append(row)
            print(f"[{scene}] {obj[:30]}: SL bbox fail ({row['attribution']})", flush=True)
            continue
        d, ncc = match_disparity(imL, imR, bL)
        disp = float(d) if d is not None else 0.0
        Z = f_full * B_M / disp if disp and disp > 5 else None
        if Z is None or ncc < 0.3:
            row.update(attribution="degenerate_disp", Z_est=None, rel_err=None,
                       pass_=False, disp_px=round(disp, 1), ncc=round(ncc, 3))
            rows.append(row)
            print(f"[{scene}] {obj[:30]}: SL degenerate disp {disp:.0f}px "
                  f"ncc {ncc:.2f}", flush=True)
            continue
        Zgt, d_full = gt_depth(scene, W, cL, cy_L)
        rel = abs(Z - Zgt) / Zgt if Zgt else None
        row.update(disp_px=round(disp, 1), ncc=round(ncc, 3),
                   Z_est=round(Z, 4),
                   Z_gt=round(Zgt, 4) if Zgt else None,
                   rel_err=round(rel, 4) if rel is not None else None,
                   pass_=bool(rel is not None and rel < 0.15),
                   attribution="none" if rel is not None and rel < 0.15
                   else "geometry_error")
        rows.append(row)
        print(f"[{scene}] {obj[:35]}: disp {disp:.0f}px Z {Z:.3f} vs GT {Zgt:.3f} "
              f"({rel*100:.1f}%)", flush=True)

        # ---- Arm Direct: single-view depth guess
        t0 = time.time()
        drep = ask_image(
            f'Estimate the distance from the camera to this object: "{obj}". '
            f'Reply ONLY with JSON: {{"depth_m": <number>}}', jpgL)
        dout = parse_json(drep)
        if isinstance(dout, dict) and isinstance(dout.get("depth_m"), (int, float)):
            Zd = float(dout["depth_m"])
            relD = abs(Zd - Zgt) / Zgt
            rows.append({"scene": scene, "obj": obj, "arm": "Direct",
                         "Z_est": round(Zd, 4), "Z_gt": round(Zgt, 4),
                         "rel_err": round(relD, 4),
                         "signed_err": round((Zd - Zgt) / Zgt, 4),
                         "pass_": bool(relD < 0.15), "attribution": "not_attributable"})
            print(f"    Direct: Z {Zd:.3f} vs GT {Zgt:.3f} ({relD*100:.1f}%)", flush=True)
        else:
            rows.append({"scene": scene, "obj": obj, "arm": "Direct",
                         "Z_est": None, "attribution": "parse", "pass_": False})
            print("    Direct: parse fail", flush=True)

    json.dump(rows, open(f"{DATA}/p277_raw.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("saved", f"{DATA}/p277_raw.json")


if __name__ == "__main__":
    main(smoke="--smoke" in sys.argv)
