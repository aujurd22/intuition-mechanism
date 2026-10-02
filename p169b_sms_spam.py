"""P169b: SMS Spam dataset-aligned test — the EXACT protocol of the
independent Jev video (BV1dmh66nENf): 200 sampled messages, spam/ham
classification, accuracy + confidence-gated coverage.

Conditions:
  A  zero-shot (no pack)
  B  pack: 8 labeled exemplars (4 spam / 4 ham)
  C  pack + confidence (model reports 0-100; gated at >= 95)
Models: deepseek-v4-flash, doubao-seed-2.1-lite.
Jev reference: 96.5% acc, gate(>=0.95): coverage 63%, acc 95.5%, 432ms.
"""
import sys, os, json, re, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm_client

# ---- load ----
rows = []
for line in open("_sms.txt", encoding="utf-8"):
    parts = line.rstrip("\n").split("\t", 1)
    if len(parts) == 2:
        rows.append((parts[0], parts[1]))
rng = random.Random(20261002)
rng.shuffle(rows)
spam = [r for r in rows if r[0] == "spam"]
ham = [r for r in rows if r[0] == "ham"]
pack = [(spam[i][1], "SPAM") for i in range(4)] + [(ham[i][1], "HAM") for i in range(4)]
test = [(spam[4 + i][1], "SPAM") for i in range(100)] + \
       [(ham[4 + i][1], "HAM") for i in range(100)]
rng.shuffle(test)

LABELS = "SPAM or HAM"


def prompt_a(text):
    return (f"Classify this SMS message into one of: {LABELS}.\n\n"
            f"SMS: {text[:400]}\n\n"
            "Answer exactly one line:\nLABEL: SPAM|HAM\nCONF: <0-100>")


def prompt_b(text):
    ex = "\n".join(f"SMS: {t[:250]}\nLABEL: {l}" for t, l in pack)
    return (f"Calibration exemplars (human-labeled):\n{ex}\n\n"
            f"Now classify. SMS: {text[:400]}\n\n"
            "Answer exactly one line:\nLABEL: SPAM|HAM\nCONF: <0-100>")


def run_model(model):
    os.environ["ARK_MODEL"] = model
    import importlib
    importlib.reload(llm_client)
    out = {}
    import time
    for cond, pf in (("A", prompt_a), ("B", prompt_b)):
        correct, n, confs, gated_n, gated_ok = 0, 0, [], 0, 0
        t0 = time.time()
        for text, lab in test:
            ans = llm_client.ask_chat(pf(text), max_tokens=256)
            m = re.search(r"LABEL:\s*(SPAM|HAM)", ans, re.I)
            c = re.search(r"CONF:\s*(\d+)", ans)
            pred = m.group(1).upper() if m else None
            conf = int(c.group(1)) / 100 if c else None
            if pred:
                n += 1
                correct += int(pred == lab)
                if conf is not None:
                    confs.append(conf)
                    if conf >= 0.95:
                        gated_n += 1
                        gated_ok += int(pred == lab)
        dt = (time.time() - t0) / len(test) * 1000
        out[cond] = {"acc": round(100 * correct / max(n, 1), 1),
                     "n": n,
                     "gate_coverage": round(100 * gated_n / max(n, 1), 1),
                     "gate_acc": round(100 * gated_ok / max(gated_n, 1), 1),
                     "mean_conf": round(100 * sum(confs) / max(len(confs), 1), 1),
                     "ms_per": round(dt, 0)}
        print(f"{model[:14]:>14} {cond}: {out[cond]}")
    return out


allout = {}
for model in ("deepseek-v4-flash", "doubao-seed-2.1-lite"):
    allout[model] = run_model(model)
json.dump(allout, open("p169b_sms_spam.json", "w"), indent=1)
print("saved p169b_sms_spam.json")
