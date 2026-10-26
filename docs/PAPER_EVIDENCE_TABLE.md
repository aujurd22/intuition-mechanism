# 论文证据表（由 `make_paper_tables.py` 生成，禁止手改）

每一行都由脚本从对应 JSON 工件中取值，并记录该文件的 sha256 前缀；论文正文只能引用本表，不得手抄数字。

| # | 主张 | 数值 | 台账行 | 工件（sha256[:12]） |
|---|---|---|---|---|
| 1 | 六行定理落域 | six-row landing d=3: s=6, d=5: s=10, d=7: s=21, d=13: s=13, d=17: s=34 | P185 | `experiments/p185_landing_structure.json` · bc4222b34e4c |
| 2 | 2-elementary 轨迹 | 2-elementary locus = 22 rows | P195 | `experiments/p195_2elem_corrected.json` · 4d5a76a90137 |
| 3 | 算术普查（N=1..60） | census N=1..60 verdict CONFIRMED (rows 60) | P20 | `experiments/p20_census_results.json` · 34c9f31933e4 |
| 4 | G6 功能层预测子 | G6 M1 update-target alignment r=0.51 in the bifurcation window (n=40) | P265 | `experiments/p265_verdict.json` · efd2ffa82c80 |
| 5 | 头牌外部靶：发现循环 | glm dev excess 10.30 (lower is better); kimi dev excess 11.00 (lower is better) | P259 | `experiments/p259_capstone_upgrade.json` · 2e468d815766 |
| 6 | 对官方工件头对头 | OR3 vs official artifact: glm 9.8 vs 10.8 (p=0.0029), kimi 10.05 vs 10.8 (p=0.0806) | P262 | `experiments/p262_funsearch_headtohead.json` · e73e3104c3cc |
| 7 | Arena 全域名打分 | arena discovery_score: sci_data=0.75, math=0.667, code_pattern=0.75 | P152 | `experiments/p152_arena_results.json` · b83df5f516c6 |
| 8 | 曲率信号撤回（n=30） | n=30 seeds, curvature separates winners in 4/13 windows (2250-2350: 132.35 vs 106.98) — null holds | P269 | `p269_curvature_verdict.json` · 862dcb43d953 |
| 9 | 语言化鸿沟（值级） | render value-scale hallucinations 0/3 levels; introspection 2/3 | P273 | `p273_value_scale_analysis.json` · 566248f59055 |
| 10 | 空间声带（合成） | PASS: SL 1.11 cm vs Direct 49.73 cm (n=22) | P275 | `p275_verdict.json` · a7a5b1e0b11e |
| 11 | 堆叠链（双目 z） | MIXED: two-view z 0.23 cm (layer 1) / 0.17 cm (layer 2); P-stack-2 FAIL (tolerance clause) | P276 | `p276_verdict.json` · 3241097e3350 |
| 12 | 真实双目 OOD | MIXED: SL median rel 0.0078 vs Direct 0.4522, paired p=0.00085 (n=14) | P277 | `p277_verdict.json` · b762510fadbd |
| 13 | 鲁棒模板（机制/修法） | MIXED: gate max |diff| 0.0 px; P-tmpl-1 PARTIAL, P-tmpl-2 FAIL | P278 | `p278_verdict.json` · a6ef046b19a5 |
| 14 | 共识簇（in-sample） | MIXED: board 0.2963 (median) -> 0.0059 (largest cluster); block stays 0.835 | P279 | `p279_verdict.json` · 0402113a403c |
| 15 | 前瞻性检验 | MIXED on 5 rows: R2 median 0.1212 vs R1 0.1619, sign test p=0.6875 | P280 | `p280_verdict.json` · dd1d3940e384 |

共 15 条主张；工件缺失/取值失败：0。
