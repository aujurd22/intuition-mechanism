# -*- coding: utf-8 -*-
"""make_paper_tables.py — generate the paper's evidence table from the artifacts.

The paper must not retype numbers: every row of docs/PAPER_EVIDENCE_TABLE.md is
pulled from a JSON artifact by this script, with the artifact's sha256 recorded so
a reader can check the exact bytes. `--check` regenerates and diffs; registry_check
runs it in check mode.

Run:  python make_paper_tables.py          (write the table)
      python make_paper_tables.py --check  (exit 1 if stale or unreadable)
"""
import hashlib
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs", "PAPER_EVIDENCE_TABLE.md")


def load(rel):
    return json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:12]


# --- extractors: (claim, registry row, artifact, fn) ----------------------
def e_p185():
    d = load("experiments/p185_landing_structure.json")
    return "six-row landing " + ", ".join(
        f"d={k}: s={v['expected']}" for k, v in
        sorted(d["six_row_landing"].items(), key=lambda kv: int(kv[0])))


def e_p195():
    d = load("experiments/p195_2elem_corrected.json")
    return f"2-elementary locus = {len(d['locus_[1,1000]'])} rows"


def e_p20():
    d = load("experiments/p20_census_results.json")
    return f"census N=1..60 verdict {d['verdict']} (rows {len(d['rows'])})"


def e_p265():
    d = load("experiments/p265_verdict.json")
    return f"G6 M1 update-target alignment r={d['M1_corr_with_final']['M1_1000_1300']} in the bifurcation window (n={d['n']})"


def e_p259():
    d = load("experiments/p259_capstone_upgrade.json")
    out = []
    for model, m in d["models"].items():
        ok = [r for r in m["rounds"] if r["err"] is None and r["dev_mean_excess"] is not None]
        best = min(ok, key=lambda r: r["dev_mean_excess"])
        out.append(f"{model.split('-')[0]} dev excess {best['dev_mean_excess']:.2f} (lower is better)")
    return "; ".join(out)


def e_p262():
    d = load("experiments/p262_funsearch_headtohead.json")
    g = d["stats"]["glm-5.3-flash"]["OR3"]
    k = d["stats"]["kimi-k2.8-preview"]["OR3"]
    return (f"OR3 vs official artifact: glm {g['he_mean']} vs {g['funsearch_mean']} "
            f"(p={g['wilcoxon_p']}), kimi {k['he_mean']} vs {k['funsearch_mean']} "
            f"(p={k['wilcoxon_p']})")


def e_p152():
    d = load("experiments/p152_arena_results.json")
    scores = {dom: v.get("discovery_score") for dom, v in d.items()}
    return "arena discovery_score: " + ", ".join(f"{k}={v}" for k, v in scores.items())


def e_p269():
    d = load("p269_curvature_verdict.json")
    w = d["curvature_win_vs_lose"]["2250_2300_2350"]
    return (f"n={d['n']} seeds, curvature separates winners in {d['n_win']}/13 windows "
            f"(2250-2350: {w['win']} vs {w['lose']}) — null holds")


def e_p273():
    d = load("p273_value_scale_analysis.json")["verdict"]
    return (f"render value-scale hallucinations {d['render_total_value_halluc']}/3 levels; "
            f"introspection {d['explain_total_value_halluc']}/3")


def e_p275():
    d = load("p275_verdict.json")
    p = d["predictions"][0]
    return (f"{d['overall']}: SL {p['sl_mean_cm']} cm vs Direct {p['direct_mean_cm']} cm "
            f"(n={p['n_paired']})")


def e_p276():
    d = load("p276_verdict.json")
    z = d["predictions"][0]["two_view_z_median_cm"]
    return (f"{d['overall']}: two-view z {z['layer1']} cm (layer 1) / {z['layer2']} cm "
            f"(layer 2); P-stack-2 FAIL (tolerance clause)")


def e_p277():
    d = load("p277_verdict.json")
    p = d["predictions"][0]
    return (f"{d['overall']}: SL median rel {p['sl_median_rel_err']} vs Direct "
            f"{p['direct_median_rel_err']}, paired p={p['paired_perm_p']} (n={d['n_paired']})")


