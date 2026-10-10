# -*- coding: utf-8 -*-
"""P272 prototype: System-One Vocalizer — intuition generates language.

Stage 1 (mechanical, ms): route -> verify -> calibrate (existing plugins).
Stage 2 (render, seconds): glm (effort=minimal) renders the SETTLED verdict
into fluent Chinese, forbidden from adding new factual claims.

P272 testable predictions:
  P-vocal: render quality is insensitive to judgment complexity;
           introspective explanation degrades (P184).
  P-ground: every factual claim in the render traces to verifier evidence.
Run: python p272_vocalizer.py
"""
import os, sys, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intuition_pack.verifiers import run_verifier
# durable key from .env_ark (ARK_API_KEY line) before llm_client import
if not os.environ.get("ARK_API_KEY"):
    for _ln in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 ".env_ark"), encoding="utf-8"):
        _ln = _ln.strip()
        if _ln.startswith("ARK_API_KEY="):
            os.environ["ARK_API_KEY"] = _ln.split("=", 1)[1].strip()
            break
from llm_client import ask  # coding-endpoint glm-5.3-flash

def vocalize(question: str, payload: dict, lang_render: str) -> dict:
    """Stage 1 mechanical (no LLM), Stage 2 render (LLM as vocal cord)."""
    t0 = time.time()
    v = run_verifier("lambert_sixrow", {"d": int(payload["d"])})
    mech_ms = (time.time() - t0) * 1000
    verdict = v["verdict"]
    value = v.get("value")
    grounded_facts = f"机械验证器判定 d={payload['d']} 的 1/x6 值：{value}（{verdict}）"
    # stage 2: render — the model may NOT add new facts
    render_prompt = (
        f"一个机械验证器已完成判定，你只负责把它渲染成一句通顺、自然的中文。\n"
        f"判定事实：{grounded_facts}。\n"
        f"用户问题：{question}\n"
        f"用户期待的表述方式：{lang_render}\n"
        "硬性规则：只能复述上面的判定事实，禁止添加任何新的事实主张、禁止解释机制、"
        "禁止推测。一两句话即可。")
    t1 = time.time()
    language = ask(render_prompt)
    render_ms = (time.time() - t1) * 1000
    return {"question": question, "verdict": verdict, "value": str(value),
            "mechanical_ms": round(mech_ms, 2), "render_ms": round(render_ms, 1),
            "language": language.strip()[:400],
            "grounded_facts": grounded_facts}

if __name__ == "__main__":
    demos = [
        ("d=5 是不是那个著名的 landing row？", {"d": 5}, "直接、口语化"),
        ("d=3 呢？", {"d": 3}, "极简，一个词加数字"),
        ("d=978 是 landing 吗？", {"d": 978}, "诚实说明机器不确定"),
        ("d=11 呢？", {"d": 11}, "直接、口语化"),
    ]
    out = []
    for q, pl, style in demos:
        r = vocalize(q, pl, style)
        out.append(r)
        print(f"Q: {q}\n  [mechanical {r['mechanical_ms']}ms -> {r['verdict']} "
              f"(value {r['value']})]\n  [render {r['render_ms']}ms]\n"
              f"  A: {r['language']}\n", flush=True)
    json.dump(out, open("p272_vocalizer_demo.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("saved p272_vocalizer_demo.json")
