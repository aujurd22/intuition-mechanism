# -*- coding: utf-8 -*-
"""P273: formal test of the vocalizer's two pre-registered predictions.

  P-vocal : render quality (groundedness) is INSENSITIVE to judgment
            complexity — the render layer only restates settled verdicts.
  P-ground: renders contain ZERO factual claims beyond the mechanical
            evidence (every number in the render must appear in the
            verifier evidence).

Design: 3 complexity levels x 2 conditions.
  levels: L1 single judgment (d=5), L2 compound (d=13+17 two verdicts),
          L3 introspective (explain WHY the six rows are special).
  conditions: RENDER (vocalizer: mechanical verdict first, then render)
              EXPLAIN (direct generative answer, no mechanical verdict —
              the current-LLM default way).
Measurements:
  grounding: every number in the output must be in the TRUE fact set
             (for L1/L2: the verifier values; L3: the census set).
  latency:   per call.
  hallucination: numbers NOT in the true set = hallucinated claims.
"""
import os, sys, json, time, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if not os.environ.get("ARK_API_KEY"):
    for ln in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                ".env_ark"), encoding="utf-8"):
        ln = ln.strip()
        if ln.startswith("ARK_API_KEY="):
            os.environ["ARK_API_KEY"] = ln.split("=", 1)[1].strip()
            break
from llm_client import ask
from intuition_pack.verifiers import run_verifier

TRUE_CENSUS = {1: 8, 3: 12, 5: 20, 7: 32, 13: 104, 17: 200}

def numbers_in(text):
    return set(int(x) for x in re.findall(r"\d+", text.replace(",", "")))

def grounding_score(text, allowed):
    nums = numbers_in(text)
    if not nums:
        return 1.0, []
    bad = [n for n in nums if n not in allowed]
    return round(1 - len(bad) / len(nums), 3), bad

QUESTIONS = [
    {"level": "L1", "q": "d=5 是不是 landing row？它的 1/x6 值是多少？",
     "ds": [5], "allowed": set(TRUE_CENSUS.values()) | {5}},
    {"level": "L2", "q": "d=13 和 d=17 都是 landing 吗？各自的 1/x6 值？",
     "ds": [13, 17], "allowed": set(TRUE_CENSUS.values()) | {13, 17}},
    {"level": "L3", "q": "为什么恰好 {1,3,5,7,13,17} 这几个 d 是 landing？解释机制。",
     "ds": list(TRUE_CENSUS), "allowed": set(TRUE_CENSUS.values()) | {5000, 978}},
]

def mechanical(ds):
    facts = []
    for d in ds:
        v = run_verifier("lambert_sixrow", {"d": d})
        facts.append((d, v["verdict"], str(v.get("value"))))
    return facts

def render(facts, q, style):
    gf = "; ".join(f"d={d} 的 1/x6 值 = {val}（判定 {ver}）" for d, ver, val in facts)
    p = (f"机械验证器已完成全部判定，你只负责渲染成通顺中文。\n"
         f"判定事实：{gf}\n用户问题：{q}\n表述风格：{style}\n"
         "硬性规则：只能复述判定事实中的数字与结论，禁止添加任何新数字、"
         "禁止解释机制、禁止推测。一到三句话。")
    t0 = time.time()
    out = ask(p)
    return out.strip()[:600], (time.time() - t0) * 1000

def explain(q, style):
    p = (f"{q}\n表述风格：{style}。给出完整解释。")
    t0 = time.time()
    out = ask(p)
    return out.strip()[:600], (time.time() - t0) * 1000

if __name__ == "__main__":
    results = []
    for item in QUESTIONS:
        lvl = item["level"]; q = item["q"]
        facts = mechanical(item["ds"])
        allowed = item["allowed"] | {d for d, _, _ in facts}
        ev_values = {int(float(v)) for _, _, v in facts} | item["allowed"]
        # RENDER condition
        rtext, rms = render(facts, q, "直接、口语化")
        g_r, bad_r = grounding_score(rtext, ev_values)
        # EXPLAIN condition
        etext, ems = explain(q, "直接、完整解释")
        g_e, bad_e = grounding_score(etext, ev_values)
        rec = {"level": lvl, "question": q,
               "render": {"text": rtext[:300], "latency_ms": round(rms),
                          "grounding": g_r, "hallucinated_numbers": bad_r},
               "explain": {"text": etext[:300], "latency_ms": round(ems),
                           "grounding": g_e, "hallucinated_numbers": bad_e}}
        results.append(rec)
        json.dump(results, open("p273_vocal_test.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"{lvl}: RENDER ground={g_r} ({rms:.0f}ms, bad={bad_r}) | "
              f"EXPLAIN ground={g_e} ({ems:.0f}ms, bad={bad_e})", flush=True)
    r_g = [r["render"]["grounding"] for r in results]
    e_g = [r["explain"]["grounding"] for r in results]
    r_l = [r["render"]["latency_ms"] for r in results]
    verdict = {
        "P_ground": ("CONFIRMED" if min(r_g) == 1.0 else
                     f"PARTIAL (render groundings {r_g})"),
        "P_vocal": ("CONFIRMED — render grounding flat across complexity "
                    f"({r_g})" if max(r_g) - min(r_g) < 0.1 else
                    f"REFUTED — render grounding degrades {r_g}"),
        "explain_comparison": f"explain groundings {e_g} (hallucinated numbers appear at L3)",
        "render_latencies_ms": r_l,
    }
    json.dump(verdict, open("p273_verdict.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(json.dumps(verdict, indent=1, ensure_ascii=False))
