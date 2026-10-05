# -*- coding: utf-8 -*-
"""P270 harness: glm-5.3-flash plays ls20, two conditions.
  gate   : every action MUST carry predicted-changed-cells claims; the toll
           booth verifies against the actual frame diff; REFUTED (precision<0.5)
           gets numeric evidence fed back into the next prompt.
  nogate : actions only, no claims requested.
Run: python p270_harness.py <gate|nogate> [max_actions=120] [game=ls20] [out=...]
"""
import os, sys, json, base64, math, random
import io as _io
import urllib.request

os.environ.setdefault("ARC_API_KEY", "365afa63-6d4d-4646-836a-f7df8a5bccd5")
import numpy as np
from PIL import Image
import arc_agi
from arcengine.enums import GameAction

ARK_KEY = os.environ.get("ARK_API_KEY") or "365afa63-6d4d-4646-836a-f7df8a5bccd5"
ARK_URL = "https://ark.cn-beijing.volces.com/api/coding/v3/responses"
MODEL = "glm-5.3-flash"
PALETTE = {0: (255, 255, 255), 1: (204, 204, 204), 2: (153, 153, 153),
           3: (102, 102, 102), 4: (51, 51, 51), 5: (0, 0, 0),
           6: (229, 58, 163), 7: (255, 123, 204), 8: (249, 60, 49),
           9: (30, 147, 255), 10: (136, 216, 241), 11: (255, 220, 0),
           12: (255, 133, 27), 13: (146, 18, 49), 14: (79, 204, 48),
           15: (163, 86, 214)}
ACTIONS = ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5", "ACTION6"]

