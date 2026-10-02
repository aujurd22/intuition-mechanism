# Insight Boundary Benchmark

**Formal Specification v1.0** — 2026-10-03

**Program**: Intuition-Mechanism (Mushroom-Body Program track)
**Question**: Insight 是不是一个不可分割的整体？如果是可分解的，边界在哪？

---

## 1. 定义

**核心命题**：Insight is verified compression of experience into
transferable structure.

**四条件**（全部机械化可查）：

| # | 条件 | 机械检查 | 失败形态 |
|---|---|---|---|
| C | Compression | bits(experience) / bits(rule) > 1 | PARAPHRASE |
| V | Verification | 探针一致率 = 100%（机械验证器仲裁） | HALLUCINATION |
| T | Transfer | 异 carrier/异 regime = 100% | OVERFIT |
| N | Novelty | 规则非 charter 重述 | — |

**边界判定**：
- **INSIGHT** = C ∧ V ∧ T ∧ N 全满足
- **HALLUCINATION** = C ✓ 但 V < 1
- **OVERFIT** = V ✓ 但 T < 1
- **PARAPHRASE** = N ✗

**边界由代码执行，不由判官意见决定。**

## 2. 三种实验

### 实验 1：MDL 分支选择

判官看到 N 项发现窗，预测延续。构造竞争规则 B_N = A(n) + ∏(n−i)（与 A
在窗内完全相等、之后巨幅分歧）。评分：判官的延续跟 A 分支还是 B 分支？

**通过标准**：选 A（最小描述）分支。

### 实验 2：歧义自觉 + 实质替代

在真欠定窗（多强规则同时拟合），判官是否自发声明歧义？被追问时能否
命名一个实质性的替代规则？

**通过标准**：自发声明歧义 + 被追问时能命名真发散的替代规则。

### 实验 3：晚分歧压力

发现窗截短（4 项），多规则同时拟合的最小自然窗。

**通过标准**：仍能选出正确分支（而非任意分支）。

## 3. 测量维度（非实验，连续量）

### 3a. SCR（Search-space Collapse Ratio）

H_before = 独立判官（跨模型×种子）对同一探针的判断分布熵
H_after = 机械验证器的熵（= 0，确定性）
SCR = 1 − H_before（归一化到 [0,1]，1 = 完全坍缩）

**物理意义**：SCR = 独立判官收敛到同一结构的程度。
SCR = 1 ⟹ 该域是压缩域（结构可迁移跨判官）。
SCR < 1 ⟹ 域欠定（多结构拟合同一发现集）。

### 3b. Verbalization Gap

步骤：判官陈述规则 → 规则翻译为代码 → 代码执行 → 代码准确率。
**GAP = 操作准确率 − 陈述规则代码准确率。**

GAP > 0 ⟹ Polanyi 悖论实证（模型知道它说不出的）。
GAP = 0 ⟹ 表达层瓶颈（更好 prompt 可关）。

### 3c. 噪声敏感度

干净窗 vs 噪声窗（单项扰动）的行为差异。
Benchmark 有判别力的充要条件：至少一个模型/条件/域存在显著差异。

---

## 4. 已测试域（12 域）

### 4.1 压缩域（COMPRESSION = 3）

| 域 | SCR | Accuracy | 判官模型 |
|---|---|---|---|
| census（六行定理） | 0.769 (部分) | 77–79% @ n=96 | deepseek/doubao/kimi |
| constrained-set | — | 85.2% (doubao) | doubao |
| config-compliance | — | 97.5% (doubao pack) | doubao |

census 特殊：唯一 multi-support 的压缩域（P¹² 支撑 = 单实二次但跨模型
分歧持续）。constrained-set 和 config-compliance 是**执行验证域**——
验证器即真值，H_after 恒为 0。

### 4.2 饱和域（SATURATED = 6）

| 域 | Accuracy | 模型 |
|---|---|---|
| code-pass-fail | 100% ×3 | all |
| python-traps | 100% ×3 | all |
| date_logic | 100% | all |
| string_ops | 100% | deepseek/doubao |
| list_ops | 100% | all |
| recursion | 100% | deepseek/doubao |

