"""ZCode UserPromptSubmit hook: mechanical intuition-pack trigger.

stdin: hook JSON with "prompt".  If the mechanical router (route.py)
matches a registered pack domain, inject the pack's prompt_block PLUS
the mandatory-verify instruction as additionalContext — the model then
sees the calibration exemplars every turn the domain is touched,
without anyone having to phrase a request.

Discipline copied from flymemory's hook_auto.py: any exception exits 0
silently; never blocks the session.
"""
import sys, json, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    try:
        raw = sys.stdin.read()
        prompt = (json.loads(raw).get("prompt") or "") if raw.strip() else ""
        if len(prompt) < 4:
            return
        head = prompt.lstrip()[:200]
        if head.startswith("<system-reminder") or \
           "Continue working toward the active session goal" in head:
            return

        from intuition_pack.store import get_store
        from intuition_pack.pack import Pack
        from intuition_pack.route import route

        store = get_store()
        packs = []
        for domain in store.list():
            raw_pack = store.get(domain)
            if raw_pack:
                try:
                    packs.append(Pack.from_json(raw_pack))
                except Exception:
                    pass
        if not packs:
            return
        hit = route(prompt, packs)
        if hit is None:
            return
        domain, rule = hit
        pack = next(p for p in packs if p.domain == domain)
        block = pack.prompt_block()
        ctx = (
            f"<intuition-pack domain={domain} rule={rule}>\n"
            f"{block}\n\n"
            f"使用规则（强制）：对属于本域的候选，先用上面的示例做快分类；"
            f"给出任何判定前必须调用 intuition-pack 的 verify 工具做机械确认"
            f"（verifier: {pack.verifier.name}，规则：{pack.verifier.rule}）。"
            f"verify 的判定优先于你的快分类。\n"
            f"</intuition-pack>"
        )
        print(json.dumps({"additionalContext": ctx}, ensure_ascii=False))
    except Exception:
        pass


main()
