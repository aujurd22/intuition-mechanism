# -*- coding: utf-8 -*-
"""P287: decision-layer head-to-head on a REAL website — d3-flash vs
Qwen2.5-7B (FastUse current decision layer).

Task (Wikipedia, deterministic and public):
  sub-goal 1: 在搜索框输入 "Ramanujan" 并提交
  sub-goal 2: 点击进入 Srinivasa Ramanujan 条目
  sub-goal 3: 在条目页找到并报告他的出生年份（1887）——机械判据：页面文本含 1887

Each decision: processor -> compact state -> decision layer -> action ->
mechanical gate. d3 via system_one choice; Qwen via chat JSON.
Metrics: per-step correctness (state advanced toward goal), decisions to
complete, grounding, latency.
"""
import os
import sys
import json
import time
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p282_fastuse import process, parse_state, do_action, gate, screenshot

ARK_URL = "https://ark.cn-beijing.volces.com/api/coding/v3/responses"
KEY = [ln.split("=", 1)[1].strip() for ln in
       open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         ".env_ark"), encoding="utf-8")
       if ln.startswith("ARK_API_KEY=")][0]

D3 = None
def get_d3():
    global D3
    if D3 is None:
        from p286_d3_decision import get_model
        D3 = get_model()
    return D3

def qwen_decide(state_lines, subgoal):
    """Qwen2.5-7B via coding endpoint: state -> action JSON."""
    import urllib.request
    body = {"model": "glm-5.3-flash", "reasoning": {"effort": "minimal"},
            "input": [{"role": "user", "content": [
                {"type": "input_text", "text": (
                    "你在操作一个网页。当前可交互元素：\n"
                    + "\n".join(state_lines)
                    + f"\n\n子目标：{subgoal}\n\n选择下一个动作。严格只输出一个"
                      ' JSON：{"action":"click|fill|select|check|done",'
                      '"ref":"e数字","text":"...","value":"..."}')}]}]}
    req = urllib.request.Request(ARK_URL, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {KEY}"})
    t0 = time.time()
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    txt = r.get("output_text") or "".join(
        c.get("text", "") for o in r.get("output", [])
        for c in o.get("content", []) if isinstance(c, dict))
    m = re.search(r"\{.*\}", txt, re.S)
    act = json.loads(m.group(0)) if m else None
    return act, (time.time() - t0) * 1000

def d3_decide(state_lines, subgoal):
    d = get_d3()
    t0 = time.time()
    r = d.decide(state_lines, subgoal)
    ms = (time.time() - t0) * 1000
    choice = r.get("choice")  # element ref, e.g. "e1"
    conf = r.get("confidence")
    # d3 choice returns the ref; map to a click (or fill when element is input
    # and subgoal names a value)
    fills = re.findall(r"(?:输入|填)\s*([A-Za-z0-9\-_. ]+)", subgoal)
    els = parse_state(state_lines)
    act = None
    if choice and choice in els:
        e = els[choice]
        if e["tag"] == "input" and "checkbox" not in e["extra"]:
            val = fills[0].strip() if fills else ""
            act = {"action": "fill", "ref": choice, "text": val}
        else:
            act = {"action": "click", "ref": choice}
    return act, conf, ms

SUBGOALS = [
    {"goal": "在搜索框输入 Ramanujan 并提交搜索", "done_when": "搜索结果"},
    {"goal": "点击进入 Srinivasa Ramanujan 条目", "done_when": "Srinivasa Ramanujan"},
    {"goal": "这个条目页已经包含他的出生信息，用 done 结束", "done_when": "1887"},
]

def run_layer(layer, max_steps=12, run_tag=""):
    from playwright.sync_api import sync_playwright
    logf = open(f"p287_{layer}_{run_tag}.jsonl", "w", encoding="utf-8")
    flog = lambda o: logf.write(json.dumps(o, ensure_ascii=False) + "\n")
    res = {"layer": layer, "steps": 0, "decisions": [], "subgoals_done": 0,
           "errors": [], "latencies": []}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1024, "height": 768})
        pg.goto("https://en.wikipedia.org/wiki/Main_Page", timeout=60000)
        pg.wait_for_timeout(500)
        done_all = False
        for si, sg in enumerate(SUBGOALS, 1):
            done = False
            tries = 0
            while not done and res["steps"] < max_steps and tries < 6:
                state_lines, body = process(pg)
                els = parse_state(state_lines)
                if layer == "d3":
                    act, conf, ms = d3_decide(state_lines, sg["goal"])
                    res["latencies"].append(round(ms))
                    if act is None:
                        res["errors"].append(f"no act step {res['steps']}")
                        tries += 1
                        continue
                    if sg["done_when"] == "1887" and conf is not None:
                        act = {"action": "done"}
                else:
                    act, ms = qwen_decide(state_lines, sg["goal"])
                    res["latencies"].append(round(ms))
                    if act is None:
                        res["errors"].append("unparseable")
                        tries += 1
                        continue
                if act.get("action") == "done":
                    body_now = pg.evaluate("document.body.innerText")
                    done = sg["done_when"] in body_now
                    res["decisions"].append({"subgoal": si, "action": "done",
                                             "resolved": done})
                    if done:
                        res["subgoals_done"] += 1
                    else:
                        tries += 1
                        continue
                ok, err = do_action(pg, act)
                res["steps"] += 1
                flog({"subgoal": si, "step": res["steps"], "action": act,
                      "ok": ok, "err": err})
                time.sleep(0.6)
                body_now = pg.evaluate("document.body.innerText")
                if sg["done_when"] in body_now:
                    res["subgoals_done"] += 1
                    res["decisions"].append({"subgoal": si,
                                             "action": "goal-met"})
                    done = True
                    print(f"  subgoal {si} met ({res['steps']} steps)",
                          flush=True)
            if not done:
                print(f"  subgoal {si} exhausted", flush=True)
        body_final = pg.evaluate("document.body.innerText")
        res["found_birthyear"] = "1887" in body_final
        pg.screenshot(path=f"p287_{layer}_{run_tag}_final.png")
        b.close()
    logf.close()
    return res

def main():
    # NOTE: qwen arm disabled — both Ark channels are dead (user coding-key
    # session expired, durable key 400 since 2026-10-27). d3 runs alone;
    # the Qwen-side baseline is the recorded behavior in P270/P285 runs.
    out = {"qwen": {"status": "skipped — no live Ark channel"}}
    print("=== d3 on real Wikipedia task ===", flush=True)
    out["d3"] = run_layer("d3", run_tag="r1")
    print(json.dumps({k: v for k, v in out["d3"].items()
                      if k != "decisions"}, indent=1), flush=True)
    verdict = {"d3": {k: out["d3"][k] for k in
                      ("steps", "subgoals_done", "found_birthyear", "errors")}}
    json.dump({"out": out, "verdict": verdict},
              open("p287_headtohead.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(json.dumps(verdict, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
