# -*- coding: utf-8 -*-
"""P282-mech: the mechanical pipeline WITHOUT any LLM — processor + scripted
actions + toll-booth gate. Validates: compact state extraction, refs, gate
precision on scripted (correct) claims, token counts, latency.
Run: python p282_mech.py
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p282_fastuse import serve, process, parse_state, gate, screenshot

def main():
    from playwright.sync_api import sync_playwright
    logf = open("p282_mech.jsonl", "w", encoding="utf-8")
    flog = lambda o: (logf.write(json.dumps(o, ensure_ascii=False) + "\n"),
                      logf.flush())
    results = {"steps": 0, "state_tokens": 0, "gate_precisions": [],
               "latencies_ms": [], "fail": []}
    httpd = serve()
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1024, "height": 768})
        pg.goto("http://127.0.0.1:8777/index.html")

        def step(action, claims, note=""):
            """processor -> action -> gate. Every step through the pipeline."""
            t0 = time.time()
            state_lines, body = process(pg)
            st_tokens = sum(len(l) for l in state_lines) // 4
            results["state_tokens"] += st_tokens
            els = parse_state(state_lines)
            # dispatch by finding the element whose name matches
            kind = action["action"]
            done = False
            if kind == "fill":
                cands = [r for r, e in els.items()
                         if e["tag"] in ("input", "textarea")
                         and "checkbox" not in e["extra"]
                         and ('value=""' in e["extra"])]
                ok = err = None
                if cands:
                    ok = pg.fill(f'[data-ref="{cands[0]}"]', action["text"]) is None
                else:
                    ok, err = False, "no empty box"
            elif kind == "check":
                cands = [r for r, e in els.items() if e["name"] == action["name"]
                         and "[unchecked]" in e["extra"]]
                if cands:
                    pg.check(f'[data-ref="{cands[0]}"]')
                    ok = True
                else:
                    ok, err = False, "target not found"
            elif kind == "select":
                sel = [r for r, e in els.items() if e["tag"] == "select"]
                if sel:
                    pg.select_option(f'[data-ref="{sel[0]}"]', action["value"])
                    ok = True
                else:
                    ok, err = False, "no select"
            elif kind == "click":
                cands = [r for r, e in els.items()
                         if action["name"].lower() in
                         (e["name"] + " " + e["extra"]).lower()
                         and e["tag"] in ("button", "a")]
                if cands:
                    pg.click(f'[data-ref="{cands[0]}"]')
                    ok = True
                else:
                    ok, err = False, "button not found"
            else:
                ok, err = False, "unknown"
            time.sleep(0.25)
            prec, hits, misses = gate(claims, pg)
            results["gate_precisions"].append(prec)
            lat = round((time.time() - t0) * 1000)
            results["latencies_ms"].append(lat)
            results["steps"] += 1
            flog({"step": results["steps"], "action": action, "note": note,
                  "state_tokens": st_tokens, "gate_prec": prec,
                  "latency_ms": lat, "ok": ok})
            print(f"[{results['steps']:02d}] {note:24s} gate={prec} "
                  f"state={st_tokens}tok {lat}ms "
                  f"{('ERR: ' + str(err)) if not ok else ''}", flush=True)
            if not ok:
                results["fail"].append(note)

        # ---- sub-goal 1: login (3 steps) ----
        step({"action": "fill", "text": "admin"},
             ["欢迎回来"], "reflex-fill username=admin")
        step({"action": "fill", "text": "admin123"},
             ["欢迎回来"], "reflex-fill password=admin123")
        step({"action": "click", "name": "登录"},
             ["欢迎回来"], "click 登录")
        # ---- sub-goal 2: checks (4 steps) ----
        step({"action": "click", "name": "复选框任务"}, ["复选框任务"], "nav→checks")
        step({"action": "check", "name": "alpha"}, ["提交"], "check alpha")
        step({"action": "check", "name": "delta"}, ["提交"], "check delta")
        step({"action": "click", "name": "提交"}, ["CHECKS PASS"], "submit checks")
        # ---- sub-goal 3: form (3 steps) ----
        step({"action": "click", "name": "表单任务"}, ["表单任务"], "nav→form")
        step({"action": "select", "value": "high"}, ["提交表单"], "select High")
        step({"action": "fill", "text": "incident-42"},
             ["提交表单"], "fill incident-42")
        step({"action": "click", "name": "提交表单"}, ["FORM PASS"], "submit form")
        # ---- sub-goal 4: report (2 steps) ----
        step({"action": "click", "name": "报表任务"}, ["报表任务"], "nav→report")
        step({"action": "click", "name": "Vega"},
             ["REPORT PASS"], "click Vega (93, max)")
        # ---- final banner check ----
        body = pg.evaluate("document.body.innerText")
        results["workflow_complete"] = "ALL TASKS COMPLETE" in body
        b.close()
    httpd.shutdown()
    logf.close()
    gp = results["gate_precisions"]
    results["gate_mean_prec"] = round(sum(gp) / len(gp), 3)
    results["state_tokens_mean"] = round(
        results["state_tokens"] / results["steps"], 1)
    json.dump(results, open("p282_mech_final.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in results.items() if k != "fail"},
                     indent=1, ensure_ascii=False))
    print("WORKFLOW:", "COMPLETE" if results["workflow_complete"] else "INCOMPLETE")

if __name__ == "__main__":
    main()
