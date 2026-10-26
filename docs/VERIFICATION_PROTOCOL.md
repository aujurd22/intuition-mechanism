# 验证协议（Verification protocol，自 P278 起强制）

> 这一节不是方法论修辞，是因为一次真实的翻车写下来的。

## 为什么有这条规则

P278 的 verdict 在提交（`00619fe`）之后被一个只读复核代理独立重写复算，抓出四个问题：

1. **复现闸门算出来却没有接线**——脚本算了 gate，然后照样给三条预测判分；
   `INCONCLUSIVE` 分支根本不存在，`declared_deviation` 里那句「已通过」还是硬编码字符串。
   复核者把输入扰动 +5 px 后用**同一份脚本**跑，它照样输出 MIXED、照样自称通过。
2. **机制结论依赖一个物理上不可能的样本**——Monopoly 的 `-18 px` 视差在正基线校正立体里不存在；
   剔掉它，木块的「离群」结论就没了（P-tmpl-1 因此从 PASS 降为 PARTIAL）。
3. **同义反复的对照被当成胜利**——Midd2 放不下任何模板，中位数≡中心模板，等于没做任何事，
   却计入了「12 条对照全通过」。
4. **措辞与数据不符**——「6 行没有 bbox」实为 5 行 + 1 行无 rel_err；「14×9」实为 112 次匹配；
   「约 2 px」实为平均 −1.3 px；「打到背景」是没测量过的说法。

四条的共性是同一个：**判据存在，但没有被强制**。所以规则不是「要更仔细」，而是**要能被机器拒绝**。

## 规则（P278 及以后）

一个实验只要提交了机读 verdict（`p<ID>_verdict.json`），就必须同时提交
`verifications/p<ID>.json`，包含三块：

```json
{
 "independent_recompute": {
   "script": "verify/p<ID>_indep.py",     // 不得 import 被测估计器
   "tolerance_px": 1.0, "observed_max_abs_px": 1.0, "status": "PASS"
 },
 "perturbation_test": {
   "script": "verify/p<ID>_perturb.py",   // 扰动输入，要求闸门真的开火
   "perturbation": "...", "expected": "...", "observed": "...", "status": "PASS"
 },
 "validity_clauses": ["...数据有效性条款，例如：负视差无效..."]
}
```

并且 verdict 里必须冻结 `prereg_sha256` 与 `raw_sha256`。

`verify_verdict.py` 会拒绝：

- 缺验证记录；记的是 PASS 但脚本不存在；
- `observed_max_abs_px > tolerance_px`；
- 冻结哈希与文件不再一致（有人事后改了预注册或原始数据）；
- 台账里没有对应的行，或行里没写出 verdict 的总体结论；
- `validity_clauses` 为空。

`ID < P278` 的历史行**豁免**（列为 grandfathered），因为把新纪律追溯适用会让 200 多行因与内容无关的理由失败。

## 怎么加一个新实验（模板）

```bash
# 1. 预注册（跑之前！）
#    p<ID>_preregistration.json  含 predictions / falsifies / validity_clauses
# 2. 跑         -> out/p<ID>/p<ID>_raw.json
# 3. 判定       -> p<ID>_verdict.json（含 hashes.prereg_sha256 / raw_sha256）
# 4. 独立复算   -> verify/p<ID>_indep.py        （重写估计器，不 import 被测代码）
# 5. 扰动测试   -> verify/p<ID>_perturb.py      （把闸门推到失败，确认它真的短路）
# 6. 记录       -> verifications/p<ID>.json
# 7. CI         -> python registry_check.py && python audit_provenance.py && python verify_verdict.py
```

## 已做的破坏性验证（这两条测试本身要能失败）

| 破坏 | 期望 | 实测 |
|---|---|---|
| 移走 `verifications/p278.json` | 验证门失败 | `[FAIL] P278: no verification record`，exit 1 |
| 往 `p278_preregistration.json` 追加一个空格 | 冻结哈希失配 | `[FAIL] P278: frozen prereg_sha256 no longer matches`，exit 1 |
| 恢复后 | 通过 | `VERIFICATION GATE: PASS — 1 enforced row(s), 5 grandfathered` |

## 现状

- `verify/p278_indep.py`：独立 NCC 重实现，**125 个位置，max |diff| = 1 px**（容差 1 px；
  1 px 来自近似并列视差在浮点求和顺序上的翻转）。
- `verify/p278_perturb.py`：扰动 +5 px 后跑**真实的** `p278_analyze.py`，输出
  `INCONCLUSIVE` / 全部 `NOT SCORED` / 文本写明 FAILED。
- 复核代理的独立实现（同一批位置）给出 **0 px**——两份独立实现互相印证。
