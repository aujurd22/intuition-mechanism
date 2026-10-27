# -*- coding: utf-8 -*-
"""FastUse — 果蝇式快计算机操作产品版（P281-P283 架构的生产实现）。

用法:
  python fastuse.py <url> "<自然语言目标>" [--budget 60] [--report out.json]
  python fastuse.py --local-site "<目标>"     使用内置测试站
  python fastuse.py <url> "<目标>" --screenshot-mode    截图配对模式

三层架构:
  规划器 (本地 7B):  自然语言目标 -> 子目标序列
  执行层  (本地 7B + 反射档):  压缩状态 -> 动作 JSON 批量 (可含预测声称)
  收费站  (机械):  每步预测声称 vs DOM 真值, REFUTED 计数, 错误入审计

决策模型: 本地 llama-server (OpenAI 兼容端点), 默认 Qwen2.5-7B-Instruct Q4_K_M。
"""
import argparse
import functools
import http.server
import json
import os
import re
import sys
import threading
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p282_fastuse import process, parse_state, do_action, gate, screenshot
from p289_borrowed import enforce_claims, validate_action, set_of_marks

CFG = {"llm_url": "http://127.0.0.1:8499/v1/chat/completions",
       "max_tokens": 300,
       "temperature": 0.2,
       "max_subgoal_tries": 4}


