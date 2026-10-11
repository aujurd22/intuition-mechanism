# -*- coding: utf-8 -*-
"""P275: Spatial Vocalizer — is metric spatial language (geometry module
emits the numbers, LLM only resolves reference) better than asking a VLM
to read numbers straight off the camera image?

  Arm SL     : two-view images -> mechanical scene graph (triangulation,
               explicit confidence) -> LLM parses the command into an
               intention JSON (object ids + relation ONLY, zero numbers)
               -> harness computes the target from a fixed relation table.
  Arm Direct : single-view image -> VLM outputs target_xy_m directly
               (the current default way; grid gives it a scale reference).

Pre-registered predictions (p275_preregistration.json):
  P-spatial-1 (accuracy)  : SL error < Direct error (paired), and SL error
                            is flat in scene complexity.
  P-spatial-2 (multi-view): off-plane (stacked) objects: two-view recovers
                            position/height; single view + plane prior
                            collapses.  Table objects: both fine (honest
                            boundary).
  P-spatial-3 (grounding) : SL emits zero coordinate numbers (every number
                            traces to the mechanical scene graph); every SL
                            failure is attributable (wrong_object vs
                            geometry_error); Direct failures are not.

Run:  python p275_spatial_harness.py          # full 12 scenes x ~2 commands
      python p275_spatial_harness.py --smoke  # 1 scene, both arms
"""
import base64
import io
import json
import math
import os
import re
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if not os.environ.get("ARK_API_KEY"):
    for ln in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                ".env_ark"), encoding="utf-8"):
        ln = ln.strip()
        if ln.startswith("ARK_API_KEY="):
            os.environ["ARK_API_KEY"] = ln.split("=", 1)[1].strip()
            break
from llm_client import ask
import p275_spatial_env as env
import p275_spatial_geometry as geo

OUT = "out/p275"
PASS_M = 0.03                       # 3 cm, a manipulation-grade tolerance
VLM_MODEL = os.environ.get("P275_VLM_MODEL", "doubao-seed-2.1-lite")

# fixed relation table -- the SAME table defines ground-truth targets and
# SL's mechanical target computation (declared semantic prior, no guessing)
REL_TABLE = {"right_of": (1.0, 0.0), "front_of": (0.0, 1.0)}


# ---------------------------------------------------------------- LLM I/O
def ask_image(prompt: str, png_path: str, model: str = VLM_MODEL) -> str:
    """Vision call: Responses API with an input_image part (data URL)."""
    b64 = base64.b64encode(open(png_path, "rb").read()).decode()
    body = json.dumps({
        "model": model,
        "input": [{"role": "user", "content": [
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"},
        ]}],
        "temperature": 0.0,
        "max_output_tokens": 512,
        "reasoning": {"effort": "minimal"},
    }).encode()
    import urllib.request
    from llm_client import BASE, KEY
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
    return json.loads(m.group(0)) if m else None


# ---------------------------------------------------------------- Arm SL
SL_PROMPT = """你是机械臂指令解析器。下面是几何模块测得的场景图（单位：米，世界坐标系：+x 向右，+y 远离相机，原点=网格中心）。

场景图：
{graph}

任务：把用户命令解析成一个 JSON 意图：
{{"source": "<物体 name>", "relation": "right_of|front_of|midpoint", "refs": ["<物体 name>", ...]}}

关系定义：right_of=目标在 ref 的 +x 方向；front_of=目标在 ref 的 +y 方向；midpoint=目标在两个 ref 的连线中点。命令里的"右边"=right_of，"前方"=front_of，"中间/中点"=midpoint。

硬性规则：只输出 JSON，共三个键（source/relation/refs），禁止输出任何数字、禁止解释。
用户命令：{command}"""


def arm_sl(command, graph):
    t0 = time.time()
    g_txt = json.dumps({"objects": [{k: o[k] for k in
                                     ("name", "pos_xyz", "width_m", "dist_to_cam_m",
                                      "confidence")}
                                    for o in graph["objects"]]},
                       ensure_ascii=False)
    reply = ask(SL_PROMPT.format(graph=g_txt, command=command))
    ms = round((time.time() - t0) * 1000)
    intent = parse_json(reply)
    # P-spatial-3 hard check: the intention carries ZERO numbers
    numeric_fields = []
    if not isinstance(intent, dict):
        return {"ok": False, "fail_stage": "intent_parse", "llm_ms": ms,
                "raw": reply[:300]}
    for k, v in intent.items():
        if k not in ("source", "relation", "refs"):
            numeric_fields.append(k)
    if numeric_fields:
        return {"ok": False, "fail_stage": "intent_has_numbers",
                "llm_ms": ms, "fields": numeric_fields}
    return {"ok": True, "intent": intent, "llm_ms": ms}


def sl_target(intent, graph, command):
    """Mechanical target computation from the scene graph + fixed table."""
    gmap = {o["name"]: o for o in graph["objects"]}
    src, rel, refs = intent.get("source"), intent.get("relation"), intent.get("refs")
    if rel == "midpoint":
        if not (isinstance(refs, list) and len(refs) == 2
                and all(r in gmap for r in refs)):
            return None, "wrong_object"
        a, b = gmap[refs[0]], gmap[refs[1]]
        return [(a["pos_xyz"][0] + b["pos_xyz"][0]) / 2,
                (a["pos_xyz"][1] + b["pos_xyz"][1]) / 2], None
    if rel not in REL_TABLE or src not in gmap or not refs or refs[0] not in gmap:
        return None, "wrong_object"
    d = REL_TABLE[rel]
    m = re.search(r"(\d+(?:\.\d+)?)\s*cm", command)   # offset FROM THE COMMAND TEXT
    if not m:
        return None, "offset_missing"
    off = float(m.group(1)) / 100.0
    ref = gmap[refs[0]]
    return [ref["pos_xyz"][0] + d[0] * off, ref["pos_xyz"][1] + d[1] * off], None


