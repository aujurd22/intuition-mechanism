"""auto_scan_loop: the self-driving generalization cycle (P151).

Cycle per queued candidate domain:
  1. batch probe (cheap, one call)          — lower bound only (P150 rule)
  2. if batch shows ANY signal (< ceiling): single-turn confirm (2 seeds)
  3. single-turn gain >= 15pp               -> build pack + mechanical gate
  4. write report; never re-probe a domain with status != "queued"

State: scan_queue.json (candidates) -> packs/ (authority) ->
p151_scan_log.json (append-only log).  Key handling: ARK_API_KEY env or
~/.intuition/ark_key file (never committed, never in the task XML).

Run:  py -3 auto_scan_loop.py            (one full cycle, then exit)
      py -3 auto_scan_loop.py --watch    (cycle every SCAN_INTERVAL_MIN)
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(ROOT, "scan_queue.json")
LOG = os.path.join(ROOT, "p151_scan_log.json")
KEY_FILE = os.path.expanduser("~/.intuition/ark_key")


def load_key():
    if os.environ.get("ARK_API_KEY"):
        return os.environ["ARK_API_KEY"]
    if os.path.exists(KEY_FILE):
        return open(KEY_FILE, encoding="utf-8").read().strip()
    return None


import llm_client  # noqa: E402  (imported after ARK key setup)


def probe_batch(items, pool, llm):
    import re
    lines = ["Calibration exemplars (execution-verified):"]
    for e in pool[:2]:
        lines.append(f"CODE:\n{e['code']}\nTESTS:\n{e['test']}\n"
                     f"VERDICT: {'PASS' if e['passes'] else 'FAIL'}")
    for i, it in enumerate(items, 1):
        lines.append(f"--- Candidate {i} ---\nCODE:\n{it['code']}\n"
                     f"TESTS:\n{it['test']}")
    lines.append("\nAnswer exactly one line per candidate, in order: "
                 "'<i>: PASS' or '<i>: FAIL'.")
    ans = llm_client.ask_chat("\n".join(lines), max_tokens=3000)
    m = {}
    for mm in re.finditer(r"(\d+)\s*[:\-]\s*(PASS|FAIL)", ans, re.I):
        m[int(mm.group(1))] = mm.group(2).upper() == "PASS"
    truth = [it["passes"] for it in items]
    preds = [m.get(i) for i in range(1, len(items) + 1)]
    if any(p is None for p in preds):
        return None
    return round(100 * sum(int(p == t) for p, t in zip(preds, truth))
                 / len(truth), 1)


def probe_single(items, pool, llm, seeds=2):
    import re
    import random
    accs = []
    rng0 = random.Random(151)
    for seed in range(seeds):
        rr = random.Random(seed * 97 + 13)
        correct = 0
        n = 0
        for it in items:
            pool_k = pool[:]
            rng0.shuffle(pool_k)
            lines = ["Calibration exemplars (execution-verified):"]
            for e in pool_k[:1]:
                lines.append(f"CODE:\n{e['code']}\nTESTS:\n{e['test']}\n"
                             f"VERDICT: {'PASS' if e['passes'] else 'FAIL'}")
            lines.append(f"CODE:\n{it['code']}\nTESTS:\n{it['test']}")
            lines.append("Answer exactly one line: 'VERDICT: PASS' or "
                         "'VERDICT: FAIL'.")
            pred = None
            for _ in range(2):
                ans = llm_client.ask_chat("\n".join(lines), max_tokens=512)
                mm = re.search(r"VERDICT:\s*(PASS|FAIL)", ans, re.I)
                if mm:
                    pred = mm.group(1).upper() == "PASS"
                    break
            if pred is None:
                continue
            n += 1
            correct += int(pred == it["passes"])
        accs.append(round(100 * correct / max(n, 1), 1))
    return round(sum(accs) / len(accs), 1), accs


def run_cycle():
    key = load_key()
    if not key:
        print("no ARK key (env or ~/.intuition/ark_key) — cycle skipped")
        return
    os.environ["ARK_API_KEY"] = key
    sys.path.insert(0, ROOT)
    import importlib
    import llm_client
    importlib.reload(llm_client)

    q = json.load(open(QUEUE, encoding="utf-8")) if os.path.exists(QUEUE) \
        else {"domains": []}
    log = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else []
    from intuition_pack.pack import build_pack
    from intuition_pack.store import get_store
    from intuition_pack.verifiers import run_verifier
    store = get_store()

    changed = False
    for dom in q["domains"]:
        if dom.get("status", "queued") != "queued":
            continue
        name = dom["domain"]
        items = dom["items"]
        pool = [it for it in items][:2]
        entry = {"domain": name, "ts": time.strftime("%Y-%m-%d %H:%M")}
        batch = probe_batch(items, pool, llm_client)
        entry["batch_acc"] = batch
        if batch is None or batch >= 95:
            # P150 rule: batch >= ceiling is only a LOWER bound signal —
            # a batch at ceiling still needs single-turn to claim it.
            st, st_seeds = probe_single(items, pool, llm_client)
            entry["single_turn"] = st_seeds
            if st >= 95:
                entry["verdict"] = "SATURATED"
                dom["status"] = "saturated"
                log.append(entry)
                print(f"{name}: batch {batch} / single {st_seeds} -> SATURATED")
                changed = True
                continue
        st, st_seeds = probe_single(items, pool, llm_client)
        entry["single_turn"] = st_seeds
        gain = round(st - (batch or 0), 1)
        entry["single_gain"] = gain
        if gain >= 15 and st >= 90:
            pack = build_pack(name, dom.get("charter", "Judge whether the "
                              "CODE passes the TESTS (exactly). Confirm "
                              "with the pytest_check verifier."),
                              [{"d": it["id"], "inputs": {"code": it["code"],
                                                          "test": it["test"]},
                                "label": "PASS" if it["passes"] else "FAIL",
                                "note": "execution-verified"}
                               for it in items],
                              {"name": "pytest_check",
                               "rule": "execution: exit 0 => PASS"},
                              source="P151 auto_scan")
            version = store.put(name, pack.to_json())
            # mechanical gate
            gate_ok = all(
                run_verifier("pytest_check", {"code": it["code"],
                                              "test": it["test"]})["verdict"]
                == ("PASS" if it["passes"] else "FAIL")
                for it in items)
            entry.update({"verdict": "COMPRESSION -> PACK BUILT",
                          "pack_version": version, "gate_ok": gate_ok})
            dom["status"] = "built"
            print(f"{name}: single gain {gain} -> PACK BUILT v{version} "
                  f"(gate {'OK' if gate_ok else 'FAIL'})")
        else:
            entry["verdict"] = "NO COMPRESSION (no build)"
            dom["status"] = "no-build"
            print(f"{name}: single gain {gain} -> no build")
        log.append(entry)
        changed = True

    if changed:
        json.dump(q, open(QUEUE, "w", encoding="utf-8"), indent=1,
                  ensure_ascii=False)
        json.dump(log, open(LOG, "w", encoding="utf-8"), indent=1,
                  ensure_ascii=False)
        print("log + queue updated")


if __name__ == "__main__":
    if "--watch" in sys.argv:
        interval = int(os.environ.get("SCAN_INTERVAL_MIN", "720")) * 60
        while True:
            run_cycle()
            time.sleep(interval)
    else:
        run_cycle()
