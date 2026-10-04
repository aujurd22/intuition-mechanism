"""P144: dataset-aligned comparison with the Jev paper — the contrast pack
on Jev's OWN text-classification datasets (IMDB, AG News).

Protocol mirrors the Jev evaluation shape (zero-shot typed classification,
no generation) with our A/B conditions:
  A  bare zero-shot (no pack)
  B  contrast pack: 8-16 labeled exemplars in the prompt (the P138 payload)
Jev reference numbers from arXiv 2609.37647: IMDB 96.5%, SST-2 96.4%,
Emotion 58.5% — text-classification family.
"""
import sys, os, json, csv, random, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
from llm_client import ask_chat

AG_LABELS = {1: "World", 2: "Sports", 3: "Business", 4: "Sci/Tech"}
IMDB_LABELS = {"positive": "POSITIVE", "negative": "NEGATIVE"}


def load_agnews(n_per_class=50, seed=20261001):
    rows = list(csv.reader(open("_agnews_train.csv", encoding="utf-8")))
    by = {1: [], 2: [], 3: [], 4: []}
    for r in rows[1:]:
        c = int(r[0])
        text = (r[1] + " " + r[2].replace("\\", " ")).strip()[:300]
        if text:
            by[c].append(text)
    rng = random.Random(seed)
    test, pack = [], []
    for c, items in by.items():
        rng.shuffle(items)
        pack.extend([(items[i], AG_LABELS[c]) for i in range(4)])
        test.extend([(items[4 + i], AG_LABELS[c]) for i in range(n_per_class)])
    rng.shuffle(test)
    return test, pack


def load_imdb(n_per_class=100, seed=20261001):
    import pandas as pd
    df = pd.read_csv("_imdb.csv")
    test, pack = [], []
    rng = random.Random(seed)
    for lab in ("positive", "negative"):
        sub = df[df.sentiment == lab]["review"].tolist()
        sub = [t.strip()[:600] for t in sub if len(t.strip()) > 100]
        rng.shuffle(sub)
        pack.extend([(sub[i], IMDB_LABELS[lab]) for i in range(8)])
        test.extend([(sub[8 + i], IMDB_LABELS[lab]) for i in range(n_per_class)])
    rng.shuffle(test)
    return test, pack


def prompt_zero(task, text, labels):
    return (f"Classify into one of: {', '.join(labels)}.\n\n"
            f"TEXT: {text}\n\n"
            f"Answer exactly one line: 'LABEL: <one of {', '.join(labels)}>'")


def prompt_pack(task, text, labels, pack):
    ex = "\n".join(f"  TEXT: {t[:220]}\n  LABEL: {l}" for t, l in pack)
    return (f"Calibration exemplars (verified labels):\n{ex}\n\n"
            f"Now classify the candidate. Labels: {', '.join(labels)}.\n\n"
            f"TEXT: {text}\n\n"
            f"Answer exactly one line: 'LABEL: <one of {', '.join(labels)}>'")


def run_model(model, dataset, test, pack, labels, n=None):
    os.environ["ARK_MODEL"] = model
    import importlib
    import llm_client
    importlib.reload(llm_client)
    if n:
        test = test[:n]
    res = {}
    for cond in ("A", "B"):
        correct = 0
        for text, lab in test:
            if cond == "A":
                p = prompt_zero(dataset, text, labels)
            else:
                p = prompt_pack(dataset, text, labels, pack)
            ans = llm_client.ask_chat(p, max_tokens=256)
            m = re.search(r"LABEL:\s*(.+)", ans)
            pred = m.group(1).strip().strip("'\".") if m else ""
            correct += int(pred.upper().startswith(lab.upper()[:4]))
        res[cond] = round(100 * correct / len(test), 1)
    return res


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "deepseek-v4-flash"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    out = {}
    ag_test, ag_pack = load_agnews()
    out["ag_news"] = run_model(model, "ag_news", ag_test, ag_pack,
                               list(AG_LABELS.values()), n)
    im_test, im_pack = load_imdb()
    out["imdb"] = run_model(model, "imdb", im_test, im_pack,
                            ["POSITIVE", "NEGATIVE"], n)
    json.dump(out, open(f"p144_{model}.json", "w"), indent=1)
    print(model, json.dumps(out, indent=1))