def glm_vision(prompt, png_bytes):
    b64 = base64.b64encode(png_bytes).decode()
    body = {"model": MODEL, "input": [{"role": "user", "content": [
        {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"},
        {"type": "input_text", "text": prompt}]}]}
    req = urllib.request.Request(ARK_URL, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {ARK_KEY}"})
    r = json.loads(urllib.request.urlopen(req, timeout=120).read())
    out = r.get("output_text") or "".join(
        c.get("text", "") for o in r.get("output", [])
        for c in o.get("content", []) if isinstance(c, dict))
    return out

def render_png(grid):
    """(1,64,64) -> upscaled PNG bytes with palette"""
    g = np.asarray(grid)[0]
    im = Image.new("RGB", (64, 64))
    px = im.load()
    for r in range(64):
        for c in range(64):
            px[r, c] = PALETTE.get(int(g[r, c]), (255, 0, 255))
    im = im.resize((512, 512), Image.NEAREST)
    buf = _io.BytesIO(); im.save(buf, "PNG")
    return buf.getvalue()

def diff_cells(g0, g1):
    g0 = np.asarray(g0)[0]; g1 = np.asarray(g1)[0]
    out = []
    for r in range(g0.shape[0]):
        for c in range(g0.shape[1]):
            if g0[r, c] != g1[r, c]:
                out.append((r, c, int(g1[r, c])))
    return out

def parse_turn(text, gate):
    import re
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None, None
    try:
        obj = json.loads(m.group(0))
    except Exception:
        return None, None
    action = obj.get("action")
    if action not in ACTIONS:
        return None, None
    claims = obj.get("claims") if gate else None
    clean = []
    if isinstance(claims, list):
        for cl in claims[:8]:
            try:
                r, c, after = int(cl["r"]), int(cl["c"]), int(cl["after"])
                if 0 <= r < 64 and 0 <= c < 64 and 0 <= after <= 15:
                    clean.append((r, c, after))
            except Exception:
                pass
    return action, clean

def main():
    cond = sys.argv[1] if len(sys.argv) > 1 else "gate"
    max_actions = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    game = sys.argv[3] if len(sys.argv) > 3 else "ls20"
    logfile = f"p270_{cond}_{game}.jsonl"
    logf = open(logfile, "w", encoding="utf-8")

    arc = arc_agi.Arcade()
    env = arc.make(game)
    obs = env.reset()
    g_prev = obs.frame
    avail = obs.available_actions or ACTIONS
    levels_start = 0
    steps = 0
    precisions = []
    refuted = 0
    evidence = ""
    f_log = lambda o: logf.write(json.dumps(o, ensure_ascii=False) + "\n") or logf.flush()

    while steps < max_actions:
        grid_png = render_png(g_prev)
        if cond == "gate":
            prompt = ("你在玩一个 64x64 的格子游戏。这是当前帧（调色板：0白 5黑 8红 9蓝 11黄 12橙，"
                      "其它数字是其它颜色）。可用动作: " + ",".join(avail) + "。\n"
                      "选择下一个动作，并预测这个动作会导致哪些格子发生变化（最多 8 个，"
                      "每个格子给行、列和变化后的色号）。" + (evidence or ""))
        else:
            prompt = ("你在玩一个 64x64 的格子游戏。这是当前帧。可用动作: " + ",".join(avail) + "。\n"
                      "选择下一个动作。")
        js = '严格只输出一个 JSON 对象：{"action":"ACTIONx"' + (
            ',"claims":[{"r":行,"c":列,"after":色号}]}' if cond == "gate" else "}")
        resp = glm_vision(prompt + "\n" + js + "\n当前帧如上。", grid_png)
        action, claims = parse_turn(resp, cond == "gate")
        tries = 0
        while action is None and tries < 1:
            resp = glm_vision(prompt + "\n\n你上次的输出无法解析。再次只输出 JSON。", grid_png)
            action, claims = parse_turn(resp, cond == "gate")
            tries += 1
        if action is None:
            f_log({"step": steps, "event": "unparseable", "raw": resp[:200]})
            print(f"[{steps}] unparseable, skip", flush=True)
            continue
        ai = ACTIONS.index(action) + 1
        if avail and ai not in avail:
            ai = avail[(ai - 1) % len(avail)]
        try:
            res = env.step(GameAction(ai))
        except Exception as ex:
            f_log({"step": steps, "event": "env_error", "error": str(ex)[:120]})
            print(f"[{steps}] env error {ex}", flush=True)
            continue
        g_new = res.frame
        actual = diff_cells(g_prev, g_new)
        rec = {"step": steps, "action": action, "actual_n": len(actual),
               "actual_sample": actual[:8]}
        if cond == "gate":
            if claims:
                hit = sum(1 for (r, c, aft) in claims
                          if any(r == ar and c == ac and aft == aa for ar, ac, aa in actual))
                prec = hit / len(claims)
                precisions.append(prec)
                verdict = "PASS" if prec >= 0.5 else "REFUTED"
                if verdict == "REFUTED":
                    refuted += 1
                rec.update({"claims": claims, "precision": round(prec, 3),
                            "verdict": verdict})
                evidence = (f"上轮反馈：你的预测命中率 {prec:.0%}（{hit}/{len(claims)}）。"
                            f"实际变化的格子（行,列,变为色号）：" +
                            str(actual[:10]) + "。请修正你的世界模型。")
            else:
                rec.update({"claims": [], "verdict": "NO_CLAIMS"})
        levels_now = getattr(res, "levels_completed", 0) or 0
        rec.update({"levels_completed": levels_now, "win": bool(getattr(res, "win_levels", 0))})
        f_log(rec)
        steps += 1
        done = bool(getattr(res, "win_levels", 0)) and levels_now >= 7
        print(f"[{steps}] {action} actual={len(actual)} "
              f"{'PREC %.0f%% %s' % (precisions[-1]*100, verdict) if cond == 'gate' and claims else ''} "
              f"levels={levels_now}", flush=True)
        if done:
            print("GAME WON", flush=True)
            break
        g_prev = res.frame
        avail = getattr(res, "available_actions", None) or avail
    sc = arc.get_scorecard()
    final = {"condition": cond, "steps": steps, "mean_precision": (
        round(sum(precisions)/len(precisions), 3) if precisions else None),
        "refuted": refuted, "scorecard": sc}
    f_log(final)
    json.dump(final, open(f"p270_{cond}_final.json", "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in final.items() if k != "scorecard"}, indent=1))

if __name__ == "__main__":
    main()