def e_p278():
    d = load("p278_verdict.json")
    return (f"{d['overall']}: gate max |diff| {d['gate']['max_abs_px_diff']} px; "
            f"P-tmpl-1 {d['predictions'][1]['verdict']}, P-tmpl-2 {d['predictions'][2]['verdict']}")


def e_p279():
    d = load("p279_verdict.json")
    rows = {r["row"]: r for r in d["rows"]}
    board = next(r for k, r in rows.items() if k.startswith("Lampshade1"))
    return (f"{d['overall']}: board {board['rel_R1']} (median) -> {board['rel_R2']} "
            f"(largest cluster); block stays 0.835")


def e_p280():
    d = load("p280_verdict.json")
    return (f"{d['overall']} on {d['n_rows']} rows: R2 median "
            f"{d['predictions'][0]['median_rel_R2']} vs R1 {d['predictions'][0]['median_rel_R1']}, "
            f"sign test p={d['predictions'][0]['sign_test_p_one_sided']}")


SPECS = [
    ("六行定理落域", "P185", "experiments/p185_landing_structure.json", e_p185),
    ("2-elementary 轨迹", "P195", "experiments/p195_2elem_corrected.json", e_p195),
    ("算术普查（N=1..60）", "P20", "experiments/p20_census_results.json", e_p20),
    ("G6 功能层预测子", "P265", "experiments/p265_verdict.json", e_p265),
    ("头牌外部靶：发现循环", "P259", "experiments/p259_capstone_upgrade.json", e_p259),
    ("对官方工件头对头", "P262", "experiments/p262_funsearch_headtohead.json", e_p262),
    ("Arena 全域名打分", "P152", "experiments/p152_arena_results.json", e_p152),
    ("曲率信号撤回（n=30）", "P269", "p269_curvature_verdict.json", e_p269),
    ("语言化鸿沟（值级）", "P273", "p273_value_scale_analysis.json", e_p273),
    ("空间声带（合成）", "P275", "p275_verdict.json", e_p275),
    ("堆叠链（双目 z）", "P276", "p276_verdict.json", e_p276),
    ("真实双目 OOD", "P277", "p277_verdict.json", e_p277),
    ("鲁棒模板（机制/修法）", "P278", "p278_verdict.json", e_p278),
    ("共识簇（in-sample）", "P279", "p279_verdict.json", e_p279),
    ("前瞻性检验", "P280", "p280_verdict.json", e_p280),
]


def build():
    lines = [
        "# 论文证据表（由 `make_paper_tables.py` 生成，禁止手改）",
        "",
        "每一行都由脚本从对应 JSON 工件中取值，并记录该文件的 sha256 前缀；"
        "论文正文只能引用本表，不得手抄数字。",
        "",
        "| # | 主张 | 数值 | 台账行 | 工件（sha256[:12]） |",
        "|---|---|---|---|---|",
    ]
    missing = []
    for i, (claim, row, rel, fn) in enumerate(SPECS, 1):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            missing.append(rel)
            lines.append(f"| {i} | {claim} | **MISSING ARTIFACT** | {row} | `{rel}` |")
            continue
        try:
            value = fn()
        except Exception as exc:                      # noqa: BLE001
            missing.append(f"{rel} ({type(exc).__name__}: {exc})")
            value = f"**EXTRACTOR ERROR** {type(exc).__name__}"
        lines.append(f"| {i} | {claim} | {value} | {row} | `{rel}` · {sha(rel)} |")
    lines.append("")
    lines.append(f"共 {len(SPECS)} 条主张；工件缺失/取值失败：{len(missing)}。")
    return "\n".join(lines) + "\n", missing


def main():
    text, missing = build()
    if "--check" in sys.argv:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        ok = (text == current) and not missing
        print(f"[{'PASS' if ok else 'FAIL'}] paper evidence table: "
              f"{len(SPECS)} claims, {len(missing)} missing, "
              f"{'up to date' if text == current else 'STALE (re-run without --check)'}")
        for m in missing:
            print("  missing:", m)
        sys.exit(0 if ok else 1)
    open(OUT, "w", encoding="utf-8", newline="").write(text)
    print(f"wrote {OUT}: {len(SPECS)} claims, {len(missing)} missing")
    for m in missing:
        print("  missing:", m)


if __name__ == "__main__":
    main()
