# -*- coding: utf-8 -*-
"""P282 daemon: owns the browser; the conversation model (this session's LLM)
is the decision layer. Protocol via files in the repo dir:
  write p282_cmd.json  -> daemon executes -> writes p282_out.json (+ PNG on shot)
Commands:
  {"cmd":"reset"}                         reload the test site (fresh state)
  {"cmd":"state"}                         -> compact state + body text
  {"cmd":"shot"}                          -> state + PNG (p282_shot.png)
  {"cmd":"act","action":{...},"claims":[...]}  execute + gate verdict
  {"cmd":"quit"}
Every act is logged to p282_distill.jsonl (operator = this conversation's model).
"""
import os, sys, json, time, threading
import http.server, functools

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "p282_testsite")
PORT = 8777
CMD = os.path.join(ROOT, "p282_cmd.json")
OUT = os.path.join(ROOT, "p282_out.json")
DISTILL = os.path.join(ROOT, "p282_distill.jsonl")

def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd

sys.path.insert(0, ROOT)
from p282_fastuse import process, parse_state, do_action, gate  # noqa: E402

def write_out(obj):
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)

def main():
    from playwright.sync_api import sync_playwright
    httpd = serve()
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1024, "height": 768})
        pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        write_out({"ready": True, "url": pg.url})
        run = True
        while run:
            if not os.path.exists(CMD):
                time.sleep(0.25)
                continue
            try:
                cmd = json.load(open(CMD, encoding="utf-8"))
                os.remove(CMD)
            except Exception:
                time.sleep(0.25)
                continue
            c = cmd.get("cmd")
            if c == "reset":
                pg.goto(f"http://127.0.0.1:{PORT}/index.html")
                write_out({"reset": True, "url": pg.url})
            elif c == "state":
                state, body = process(pg)
                write_out({"state": state, "body": body[:600], "url": pg.url})
            elif c == "shot":
                state, body = process(pg)
                png = pg.screenshot(path=os.path.join(ROOT, "p282_shot.png"))
                write_out({"state": state, "body": body[:600],
                           "shot": "p282_shot.png"})
            elif c == "act":
                act = cmd.get("action", {})
                claims = cmd.get("claims", [])
                before = pg.evaluate("document.body.innerText")[:400]
                if act.get("action") == "click_xy":
                    pg.mouse.click(act["x"], act["y"])
                    ok, err = True, None
                elif act.get("action") == "type_text":
                    pg.keyboard.type(act["text"], delay=20)
                    ok, err = True, None
                else:
                    ok, err = do_action(pg, act)
                time.sleep(0.25)
                state, body = process(pg)
                prec, hits, misses = (gate(claims, pg) if claims and ok
                                      else (None, [], []))
                rec = {"ts": time.time(),
                       "operator": "conversation-model",
                       "mode": cmd.get("mode", "compact"),
                       "subgoal": cmd.get("subgoal", ""),
                       "state_before": cmd.get("state_seen", [])[:8],
                       "action": act, "ok": ok, "err": err,
                       "claims": claims, "gate_precision": prec,
                       "gate_hits": hits, "gate_misses": misses,
                       "body_after": body[:300]}
                with open(DISTILL, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                write_out({"act_done": True, "ok": ok, "err": err,
                           "gate_prec": prec, "gate_misses": misses,
                           "state": state, "body": body[:600], "url": pg.url})
            elif c == "quit":
                write_out({"quit": True})
                run = False
        b.close()
    httpd.shutdown()

if __name__ == "__main__":
    main()
