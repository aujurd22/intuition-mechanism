# -*- coding: utf-8 -*-
"""G2B 判卷工具 — 对照注册答案键给星语考卷评分。

用法:
  python judge_answers.py 答案.txt        # 文件格式见下
  python judge_answers.py                # 从剪贴板说明的粘贴格式读 stdin

答案文件格式（逐行，顺序自由，缺答按错计）:
  1. badum 有把握
  7. batis 在猜
  13. 方法在……时可能失灵……     (文字题，只存档不判分)
  14. is
  21. ok

输出: exam1/exam2 准确率、把握校准、(元音,词尾)对签名（练过 vs 新对）、
陷阱词错误率、P239 预注册判据、逐题明细。文字题单独打印供 0-2 分人工评。
"""
import json, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = json.load(open(os.path.join(HERE, "answer_key.json"), encoding="utf-8"))
TRAIN_PAIRS = {r["stem"][1] + r["stem"][2] for r in KEY["train"]}

def suffix_of(plural):
    return plural[-2:] if plural.endswith(("um", "ok")) else plural[-2:]

def parse_answers(text):
    p1, p2, scope = {}, {}, ""
    for line in text.splitlines():
        m = re.match(r"\s*(\d+)\.\s*(.+)", line.strip())
        if not m:
            continue
        n, body = int(m.group(1)), m.group(2).strip()
        if n == 13:
            scope = body
        elif 1 <= n <= 12:
            mm = re.match(r"(\S+?)\s*(有把握|在猜|sure|guess)?\s*$", body, re.I)
            if mm:
                p1[n] = (mm.group(1).lower(), (mm.group(2) or "").lower())
        elif 14 <= n <= 21:
            mm = re.search(r"(um|is|ok)\b", body, re.I)
            if mm:
                p2[n] = mm.group(1).lower()
    return p1, p2, scope

def main():
    text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 \
        else sys.stdin.read()
    p1, p2, scope = parse_answers(text)

    print("=== 第一部分（12 题） ===")
    e1_ok = e1_n = 0
    sure, guess = [], []
    trap_wrong = trap_n = plain_wrong = plain_n = 0
    pair_rows = []
    for i, r in enumerate(KEY["exam1"]):
        n = i + 1
        t = suffix_of(r["plural"])
        ans, conf = p1.get(n, ("", ""))
        ok = ans[-2:] == t if ans else False
        e1_ok += ok; e1_n += 1
        (sure if conf in ("有把握", "sure") else guess).append(ok)
        is_trap = (r["stem"][0] in "bdg") != (r["stem"][2] in "bdg")
        pair = r["stem"][1] + r["stem"][2]
        pair_rows.append((pair, pair in TRAIN_PAIRS, ok))
        if is_trap:
            trap_n += 1; trap_wrong += (not ok)
        else:
            plain_n += 1; plain_wrong += (not ok)
        print(f"{n}. {r['stem']} 答={ans or '(缺)'} 键={r['plural']} "
              f"{'对' if ok else '错'} [{conf or '未标'}]{' 陷阱' if is_trap else ''}")
    e1 = e1_ok / e1_n
    cal = (sum(sure) / len(sure) - sum(guess) / len(guess)) \
        if sure and guess else None
    print(f"exam1: {e1_ok}/{e1_n} = {e1:.3f}  "
          f"有把握 {sum(sure)}/{len(sure)}  在猜 {sum(guess)}/{len(guess)}"
          + (f"  校准差 {cal:+.2f}" if cal is not None else ""))

    print("=== 第二部分（8 题，密码遮蔽） ===")
    e2_ok = e2_n = 0
    nov_ok = nov_n = trd_ok = trd_n = 0
    for i, r in enumerate(KEY["exam2"]):
        n = i + 14
        t = suffix_of(r["plural"])
        ans = p2.get(n, "")
        ok = ans == t
        e2_ok += ok; e2_n += 1
        pair = r["stem"][1] + r["stem"][2]
        trained = pair in TRAIN_PAIRS
        if trained:
            trd_n += 1; trd_ok += ok
        else:
            nov_n += 1; nov_ok += ok
        print(f"{n}. {r['cipher']}({r['stem']}) 答={ans or '(缺)'} 键={t} "
              f"{'对' if ok else '错'} [{pair} {'练过' if trained else '新'}]")
    e2 = e2_ok / e2_n
    print(f"exam2: {e2_ok}/{e2_n} = {e2:.3f}  "
          f"练过对 {trd_ok}/{trd_n}  新对 {nov_ok}/{nov_n}")

    all_pairs = pair_rows + [(r["stem"][1] + r["stem"][2], True, True)
                             for r in KEY["train"]]
    trd_all = [ok for p_, tr, ok in pair_rows + 
               [(x["stem"][1] + x["stem"][2], True, True) for x in KEY["train"]]
               if tr]
    print("=== 键型签名 ===")
    print(f"练过对合并: {trd_ok + 16}/{trd_n + 16}   "
          f"新对合并: {nov_ok}/{nov_n}")
    print(f"陷阱词错误 {trap_wrong}/{trap_n}  非陷阱错误 {plain_wrong}/{plain_n}"
          f"  -> P-b {'CONFIRM' if trap_wrong > plain_wrong else 'NOT confirmed'}")

    print("=== P239 预注册判据 ===")
    print(f"P-a 可学会 (exam1>=8/12): {'PASS' if e1_ok >= 8 else 'FAIL'}")
    print(f"P-c 无塌缩 (exam1-exam2 < 0.25): "
          f"{'PASS' if e1 - e2 < 0.25 else 'FAIL'} (差 {e1 - e2:+.3f})")
    print(f"P234 迁移: 遮蔽后 {e2:.3f} vs 机遇 1/3 -> "
          f"{'结构存活' if e2 > 0.5 else ('崩塌' if e2 < 0.45 else '中间')}")
    print(f"对比模型: deepseek 1.00/0.375  doubao 0.83/0.625  glm 0.42/0.0  "
          f"作者pilot 0.833/0.875")
    print("=== 文字题（0-2 人工评分：0 无范围 / 1 模糊 / 2 明确条件边界） ===")
    print(scope or "(未答)")

if __name__ == "__main__":
    main()
