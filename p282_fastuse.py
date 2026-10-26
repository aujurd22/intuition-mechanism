# -*- coding: utf-8 -*-
"""P282: Fast Computer Use MVP — fly-style two-tier browser agent.

Architecture (P281 design, browser domain):
  tier 0 processor (mechanical, ms): DOM -> compact labeled state (~tokens/10)
  tier 1 reflex     (0 LLM call):    unambiguous single-match fills
  tier 2 click LLM  (1 call, glm):   ambiguous actions + prediction claims
  tier 3 gate       (mechanical):    claims verified vs actual DOM text,
                                     REFUTED evidence fed back
Benchmark: local test site, 4 sub-goals (login / checks / form / report).
Paired modes: compact (DOM state) vs screenshot (png vision).
"""
import os, sys, json, time, base64, io as _io, re, threading
import http.server, functools, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "p282_testsite")
PORT = 8777

def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd

ARK_URL = "https://ark.cn-beijing.volces.com/api/coding/v3/responses"
KEY = [ln.split("=", 1)[1].strip() for ln in
       open(os.path.join(ROOT, ".env_ark"), encoding="utf-8")
       if ln.startswith("ARK_API_KEY=")][0]

def glm(state_prompt, image_b64=None):
    content = []
    if image_b64:
        content.append({"type": "input_image", "image_url":
                        f"data:image/png;base64,{image_b64}"})
    content.append({"type": "input_text", "text": state_prompt})
    body = {"model": "glm-5.3-flash", "reasoning": {"effort": "minimal"},
            "input": [{"role": "user", "content": content}]}
    req = urllib.request.Request(ARK_URL, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {KEY}"})
    t0 = time.time()
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    txt = r.get("output_text") or "".join(
        c.get("text", "") for o in r.get("output", [])
        for c in o.get("content", []) if isinstance(c, dict))
    return txt.strip(), (time.time() - t0) * 1000

INJECT_JS = """
() => {
  const els = document.querySelectorAll(
    'button, input, select, textarea, a[href], [onclick]');
  let i = 0;
  document.querySelectorAll('[data-ref]').forEach(e => e.removeAttribute('data-ref'));
  const out = [];
  for (const e of els) {
    const r = e.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    if (e.offsetParent === null && e.type !== 'hidden') continue;
    const ref = 'e' + (++i);
    e.setAttribute('data-ref', ref);
    const tag = e.tagName.toLowerCase();
    const name = ((e.innerText && e.tagName !== 'SELECT' ? e.innerText :
                  (e.tagName === 'SELECT' ?
                     (e.options[e.selectedIndex] || {}).text || '' :
                     (e.type === 'checkbox' && e.closest('label') ?
                        e.closest('label').innerText : '')) ||
                  e.placeholder || e.value ||
                  e.getAttribute('aria-label') || e.id || '')
                  .replace(/\s+/g, ' ').trim().slice(0, 40));
    let extra = '';
    if (tag === 'input') {
      if (e.type === 'checkbox') extra = e.checked ? ' [checked]' : ' [unchecked]';
      else extra = ` value="${(e.value || '').slice(0, 30)}"`;
    }
    if (tag === 'select') {
      const o = e.options[e.selectedIndex];
      extra = ` selected="${o ? o.text : ''}"`;
    }
    const rowCtx = e.closest('tr') ?
      ' [' + e.closest('tr').innerText.replace(/\s+/g, ' ').trim().slice(0, 40) + ']' : '';
    out.push(`[${ref}] ${tag} "${name}"${rowCtx}${extra}`);
    if (out.length >= 30) break;
  }
  return {state: out, body: document.body.innerText.slice(0, 600)};
}
"""

def process(page):
    d = page.evaluate(INJECT_JS)
    return d["state"], d["body"]

def parse_state(state_lines):
    els = {}
    for ln in state_lines:
        m = re.match(r"\[(e\d+)\] (\w+) \"(.*?)\"(.*)", ln)
        if m:
            els[m.group(1)] = {"tag": m.group(2), "name": m.group(3),
                               "extra": m.group(4).strip()}
    return els

def screenshot(page):
    png = page.screenshot()
    return base64.b64encode(png).decode()

def do_action(page, act):
    kind = act.get("action")
    sel = f'[data-ref="{act.get("ref", "")}"]'
    try:
        if kind == "click":
            page.click(sel, timeout=3000)
        elif kind == "fill":
            page.fill(sel, act.get("text", ""), timeout=3000)
        elif kind == "select":
            page.select_option(sel, act.get("value", ""), timeout=3000)
        elif kind == "check":
            page.check(sel, timeout=3000)
        elif kind == "go_back":
            page.go_back(timeout=5000)
            return True, None
        elif kind == "done":
            return True, None
        else:
            return False, f"unknown action {kind}"
        return True, None
    except Exception as ex:
        return False, str(ex)[:120]

def parse_action(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        a = json.loads(m.group(0))
        return a if "action" in a else None
    except Exception:
        return None

def gate(claims, page):
    if not claims:
        return None, 0, []
    body = page.evaluate("document.body.innerText")
    hits, misses = [], []
    for c in claims[:6]:
        target = str(c.get("page_contains", "")) if isinstance(c, dict) else str(c)
        if target and target in body:
            hits.append(target)
        else:
            misses.append(target)
    prec = round(len(hits) / len(claims[:6]), 3)
    return prec, hits, misses

SUBGOALS = [
    {"goal": "用 admin/admin123 登录", "done_when": "欢迎回来"},
    {"goal": "进入复选框任务，恰好勾选 alpha 和 delta，然后提交", "done_when": "CHECKS PASS"},
    {"goal": "进入表单任务，下拉选 High，填 incident-42，提交", "done_when": "FORM PASS"},
    {"goal": "进入报表任务，点击数值最大那行的选择按钮", "done_when": "REPORT PASS"},
]

def run_condition(mode, max_steps=25, run_tag="a"):
    from playwright.sync_api import sync_playwright
    logf = open(f"p282_{mode}_{run_tag}.jsonl", "w", encoding="utf-8")
    flog = lambda o: (logf.write(json.dumps(o, ensure_ascii=False) + "\n"),
                      logf.flush())
    results = {"mode": mode, "steps": 0, "llm_calls": 0, "reflex": 0,
               "state_tokens": 0, "claim_precisions": [], "refuted": 0,
               "subgoals_done": 0, "errors": [], "llm_ms": 0}
    httpd = serve()
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1024, "height": 768})
        pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        t_start = time.time()
        for sg in SUBGOALS:
            done = False
            tries = 0
            while not done and results["steps"] < max_steps and tries < 8:
                state_lines, body = process(pg)
                results["state_tokens"] += sum(len(l) for l in state_lines) // 4
                els = parse_state(state_lines)
                act, via = None, None
                # ---- tier 1 reflex: fill value named in the sub-goal ----
                fills = re.findall(r"(?:填|选)\s*([A-Za-z0-9\-]+)", sg["goal"])
                empties = [r for r, e in els.items()
                           if e["tag"] in ("input", "textarea")
                           and "checkbox" not in e["extra"]
                           and 'value=""' in e["extra"]]
                if len(empties) == 1 and fills:
                    act = {"action": "fill", "ref": empties[0], "text": fills[0]}
                    via = "reflex-fill"
                # ---- tier 2: click LLM ----
                if act is None:
                    state_txt = "\n".join(state_lines)
                    if mode == "compact":
                        p_txt = (f"你在操作一个网页。当前可交互元素：\n{state_txt}\n\n"
                                 f"当前子目标：{sg['goal']}\n\n"
                                 "选择下一个动作。严格只输出一个 JSON 对象：\n"
                                 '{"action":"click|fill|select|check|done","ref":"e数字",'
                                 '"text":"...","value":"...",'
                                 '"claims":["动作后页面应出现的文字",...]}\n'
                                 "claims 预测动作后页面会出现的文字（最多 2 条，机械核验对照）。"
                                 "子目标已完成则输出 {\"action\":\"done\"}。")
                        txt, ms = glm(p_txt)
                        act = parse_action(txt)
                    else:
                        b64 = screenshot(pg)
                        p_txt = (f"你是计算机操作智能体。屏幕截图如下。\n"
                                 f"当前子目标：{sg['goal']}\n\n"
                                 "选择下一个动作。严格只输出一个 JSON 对象：\n"
                                 '{"action":"click|fill|select|check|done",'
                                 '"selector":"CSS选择器","text":"...","value":"..."}\n'
                                 "子目标已完成则输出 {\"action\":\"done\"}。")
                        txt, ms = glm(p_txt, image_b64=b64)
                    results["llm_calls"] += 1
                    results["llm_ms"] = results.get("llm_ms", 0) + ms
                    if act is None:
                        results["errors"].append(
                            f"unparseable step {results['steps']}: {txt[:80]}")
                        tries += 1
                        continue
                else:
                    act["claims"] = []
                ok, err = do_action(pg, act)
                flog({"mode": mode, "step": results["steps"], "via": via or mode,
                      "action": act, "ok": ok, "err": err})
                if not ok:
                    results["errors"].append(f"{act.get('action')}: {err}")
                    tries += 1
                    continue
                results["steps"] += 1
                if via:
                    results["reflex"] += 1
                if act.get("claims") and mode == "compact":
                    prec, hits, misses = gate(act["claims"], pg)
                    results["claim_precisions"].append(prec)
                    if prec < 0.5:
                        results["refuted"] += 1
                    flog({"step": results["steps"], "gate": {"prec": prec,
                          "hits": hits, "misses": misses}})
                body_now = pg.evaluate("document.body.innerText")
                if sg["done_when"] in body_now:
                    results["subgoals_done"] += 1
                    done = True
                    print(f"  subgoal done ({results['steps']} steps): "
                          f"{sg['goal'][:36]}", flush=True)
            if not done:
                print(f"  subgoal exhausted: {sg['goal'][:44]}", flush=True)
        results["wall_s"] = round(time.time() - t_start, 1)
        b.close()
    httpd.shutdown()
    logf.close()
    return results

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "compact"
    budget = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    tag = sys.argv[3] if len(sys.argv) > 3 else "a"
    out = run_condition(mode, budget, tag)
    json.dump(out, open(f"p282_{mode}_final.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k != "errors"},
                     indent=1, ensure_ascii=False))
