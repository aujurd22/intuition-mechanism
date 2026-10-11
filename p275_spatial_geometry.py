# -*- coding: utf-8 -*-
"""P275 geometry module: build the "spatial language" scene graph from two
camera views.  Reads ONLY the rendered RGB images + camera calibration
(standard extrinsic/intrinsic knowledge any real system has).  Ground truth
of the environment is off-limits here; it belongs to the scorer.

Pipeline (all mechanical, no LLM):
  1. hue segmentation per palette color   (recognition premise: solved)
  2. bottom-band centroid per view        (contact patch -> table plane)
  3. triangulation of the two centroids   (metric x,y + residual confidence)
  4. metric size from pixel extent at triangulated depth

Output scene graph = the "spatial language": for each object a name, metric
position, metric size estimate, and an explicit confidence.
"""
import colorsys
import math

import numpy as np
from PIL import Image

import p275_spatial_env as env


def hue_of(rgb):
    h, _, _ = colorsys.rgb_to_hsv(*[c / 255 for c in rgb])
    return h * 360.0


def segment(img, rgb_color, hue_tol=18.0, s_min=0.35, v_min=0.10):
    """Mask pixels whose hue matches the object color; returns mask + (u,v)
    of the bottom band (lowest 30% rows of the mask = contact region)."""
    hsv = np.array(img.convert("HSV"), dtype=float)
    h, s, v = hsv[..., 0] * 360.0 / 255.0, hsv[..., 1] / 255.0, hsv[..., 2] / 255.0
    h0 = hue_of(rgb_color)
    dh = np.abs(h - h0)
    dh = np.minimum(dh, 360 - dh)
    mask = (dh < hue_tol) & (s > s_min) & (v > v_min)
    ys, xs = np.nonzero(mask)
    if len(xs) < 40:
        return None
    y_cut = np.quantile(ys, 0.70)
    band = ys >= y_cut
    return {"mask": mask, "centroid": (float(xs[band].mean()), float(ys[band].mean())),
            "n_pix": int(len(xs)),
            "u_span": (float(xs.min()), float(xs.max())),
            "v_span": (float(ys.min()), float(ys.max()))}


def ray_from_pixel(u, v, cam_pos, basis):
    dx = (u - env.CX) / env.FX
    dy = -(v - env.CY) / env.FY
    right, up, fwd = basis
    d = right * dx + up * dy + fwd * 1.0
    return cam_pos, d / np.linalg.norm(d)


def closest_point_midpoint(c1, d1, c2, d2):
    """Midpoint of the shortest segment between two rays."""
    w0 = c1 - c2
    a, b = d1 @ d1, d1 @ d2
    cc, dd = d2 @ d2, d2 @ w0
    denom = a * cc - b * b
    if abs(denom) < 1e-9:
        return None, float("inf")
    t1 = (b * dd - cc * (d1 @ w0)) / denom
    t2 = (a * dd - b * (d1 @ w0)) / denom
    p1, p2 = c1 + t1 * d1, c2 + t2 * d2
    return (p1 + p2) / 2, float(np.linalg.norm(p1 - p2))