# ------------------------------------------------------------- Arm Direct
DIRECT_PROMPT = """图像是一个俯视的桌面场景。世界坐标系：原点=网格中心（粗线大十字的交点），+x 向右，+y 向画面深处（远离相机），单位米。网格：小格 5 cm，粗线大格 20 cm。

任务：{command}

判断命令执行完成后，被移动物体应处的目标位置的坐标。输出 JSON：{{"target_xy_m": [x, y]}}。只输出 JSON。"""


def arm_direct(command, png):
    t0 = time.time()
    reply = ask_image(DIRECT_PROMPT.format(command=command), png)
    ms = round((time.time() - t0) * 1000)
    out = parse_json(reply)
    if not isinstance(out, dict) or "target_xy_m" not in out:
        return {"ok": False, "fail_stage": "parse", "llm_ms": ms, "raw": reply[:300]}
    xy = out["target_xy_m"]
    if not (isinstance(xy, list) and len(xy) == 2
            and all(isinstance(v, (int, float)) for v in xy)):
        return {"ok": False, "fail_stage": "bad_xy", "llm_ms": ms}
    return {"ok": True, "target": [float(xy[0]), float(xy[1])], "llm_ms": ms}


# ---------------------------------------------------------------- scoring
def score(err):
    return {"err_m": round(err, 4), "err_cm": round(err * 100, 2),
            "pass": bool(err <= PASS_M)}


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def perm_p(paired_diffs, n=20000, seed=7):
    """One-sided sign-flip permutation test: mean(d) > 0."""
    d = np.asarray(paired_diffs, dtype=float)
    d = d[~np.isnan(d)]
    if len(d) == 0:
        return float("nan")
    rng = np.random.default_rng(seed)
    obs = d.mean()
    flips = rng.choice((-1, 1), size=(n, len(d)))
    null = (flips * d).mean(axis=1)
    return float((null >= obs).mean())


# ------------------------------------------------------------------- main
def main(smoke=False):
    os.makedirs(OUT, exist_ok=True)
    scenes = env.build_all()
    if smoke:
        scenes = scenes[:1]
    rows, graph_stats = [], {"two": {}, "one": {}}
    for i, sc in enumerate(scenes):
        p1 = f"{OUT}/s{i}_cam1.png"
        p2 = f"{OUT}/s{i}_cam2.png"
        if not os.path.exists(p1):
            env.render(sc, env.CAM_BASE, p1)
            env.render(sc, env.CAM_BASE + np.array([env.BASELINE, 0, 0]), p2)
        g2 = geo.build_scene_graph(sc, p1, p2)
        g1 = geo.build_scene_graph(sc, p1, None, single_view=True)
        e2, z2, w2 = geo.graph_errors(g2, sc)
        e1, z1, w1 = geo.graph_errors(g1, sc)
        graph_stats["two"].update(e2); graph_stats["one"].update(e1)
        graph_stats.setdefault("z_two", {}).update(z2)
        graph_stats.setdefault("z_one", {}).update(z1)
        print(f"[scene {i}] graph two-view errs(cm): "
              f"{ {k: round(v*100,1) for k, v in e2.items()} }", flush=True)
        for ci, cmd in enumerate(sc["commands"]):
            true_t = cmd["target_true"]
            # ---- Arm SL
            r_sl = arm_sl(cmd["command"], g2)
            row = {"scene": i, "cmd": cmd["command"], "relation": cmd["relation"],
                   "n_objects": len(sc["objects"]), "arm": "SL"}
            if r_sl["ok"]:
                tgt, fail = sl_target(r_sl["intent"], g2, cmd["command"])
                if tgt is None:
                    row.update(attribution=fail, err_m=None, pass_=False)
                else:
                    row.update(intent=r_sl["intent"],
                               target_sl=[round(tgt[0], 4), round(tgt[1], 4)],
                               **score(dist(tgt, true_t)))
                    row["pass_"] = row["pass"]
                    row["attribution"] = ("none" if row["pass_"]
                                          else ("wrong_object" if fail == "wrong_object"
                                                else "geometry_error"))
            else:
                row.update(attribution=r_sl["fail_stage"], err_m=None, pass_=False)
            row["llm_ms"] = r_sl.get("llm_ms")
            rows.append(row)
            # ---- Arm Direct
            r_di = arm_direct(cmd["command"], p1)
            row = {"scene": i, "cmd": cmd["command"], "relation": cmd["relation"],
                   "n_objects": len(sc["objects"]), "arm": "Direct"}
            if r_di["ok"]:
                row.update(target_direct=r_di["target"],
                           **score(dist(r_di["target"], true_t)))
                row["pass_"] = row["pass"]
                row["attribution"] = "not_attributable"
            else:
                row.update(attribution=r_di["fail_stage"], err_m=None, pass_=False)
            row["llm_ms"] = r_di.get("llm_ms")
            rows.append(row)
            print(f"  [{cmd['relation']}] SL: {rows[-2].get('err_cm', rows[-2]['attribution'])} cm | "
                  f"Direct: {rows[-1].get('err_cm', rows[-1]['attribution'])} cm", flush=True)
        if smoke:
            break

    json.dump({"rows": rows, "graph_stats": graph_stats},
              open(f"{OUT}/p275_raw.json" if not smoke else f"{OUT}/p275_smoke_raw.json",
                   "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved raw rows")


if __name__ == "__main__":
    main(smoke="--smoke" in sys.argv)