def llm(messages, max_tokens=None):
    body = {"model": "local",
            "messages": messages,
            "max_tokens": max_tokens or CFG["max_tokens"],
            "temperature": CFG["temperature"]}
    req = urllib.request.Request(CFG["llm_url"], data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    t0 = time.time()
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    txt = r["choices"][0]["message"]["content"].strip()
    return txt, (time.time() - t0) * 1000


PLAN_SYS = ("你是网页操作规划器。给定网页当前状态和总目标，输出完成总目标所需的"
            "全部子目标（最多 8 个，按顺序覆盖总目标的每一部分）。"
            "只输出 JSON：{\"subgoals\":[{\"goal\":\"子目标描述（含要填的具体值）\","
            "\"done_when\":\"完成后页面正文中会逐字出现的短文字\"}]}。"
            "done_when 必须是字面文本（如 \"欢迎回来\"、\"CHECKS PASS\"、"
            "\"控制台\"），不要写状态描述。")


def plan(goal, state_lines):
    usr = ("网页状态：\n" + "\n".join(state_lines)
           + f"\n\n总目标：{goal}")
    out, ms = llm([{"role": "system", "content": PLAN_SYS},
                   {"role": "user", "content": usr}], max_tokens=400)
    m = re.search(r"\{.*\}", out, re.S)
    if not m:
        return [goal], ms
    try:
        subs = json.loads(m.group(0)).get("subgoals", [])
        out_subs = []
        for s in subs[:8]:
            if isinstance(s, dict):
                out_subs.append({"goal": str(s.get("goal", "")),
                                 "done_when": str(s.get("done_when", ""))})
            else:
                out_subs.append({"goal": str(s), "done_when": ""})
        return out_subs or [{"goal": goal, "done_when": ""}], ms
    except Exception:
        return [{"goal": goal, "done_when": ""}], ms


EXEC_SYS = ("你是网页操作执行器。把网页状态和子目标转成动作 JSON 序列。"
            "只输出 JSON：{\"actions\":[{\"action\":\"click|fill|select|check|done\","
            "\"ref\":\"e数字\",\"text\":\"...\",\"value\":\"...\","
            "\"claims\":[\"该动作完成后页面正文中会逐字出现的短文字\"]}]}。"
            "claims 规则：必须是字面文本，不要写状态描述。"
            "fill 的 text 只填要输入的值本身（如 admin），"
            "不要把元素的身份标记（id=...）当值填入。"
            "示例：点击导航链接进入控制台 → claims:[\"控制台\"]；"
            "提交表单成功 → claims:[\"CHECKS PASS\"]；"
            "登录失败 → claims:[\"登录失败\"]。"
            "每个动作都必须带至少一条 claims（机械核验对照：动作后页面文本"
            "必须包含该文字）。"
            "子目标完成时最后一个动作的 action 用 done。")


def execute_actions(state_lines, subgoal):
    usr = ("网页可交互元素：\n" + "\n".join(state_lines) +
           f"\n\n子目标：{subgoal}")
    out, ms = llm([{"role": "system", "content": EXEC_SYS},
                   {"role": "user", "content": usr}])
    m = re.search(r"\{.*\}", out, re.S)
    if not m:
        return [], out, ms
    try:
        obj = json.loads(m.group(0))
        acts = obj.get("actions", [])
        if obj.get("action"):
            acts = [obj]
        return acts[:6], out, ms
    except Exception:
        return [], out, ms


def run(url, goal, budget, report_path, screenshot_mode=False, local_site=False):
    from playwright.sync_api import sync_playwright
    audit = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "fastuse_audit.jsonl"), "a", encoding="utf-8")
    flog = lambda o: audit.write(json.dumps(o, ensure_ascii=False) + "\n")

    report = {"goal": goal, "url": url,
              "started": time.strftime("%Y-%m-%d %H:%M"),
              "mode": "screenshot" if screenshot_mode else "compact",
              "steps": 0, "llm_calls": 0, "llm_ms": 0, "reflex": 0,
              "state_tokens": 0, "claim_precisions": [], "refuted": 0,
              "actions_verified": 0, "actions_unverified": 0,
              "subgoals_done": 0, "subgoals_total": 0, "errors": [],
              "subgoals": []}
    httpd = None
    if local_site:
        httpd = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 8777),
            functools.partial(http.server.SimpleHTTPRequestHandler,
                              directory=os.path.join(
                                  os.path.dirname(os.path.abspath(__file__)),
                                  "p282_testsite")))
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
    t_start = time.time()

    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1024, "height": 768})
        pg.goto(url, timeout=30000)
        pg.wait_for_timeout(400)

        # ---- 规划器 ----
        state_lines, body = process(pg)
        subgoals, pms = plan(goal, state_lines)
        report["llm_calls"] += 1
        report["llm_ms"] += pms
        report["subgoals_total"] = len(subgoals)
        print(f"规划: {len(subgoals)} 个子目标", flush=True)
        for i, s in enumerate(subgoals, 1):
            print(f"  {i}. {s}", flush=True)

        # ---- 执行 ----
        for si, sg in enumerate(subgoals, 1):
            subgoal = sg if isinstance(sg, str) else sg.get("goal", str(sg))
            done_when = (sg.get("done_when", "") if isinstance(sg, dict) else "")
            sg_status = "exhausted"
            for tries in range(CFG["max_subgoal_tries"]):
                if report["steps"] >= budget:
                    sg_status = "budget-exhausted"
                    break
                state_lines, body = process(pg)
                st_tokens = sum(len(l) for l in state_lines) // 4
                report["state_tokens"] += st_tokens
                els = parse_state(state_lines)
                acts, via = [], "llm"
                # 反射档: 唯一空框 + 子目标点名填值
                fills = re.findall(r"(?:填|输入)\s*([A-Za-z0-9\-_.]+)", subgoal)
                empties = [r for r, e in els.items()
                           if e["tag"] in ("input", "textarea")
                           and "checkbox" not in e["extra"]
                           and 'value=""' in e["extra"]]
                if len(empties) == 1 and len(fills) == 1:
                    acts = [{"action": "fill", "ref": empties[0], "text": fills[0]}]
                    via = "reflex"
                # 决策层
                if not acts:
                    if screenshot_mode:
                        b64 = screenshot(pg)
                        usr = (f"你是计算机操作智能体。屏幕截图如下。\n"
                               f"子目标：{subgoal}\n\n选择下一个动作。严格只输出"
                               '一个 JSON：{"actions":[{"action":"click|fill|select|'
                               'check|done","selector":"CSS选择器","text":"...",'
                               '"value":"..."}]}\n子目标完成则最后一步用 done。')
                        out, ms = llm([{"role": "user", "content": [
                            {"type": "input_image",
                             "image_url": f"data:image/png;base64,{b64}"},
                            {"type": "input_text", "text": usr}]}])
                    else:
                        usr = ("网页可交互元素：\n" + "\n".join(state_lines) +
                               f"\n\n子目标：{subgoal}")
                        out, ms = llm([{"role": "system", "content": EXEC_SYS},
                                       {"role": "user", "content": usr}])
                    report["llm_calls"] += 1
                    report["llm_ms"] += ms
                    n_refs = pg.evaluate(
                        "document.querySelectorAll('[data-ref]').length")
                    print(f"    [diag] refs after llm: {n_refs} | "
                          f"url={pg.url} | "
                          f"title={pg.title()[:30]}", flush=True)
                    m = re.search(r"\{.*\}", out, re.S)
                    if not m:
                        report["errors"].append(f"unparseable: {out[:80]}")
                        continue
                    try:
                        obj = json.loads(m.group(0))
                        acts = obj.get("actions", [])
                        if obj.get("action"):
                            acts = [obj]
                        acts = acts[:6]
                    except Exception:
                        report["errors"].append("json parse fail")
                        continue
                # 逐动作执行 + 收费站
                sg_done = False
                for a in acts:
                    if report["steps"] >= budget:
                        break
                    if a.get("action") == "done":
                        sg_done = True
                        break
                    # B2: claims 硬门 + B3: 结构化校验（fail-closed）
                    v_ok, v_why = validate_action(a)
                    if not v_ok:
                        report["errors"].append(f"schema: {v_why}")
                        tries += 1
                        break
                    ok_c, c_why = enforce_claims(a)
                    if not ok_c:
                        report["errors"].append(f"claims gate: {c_why}")
                        tries += 1
                        break
                    claims = a.get("claims", [])
                    ok, err = do_action(pg, a)
                    if not ok and "Timeout" in str(err):
                        refs_now = pg.evaluate(
                            "Array.from(document.querySelectorAll('[data-ref]')).map(e => e.getAttribute('data-ref')).join(',')")
                        err += f" | refs@fail: {refs_now[:80]}"
                    report["steps"] += 1
                    if via == "reflex":
                        report["reflex"] += 1
                    flog({"subgoal": si, "step": report["steps"],
                          "action": a, "ok": ok, "err": err})
                    if not ok:
                        report["errors"].append(f"{a.get('action')}: {err}")
                        continue
                    if claims:
                        prec, hits, misses = gate(claims, pg)
                        report["claim_precisions"].append(prec)
                        report["actions_verified"] += 1
                        if prec < 0.5:
                            report["refuted"] += 1
                            flog({"gate": "REFUTED", "claims": claims,
                                  "misses": misses})
                    else:
                        report["actions_unverified"] += 1
                body_now = pg.evaluate("document.body.innerText")
                if done_when and done_when in body_now:
                    sg_done = True
                if sg_done:
                    sg_status = "done"
                    break
                sg_status = "batch-ran"
                print(f"  [{si}] batch {len(acts)} actions "
                      f"@ step {report['steps']} (try {tries+1})", flush=True)

            report["subgoals"].append({"subgoal": subgoal,
                                       "done_when": done_when,
                                       "status": sg_status})
            report["subgoals_done"] += (1 if sg_status == "done" else 0)
            if sg_status != "done":
                report["errors"].append(f"subgoal {si}: {sg_status}")
            if report["steps"] >= budget:
                break

        report["wall_s"] = round(time.time() - t_start, 1)
        pg.screenshot(path=report_path.replace(".json", "_final.png"))
        b.close()
    if httpd:
        httpd.shutdown()
    audit.close()
    json.dump(report, open(report_path, "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    return report


def run_local_site(goal, budget, report_path, screenshot_mode=False):
    httpd = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 8777),
        functools.partial(http.server.SimpleHTTPRequestHandler,
                          directory=os.path.join(
                              os.path.dirname(os.path.dirname(
                                  os.path.abspath(__file__))),
                              "p282_testsite")))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        return run("http://127.0.0.1:8777/index.html", goal, budget,
                   report_path, screenshot_mode)
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="FastUse: 果蝇式快计算机操作")
    ap.add_argument("url", nargs="?", default="", help="目标网址")
    ap.add_argument("goal", help="自然语言目标")
    ap.add_argument("--budget", type=int, default=60, help="最大动作步数")
    ap.add_argument("--report", default="fastuse_report.json")
    ap.add_argument("--local-site", action="store_true", help="内置测试站")
    ap.add_argument("--screenshot-mode", action="store_true",
                    help="截图模式（配对对比用；默认压缩状态模式）")
    args = ap.parse_args()
    if not args.url and not args.local_site:
        ap.error("需要 url 或 --local-site")
    if args.local_site:
        rep = run_local_site(args.goal, args.budget, args.report,
                             args.screenshot_mode)
    else:
        rep = run(args.url, args.goal, args.budget, args.report,
                  args.screenshot_mode)
    print(json.dumps({k: v for k, v in rep.items() if k != "errors"},
                     indent=1, ensure_ascii=False))
