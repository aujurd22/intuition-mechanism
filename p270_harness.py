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

def _load_key():
    k = os.environ.get("ARK_API_KEY")
    if k:
        return k
    envf = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env_ark")
    if os.path.exists(envf):
        for ln in open(envf, encoding="utf-8"):
            ln = ln.strip()
            if ln.startswith("ARK_API_KEY="):
                return ln.split("=", 1)[1].strip()
    return ""
ARK_KEY = _load_key()
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
    last = None
    for attempt in range(4):
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=600).read())
            break
        except Exception as ex:
            last = ex
            if attempt == 3:
                raise
            import time as _t
            _t.sleep([5, 15, 30][attempt])
    else:
        raise RuntimeError("unreachable")
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
    im = im.resize((384, 384), Image.NEAREST)
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

def spend_rows_low_yield(logfile, k):
    """Last k recorded steps that were all low-yield (actual_n < 20)?"""
    try:
        rows = [json.loads(l) for l in open(logfile, encoding="utf-8")]
    except (OSError, ValueError):
        return []
    tail = [r for r in rows if "actual_n" in r][-k:]
    if len(tail) < k:
        return []
    return [r for r in tail if r.get("actual_n", 0) < 20]


def main():
    cond = sys.argv[1] if len(sys.argv) > 1 else "gate"
    max_actions = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    game = sys.argv[3] if len(sys.argv) > 3 else "ls20"
    logfile = f"p270_{cond}_{game}.jsonl"
    logf = open(logfile, "w", encoding="utf-8", buffering=1)  # line-buffered: survives SIGKILL

    arc = arc_agi.Arcade()
    env = arc.make(game)
    obs = env.reset()
    g_prev = obs.frame
    avail = list(obs.available_actions or [1, 2, 3, 4])
    levels_start = 0
    steps = 0
    precisions = []
    refuted = 0
    evidence = ""
    action = None  # pack arm may set it before the GLM block; gate arm starts fresh
    f_log = lambda o: logf.write(json.dumps(o, ensure_ascii=False, default=str) + "\n") or logf.flush()

    while steps < max_actions:
        grid_png = render_png(g_prev)
        if cond in ("pack", "hybrid"):
            # pack/hybrid arms: the intuition-pack ranks the available
            # actions from past (action -> actual diff) experience; GLM
            # is only consulted when the pack abstains (hybrid: or for
            # claims refinement on a confident action).
            from intuition_pack.server import get_store
            import json as _j
            try:
                pack = _j.loads(get_store().get(f"arc-action-{game}"))
            except Exception:
                pack = None
            counts = {}
            for e in (pack or {}).get("exemplars", []):
                a = e["inputs"].get("action")
                lab = e.get("label")
                if a:
                    c = counts.setdefault(a, {"R": 0, "N": 0})
                    c["R" if lab == "RATIONAL" else "N"] += 1
            def _score(a):
                c = counts.get(a)
                if not c or (c["R"] + c["N"]) < 2:
                    return None  # ABSTAIN: not enough evidence
                return c["R"] / (c["R"] + c["N"])
            scored = [(a, _score(ACTIONS[a - 1])) for a in avail]
            # staleness (v15.1 fix for the ACTION4 lock-in): if the last
            # K steps produced no level progress, treat ALL evidence as
            # stale — game state changed, so old confidences no longer
            # apply. Reset by filtering exemplars to recent ones only.
            K = 6
            recent_low_yield = len(spend_rows_low_yield(logfile, K))
            filter_recent = recent_low_yield >= K
            if filter_recent:
                kept = [e for e in (pack or {}).get("exemplars", [])
                        if e["inputs"].get("step", 0) >= steps - K]
                counts = {}
                for e in kept:
                    a = e["inputs"].get("action")
                    lab = e.get("label")
                    if a:
                        c = counts.setdefault(a, {"R": 0, "N": 0})
                        c["R" if lab == "RATIONAL" else "N"] += 1
                def _score(a):
                    c = counts.get(a)
                    if not c or (c["R"] + c["N"]) < 2:
                        return None
                    return c["R"] / (c["R"] + c["N"])
                # all actions become partially unknown again; try the
                # least-recently-tried first
                scored = [(a, _score(ACTIONS[a - 1])) for a in avail]
            unknown = [a for a, s in scored if s is None]
            # least-evidence first: order unknowns by times tried this
            # run (tracked in f_log rows), so a dead action stops
            # being retried before other unknowns
            tried = {}
            try:
                for line in open(logfile, encoding="utf-8"):
                    rj = json.loads(line)
                    a = rj.get("action")
                    if a:
                        tried[a] = tried.get(a, 0) + 1
            except (OSError, ValueError):
                pass
            unknown.sort(key=lambda a: tried.get(ACTIONS[a - 1], 0))
            confident = [(a, s) for a, s in scored
                         if s is not None and s >= 0.6]
            if unknown:
                # exploration: an untested action is the most informative
                # choice — the pack knows nothing about it yet
                action, claims = ACTIONS[unknown[0] - 1], []
                print(f"[{steps}] PACK explore {action} (no evidence)",
                      flush=True)
            elif confident:
                confident.sort(key=lambda t: -t[1])
                action, claims = ACTIONS[confident[0][0] - 1], []
                print(f"[{steps}] PACK choose {action} "
                      f"conf={confident[0][1]:.2f}", flush=True)
                if cond == "hybrid":
                    # hybrid arm: pack locked a confident action, but
                    # GLM still adds claims refinement on top (the
                    # claims are verified by the toll booth as usual)
                    prompt = ("你在玩一个 64x64 的格子游戏。这是当前帧。可用动作: "
                              + ",".join(ACTIONS[i-1] for i in avail) + "。\n"
                              f"已选动作: {action}。请预测这个动作会导致哪些格子"
                              "发生变化（最多 8 个，每个给行列和变化后色号）。"
                              + (evidence or ""))
                    js_h = ('严格只输出一个 JSON 对象：{"action":"' + action
                            + '","claims":[{"r":行,"c":列,"after":色号}]}')
                    try:
                        resp = glm_vision(prompt + "\n" + js_h + "\n当前帧如上。",
                                          grid_png)
                        _a, claims = parse_turn(resp, True)
                        if _a is not None and _a != action:
                            claims = []  # GLM disagreed: keep pack choice,
                            # discard unverified claims
                    except Exception as ex:
                        claims = []
                        print(f"[{steps}] hybrid GLM claims failed: "
                              f"{ex!r}"[:90], flush=True)
            else:
                print(f"[{steps}] PACK abstain -> GLM", flush=True)
        if cond in ("gate", "pack", "hybrid") and action is None:
            prompt = ("你在玩一个 64x64 的格子游戏。这是当前帧（调色板：0白 5黑 8红 9蓝 11黄 12橙，"
                      "其它数字是其它颜色）。可用动作: " + ",".join(ACTIONS[i-1] for i in avail) + "。\n"
                      "选择下一个动作，并预测这个动作会导致哪些格子发生变化（最多 8 个，"
                      "每个格子给行、列和变化后的色号）。" + (evidence or ""))
        elif cond == "nogate":
            prompt = ("你在玩一个 64x64 的格子游戏。这是当前帧。可用动作: " + ",".join(ACTIONS[i-1] for i in avail) + "。\n"
                      "选择下一个动作。")
        js = '严格只输出一个 JSON 对象：{"action":"ACTIONx"' + (
            ',"claims":[{"r":行,"c":列,"after":色号}]}' if cond == "gate" else "}")
        if cond == "pack" and action is not None:
            pass  # pack decided: skip the GLM call entirely
        elif cond == "hybrid" and action is not None:
            pass  # hybrid confident branch already ran GLM for claims
        else:
            try:
                resp = glm_vision(prompt + "\n" + js + "\n当前帧如上。", grid_png)
                action, claims = parse_turn(resp, cond == "gate")
                tries = 0
                while action is None and tries < 1:
                    resp = glm_vision(prompt + "\n\n你上次的输出无法解析。再次只输出 JSON。", grid_png)
                    action, claims = parse_turn(resp, cond == "gate")
                    tries += 1
            except Exception as ex:
                f_log({"step": steps, "event": "glm_error", "error": str(ex)[:120]})
                print(f"[{steps}] glm error, skip", flush=True)
                continue
            if action is None:
                f_log({"step": steps, "event": "unparseable", "raw": resp[:200]})
                print(f"[{steps}] unparseable, skip", flush=True)
                continue
        ai = ACTIONS.index(action) + 1
        if avail and ai not in avail:
            ai = avail[0]   # 无效动作 -> 回退到第一个可用动作
        try:
            res = env.step(ai)   # py3.13: GameAction(value) 构造有怪癖，直接传 int
        except Exception as ex:
            f_log({"step": steps, "event": "env_error", "error": str(ex)[:120]})
            print(f"[{steps}] env error {ex}", flush=True)
            continue
        g_new = res.frame
        actual = diff_cells(g_prev, g_new)
        rec = {"step": steps, "action": action, "actual_n": len(actual),
               "actual_sample": actual[:8]}
        if cond == "pack":
            # self-update: fold the fresh observation back into the pack
            # so exploration accumulates (this is the flyloop cycle:
            # experience -> memory -> prediction -> error -> update)
            try:
                from intuition_pack.pack import build_pack
                from intuition_pack.server import get_store
                lab = "RATIONAL" if len(actual) >= 20 else "NOT"
                old = json.loads(get_store().get(f"arc-action-{game}"))
                exs = old.get("exemplars", [])
                exs = [e for e in exs
                       if not (e["inputs"].get("action") == action
                               and e["inputs"].get("step", 0) >= steps)]
                exs.append(dict(d=len(exs),
                                inputs={"action": action,
                                        "actual_n": len(actual),
                                        "actual_sample": actual[:8],
                                        "step": steps},
                                label=lab,
                                note="live self-update"))
                newp = build_pack(f"arc-action-{game}", old["charter"], exs,
                                  old["verifier"], "p270 self-update")
                get_store().put(f"arc-action-{game}", newp.to_json())
            except Exception as ex2:
                print(f"[{steps}] pack self-update failed: {ex2!r}"[:100],
                      flush=True)
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
        avail = list(getattr(res, "available_actions", None) or [1, 2, 3, 4])
    sc = arc.get_scorecard()
    final = {"condition": cond, "steps": steps, "mean_precision": (
        round(sum(precisions)/len(precisions), 3) if precisions else None),
        "refuted": refuted, "scorecard": sc}
    f_log(final)
    json.dump(final, open(f"p270_{cond}_final.json", "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in final.items() if k != "scorecard"}, indent=1))

if __name__ == "__main__":
    main()
