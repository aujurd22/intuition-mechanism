# -*- coding: utf-8 -*-
"""Operator helpers: the conversation model drives the daemon through these.
  send(cmd)              write command, wait for out, return parsed result
  state()                current compact state
"""
import json, os, time

ROOT = os.path.dirname(os.path.abspath(__file__))
CMD = os.path.join(ROOT, "p282_cmd.json")
OUT = os.path.join(ROOT, "p282_out.json")

def send(cmd, timeout=30):
    if os.path.exists(CMD):
        os.remove(CMD)
    with open(CMD, "w", encoding="utf-8") as f:
        json.dump(cmd, f, ensure_ascii=False)
    t0 = time.time()
    while time.time() - t0 < timeout:
        if os.path.exists(OUT):
            try:
                d = json.load(open(OUT, encoding="utf-8"))
                os.remove(OUT)
                return d
            except Exception:
                time.sleep(0.1)
        time.sleep(0.15)
    return {"timeout": True}

def state():
    return send({"cmd": "state"})

def act(action, claims=None, subgoal="", mode="compact", state_seen=None):
    return send({"cmd": "act", "action": action, "claims": claims or [],
                 "subgoal": subgoal, "mode": mode,
                 "state_seen": state_seen or []})
