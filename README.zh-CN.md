# Intuition-Mechanism

<p align="center">
  <b>中文</b> · <a href="README.md">English</a>
</p>

<p align="center">
  <img src="docs/fig_sixrow.png" width="720" alt="六行定理普查图"/>
</p>

> **直觉是可验证的经验压缩，在可迁移的结构中。**
> 四个条件——压缩、验证、迁移、新颖——全部机械化检查。
> 不满足任何一条的，都是幻觉。这条边界是可以测量的。

---

## 从果蝇脑到结构发现

一切从一个问题开始：**果蝇的蘑菇体只有 ~2500 个 Kenyon 细胞，凭什么做联想记忆？**

答案是 k-WTA（赢者通吃）稀疏编码——高维随机投影 + 尖锐竞争。这个机制被 [FlyMemory](https://github.com/aujurd22/flymemory)（经验记忆）、[FlyPoet](https://github.com/aujurd22/flypoet)（表示形成）、[FlyLoop](https://github.com/aujurd22/flyloop)（世界切换）分别验证。而本仓 `intuition-mechanism` 是这条线的**最远端**：

```
FlyPoet          FlyMemory           FlyLoop            ← 本仓
表示如何形成      经验如何保存         经验何时压缩        压缩后如何产生新结构
     ↓                 ↓                   ↓                    ↓
  稳定表示          可审计记忆          组合推理           六行定理 / Insight Arena
```

四层对应智能形成的四个阶段。本仓回答最后一层的问题：**压缩之后，新结构怎么冒出来？**

---

## 核心发现

### 六行有理性定理

对 Ramanujan 型 1/π 级数，1/x₆(i√(d/6)) 为正整数**当且仅当** d ∈ {1, 3, 5, 7, 13, 17}，值恰为 {8, 12, 20, 32, 104, 200}。

- **穷尽验证**：d ∈ [1, 5000]，零反例（P121 + P157）
- **三层解释**：场（genus 域）→ 轨道（支撑特征）→ 单位（Pell 归一化）
- **独立复算**：双代码路径一致到 3.5×10⁻¹⁷
- **Heegner 影子**：d=978=6×163 的 near-integer 行（residual 7.5×10⁻¹³ = e^(π√163) 签名）——连接 Heegner 数理论

| d | 1/x₆ | 2-elementary | h(Q(√−d)) |
|---|---|---|---|
| 1 | 8 | ✓ | 1* |
| 3 | 12 | ✓ | 1 |
| 5 | 20 | ✓ | 2 |
| 7 | 32 | ✓ | 1 |
| 13 | 104 | ✓ | 2 |
| 17 | 200 | ✓ | 4 |
| 978 | — | ✗ (multi-support) | 7.5e-13 near-int |

<details>
<summary>三层证明结构（展开）</summary>

| 层 | 内容 | 证明类型 |
|---|---|---|
| **场** | 2-elementary ⟹ H = H_gen：所有代数模值落在 genus 域内 | 定理（引用级） |
| **轨道** | P¹² 的支撑 = 单实二次坐标 ℚ(√s_d)；s_d ∈ {6,10,21,13,34} | 测量 + PSLQ 确认 |
| **单位** | 64P¹² = ε^(−2m_d)：椭圆单位到秩 1 场基本单位的投影 | Siegel–Ramachandra + F1-F3 验证 |
| **有理性** | 导数比 R_d = (Ec/W₆)/24 ∈ ℚ（消越恒等式，P83-A） | 定理（初等证明） |

</details>

### Insight 双轴理论

LLM 判官的"有趣度"不是单一维度，而是两个独立轴：

- **Surprise 轴**：追踪 genus 结构深度（固定 degree 下的深度判别）
- **Utility 轴**：追踪已发表有理性的接近度

两轴可分离（P92 双重分离实验），**且歧义自觉跨 carrier 迁移**（P166）。

### Insight-vs-Hallucination 边界（机械化）

| 条件 | 机械检查 | 失败形态 |
|---|---|---|
| Compression | mdl_ratio > 1 | PARAPHRASE |
| Verification | 探针一致率 = 100% | **HALLUCINATION** |
| Transfer | 异 carrier = 100% | OVERFIT |
| Novelty | 规则非 charter 重述 | — |

P152 实战：math 轨判官的"RATIONAL ⟺ 类数 1"规则（Heegner 假设形状），探针 5/6，边界**正确拒绝**——并追踪发现这是 Heegner 集 vs rational locus 的**范畴错误**（P163）。

---

## Insight Arena

三轨 × 三模型 × 三种子的结构发现基准：

| 轨道 | Compression | Transfer | Surprise | 判定 |
|---|---|---|---|---|
| 科学数据（阻尼振荡 + 隐藏相位反转） | 19.5 | 100% | ✓ 未提示自发检出 | INSIGHT |
| 代码设计模式（输入纯度规则） | 13.0 | 100% | — | INSIGHT |
| 数学（census 规则发现） | — | 77–79% | — | HALLUCINATION |

**909 条判定**（P153），全部存档。噪声对照实验（P164）证明 benchmark 有判别力——不是橡皮图章。

### 三条 standing 定律

1. **Math 是抗性域**——三模型全 76–79%（n=96/模型），收缩定律有地板（P153）
2. **歧义压力需要构造**——最小自然窗无法制造压力（96/96 全中，P159）；必须有晚分歧规则对
3. **Verbalization gap 在知识层**——三模型陈述规则代码执行全 50%（纯机遇），操作判定 79–94%——**模型知道它说不出的东西**（P170）

---

## intuition-pack 插件

**Build your own System-One judge: verified, calibrated, audit-trail included.**

8 个 MCP 工具 + 10 个验证器 + 3 个在线域：

```
pack_probe              你的域是压缩域吗？（学习曲线自动判定）
pack_build              蒸馏对比示例包 + charter + 验证器规格
verify / score          机械判定 + 完整审计轨迹 + 弃权原语
regression              机械门禁——不过不许部署
route_text              零 LLM 机械触发路由
needs_verification_check  Jev-nouli 对齐弃权检查
```

每个判定通过**四条件机械化检查**——Insight-vs-Hallucination 边界由代码执行，不由判官意见决定。

### vs Jev 对比

| 指标 | Jev (arXiv 2609.37647) | intuition-pack verify |
|---|---|---|
| 校准 ECE | 0.028 (Choice) | **0.0075** |
| Selective @ 50% | 96.3–98.2% | **100%** |
| 延迟 | 0.36 s (API) | **0.37 ms** (本地) |
| 成本 | ~$2.7e-5/req | **$0** |
| 域广度 | 37 datasets | 12 domains（持续增长） |

诚实条款：协议对齐 ≠ 能力对齐。我们的 ECE 来自残差饱和映射（scope 显式声明），非学习校准。

---

## 通用化现状

```
probe 矩阵     12 域判定完成（COMPRESSION ×3 / SATURATED ×6 / DISTRIBUTIONAL ×1 / BORDERLINE ×2）
验证器模板     执行 / 谓词 / 数值 / schema / 集合 / 正则
自动循环       auto_scan_loop.py — schtasks 每日 07:30 重扫候选域
边界定律       压缩域集合随模型进步收缩 → 耐久资产 = 检测器 + 流水线速度
```

---

## 诚实边界

- 判定线结果是对**特定模型、特定 API 端点、特定时刻**的行为快照——不是可重放的定律
- 类不变量表层（s_d ∈ {6,10,21,13,34} 的统一规则）**仍是古典表格**——理论最深处未闭合
- Memory→Insight 三臂实验（P167）是**本地干燥跑**（单域 24 episode），跨仓全规模实验待执行
- 品味（选择结构空间）是元层直觉，无训练信号——这是程序自己的 P35/P54 负结果反复确认的

---

## 仓库地图

```
docs/
  RESEARCH_PLAN.md            注册表：110+ P-numbers，每条含预测/判定/工件
  DEEP_STRUCTURES.md          四层链 + SCR + verbalization gap + 边界综合
  CHARACTER_OBSTRUCTION.md    genus 理论层（P132 修正）
  INTERESTINGNESS_FORMAL.md   双轴理论 + 判官景观
  MEMORY_GEOMETRY.md          六定律五基底
  MEMORY_CONTROLLER.md        R1-R8 策略 + DR 接口层
  RAG_DESIGN_CONSTRAINTS.md   C1-C7 + DR1-DR10
  THEOREM_FIVE_ROWS.md        六行定理陈述 + 证明标签
intuition_pack/               MCP 插件（8 工具）
sdb/                          Structure Discovery Benchmark
p*.py, *.json                 ~100 实验脚本 + 归档结果
```

---

## 相关仓库

| 仓库 | 层 | 关系 |
|---|---|---|
| [mushroom-body-program](https://github.com/aujurd22/mushroom-body-program) | 总入口 | Selection → Compression → Memory → Emergent Structure |
| [flymemory](https://github.com/aujurd22/flymemory) | 记忆层 | 经验保存与压缩（本仓的输入源） |
| [flypoet](https://github.com/aujurd22/flypoet) | 表示层 | 稀疏表示形成（本仓的基底） |
| [flyloop](https://github.com/aujurd22/flyloop) | 学习层 | 何时压缩经验（本仓的约束源） |

---

*The rest is hallucination — and that boundary is measurable.*