### 4.3 分布域（DISTRIBUTIONAL = 1）

| 域 | 结果 |
|---|---|
| IMDB / AG News | pack 无增益（±3pp）——分布域零样本已到天花板 |

---

## 5. 结果汇总

### 5a. Insight Boundary 实验

| 实验 | deepseek | doubao | kimi | 通过 |
|---|---|---|---|---|
| E1 MDL 分支选择 | 5/5 A | 5/5 A | 5/5 A | ✓ |
| E2 歧义自觉 + 实质替代 | 5/5 + 3/5 | 5/5 + 4/5 | 5/5 + 5/5 | ✓ |
| E3 晚分歧拒绝 | 3/3 amb | 3/3 amb | 2/3 amb | ✓ |

### 5b. 噪声对照（P164）

| 模型 | 异常检出 | 歧义声明 | 干净延续 |
|---|---|---|---|
| deepseek | 16/24 | 24/24 | 20/24 |
| doubao | 20/24 | 20/24 | 17/24 |
| kimi | 22/24 | 24/24 | 18/24 |

doubao 出现 4 次过度自信失败（噪声窗无声转弱规则）——失败形态首现。

### 5c. 跨 carrier 迁移（P166）

歧义自觉 6/6 迁移到多项式 carrier——协议级行为，域无关。

### 5d. Verbalization Gap（P170）

| 模型 | 陈述规则代码准确率 | 操作判定准确率 | GAP |
|---|---|---|---|
| deepseek | — (拒绝代码) | 81.2% | — |
| doubao | 50.0% | 100% | **50pp** |
| kimi | 50.0% | 100% | **50pp** |

**GAP 在知识层**：模型无法言说的特征，不是表达能力问题。

---

## 6. 与已有工作的关系

| 已有工作 | 覆盖 | 我们独有 |
|---|---|---|
| [JudgeBench](https://arxiv.org/abs/2410.12784) (ICLR 2025) | 判官可靠性评估 | verbalization gap、SCR、歧义自觉 |
| [ARC-AGI](https://arcprize.org) | 抽象推理 | 验证器护送 + 四条件边界 |
| [EAIRA](https://journals.sagepub.com) (2026) | LLM-as-judge 方法论 | SCR 跨独立判官测量 |
| [Conformal Elo](https://arxiv.org/abs/2606.13221) | conformal 弃权 | ABSTAIN 已采纳（P168），SCR 独有 |
| [Kahneman–Klein](https://academic.oup.com/aob) | 专家直觉条件 | 工程化实现 |

---

## 7. 诚实限制

1. **样本量**：Floor cells 基于三种子 38–57 票；弱信号（< 60%）不排除
2. **单流限制**：P167 三臂实验只覆盖单律流——多律流切换（flyloop 场景）未测
3. **模型代际依赖**：收缩定律意味着部分结论有过期日期
4. **Verbalization gap 在知识层**：verbalization 训练不可能关闭——只能靠 carrier 多样化
5. **2-elementary locus 的判别式族依赖**：11 行结果限于 D = −24d；其他族（如 −4d）可能不同
6. **"品味不可机械化"是当前结论**：如果未来出现能自动生成验证器的方法，这个边界会移动

---

## 8. 中心问题

> **什么样的压缩，能够产生可迁移的结构？**

我们的回答（第一版）：

> 压缩产生可迁移结构 ⟺ 独立判官坍缩到同一结构（SCR → 1）
> 且陈述规则通过机械验证（V = 1）
> 且跨 carrier 有效（T = 1）
> 且不是 charter 重述（N = 1）。

四个条件的交集 = Insight。这是可执行的，不是隐喻。

---

*Source: [Intuition-Mechanism](https://github.com/aujurd22/intuition-mechanism) —
Mushroom-Body Program track.
[Benchmark code](sdb/), [arena](sdb/arena.py),
[plugin](intuition_pack/), [registry](docs/RESEARCH_PLAN.md).*
