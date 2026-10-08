# VCNet × Mushroom-Body 合体架构 — 实验设计（v1 草案）

## 动机

arXiv 2508.02995（VCNet）证明灵长类视觉皮层的**宏结构**（层级跨区
处理、双流信息分离、自顶向下预测反馈）能带来数据效率与鲁棒性
（Spots-10 92.1% SOTA、光场 74.4%）。但 VCNet 只借了"宏结构"——
微回路层面的稀疏化机制（如果蝇 MB 的 k-WTA / APL）完全缺位。
我们四仓恰好持有微回路构件：

- `flypoet/adaptive_kwta.py` — 自适应 k-WTA（梯度保护已验证，
  CUDA benchmark 齐备）
- `flymemory` 的 Hopfield 模式完成（20% 线索 → 100% 恢复）
- `intuition-mechanism` 的预测-误差门控（P270 在 ARC 上已跑通）

**合体假设**：宏结构（VCNet 骨架）+ 微回路（k-WTA 稀疏化 +
Hopfield 记忆 + 预测门控）> 任一单独。

## 三个接入点（按野心排序）

### A. k-WTA 替换 VCNet 的稀疏化层（最小可发表）

- VCNet 论文未开源；先复现其骨架（分层+双流+反馈，公开描述足够
  详细），稀疏化用我们 adaptive_kwta 替换其默认 ReLU/GELU。
- 基线：同 FLOPs 的 plain CNN / ViT-T / VCNet-ReLU。
- 数据：Spots-10（9★ 数据集仓库可得，~92MB）。
- 指标：准确率、样本效率曲线（1%/10%/100% 数据）、FGSM 对抗鲁棒。
- 预期卖点：数据效率与鲁棒性提升来自稀疏化（MB 的增益在文献中
  从未在皮层宏结构上测过）。

### B. Hopfield 记忆做 top-down 反馈的记忆库（中等）

- VCNet 的预测反馈是层间旁路；我们换成 **Hopfield 模式完成**：
  下层特征作为 20% 线索，上层原型库恢复完整上下文再回注。
- 与 A 共享骨架；消融：反馈 on/off、线索比例扫描。

### C. ARC 帧预测门控 × VCNet 视觉编码（远期）

- P270 的"预测-误差-更新"门控里，帧编码器换成 VCNet 式双流编码，
  检验解耦表征是否提升 changed-cell 预测精度（P270 的 precision
  指标直接复用）。

## 执行计划

1. **矩阵跑完后**（GPU 空出）：clone Spots-10，复现 plain CNN 基线
   （1 天）。
2. 实现 VCNet 骨架（2-3 天，论文宏结构描述 + 标准 conv 块）。
3. 接入 adaptive_kwta（半天，构件现成）。
4. 三臂对比：plain / VCNet-ReLU / VCNet-kWTA（各 3 seed）。
5. 产出：intuition-mechanism 注册表新 P 编号 + flypoet 的跨域
   验证章节；若 A 点假设成立 → 独立 preprint 草稿。

## 风险

- VCNet 未开源：骨架复现有偏差风险（缓解：先做 A 的消融部分，
  不依赖精确复现——k-WTA 在"分层双流"上 vs 在 plain CNN 上的
  差异本身即是结果）。
- Spots-10 是小数据集（纹理敏感），结论外推性有限（缓解：加
  CIFAR-10-C 鲁棒性对照）。