def build_scene_graph(scene, img1_path, img2_path, single_view=False):
    """Scene graph from the two views.  single_view=True skips triangulation
    (P-spatial-2 control): position from cam1 only via the table-plane
    prior (intersect ray with z=0), size from cam1 extent only."""
    im1 = Image.open(img1_path)
    im2 = Image.open(img2_path) if not single_view else None
    basis1 = env.look_at(env.CAM_BASE, env.LOOK_AT)
    basis2 = env.look_at(env.CAM_BASE + np.array([env.BASELINE, 0, 0]), env.LOOK_AT)
    graph = {"objects": [], "views": 1 if single_view else 2}
    for obj in scene["objects"]:
        seg1 = segment(im1, obj["rgb"])
        if seg1 is None:
            continue
        est = {"name": obj["name"], "kind": obj["kind"], "color": obj["color"]}
        if single_view:
            c, d = ray_from_pixel(*seg1["centroid"], env.CAM_BASE, basis1)
            t = -c[2] / d[2]                    # table-plane prior (z=0)
            pos = c + t * d                     # -> [x, y, 0] by construction
            conf, resid = 0.4, float("nan")     # no stereo check possible
            z_ref = np.linalg.norm(pos - env.CAM_BASE)
        else:
            seg2 = segment(im2, obj["rgb"])
            if seg2 is None:
                continue
            c1, d1 = ray_from_pixel(*seg1["centroid"], env.CAM_BASE, basis1)
            c2, d2 = ray_from_pixel(*seg2["centroid"],
                                    env.CAM_BASE + np.array([env.BASELINE, 0, 0]), basis2)
            mid, resid = closest_point_midpoint(c1, d1, c2, d2)
            if mid is None:
                continue
            pos = mid                           # full 3D point (z comes out)
            conf = max(0.0, 1.0 - resid / 0.05)     # 5 cm ray skew -> zero
            z_ref = np.linalg.norm(mid - env.CAM_BASE)
        # metric width from horizontal pixel extent at triangulated depth
        w1 = (seg1["u_span"][1] - seg1["u_span"][0]) * z_ref / env.FX
        width = w1 if single_view else 0.5 * (
            w1 + (seg2["u_span"][1] - seg2["u_span"][0]) * z_ref / env.FX)
        est["pos_xyz"] = [round(float(pos[0]), 4), round(float(pos[1]), 4),
                          round(float(pos[2]), 4)]
        est["width_m"] = round(float(width), 4)
        est["dist_to_cam_m"] = round(float(z_ref), 4)
        est["confidence"] = round(float(conf), 3)
        est["reproj_residual_m"] = None if single_view else round(resid, 5)
        graph["objects"].append(est)
    return graph


def graph_errors(graph, scene):
    """Scorer-side helper: reconstruction error of the scene graph itself
    (xy error, z error, width error, per object)."""
    gt = {o["name"]: o for o in scene["objects"]}
    errs, z_errs, size_errs = {}, {}, {}
    for o in graph["objects"]:
        g = gt[o["name"]]
        errs[o["name"]] = round(math.hypot(o["pos_xyz"][0] - g["pos"][0],
                                           o["pos_xyz"][1] - g["pos"][1]), 4)
        z_errs[o["name"]] = round(abs(o["pos_xyz"][2] - g["pos"][2]), 4)
        w_true = g["size"]["r"] * 2 if g["kind"] == "cylinder" else g["size"]["w"]
        size_errs[o["name"]] = round(abs(o["width_m"] - w_true), 4)
    return errs, z_errs, size_errs


if __name__ == "__main__":
    import json
    scenes = env.build_all()
    sc = scenes[0]
    env.render(sc, env.CAM_BASE, "out/p275/_g_cam1.png")
    env.render(sc, env.CAM_BASE + np.array([env.BASELINE, 0, 0]), "out/p275/_g_cam2.png")
    g2 = build_scene_graph(sc, "out/p275/_g_cam1.png", "out/p275/_g_cam2.png")
    g1 = build_scene_graph(sc, "out/p275/_g_cam1.png", None, single_view=True)
    e2, z2, s2 = graph_errors(g2, sc)
    e1, z1, s1 = graph_errors(g1, sc)
    print("two-view  pos errors (cm):", {k: round(v * 100, 1) for k, v in e2.items()})
    print("one-view  pos errors (cm):", {k: round(v * 100, 1) for k, v in e1.items()})
    print("two-view    z errors (cm):", {k: round(v * 100, 1) for k, v in z2.items()})
    print("one-view    z errors (cm):", {k: round(v * 100, 1) for k, v in z1.items()})
    print(json.dumps(g2, ensure_ascii=False, indent=1)[:800])
