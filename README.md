# Intuition-Mechanism Program

**Insight Mechanism Reproduction Program** — a Mushroom-Body Program track.
Research plan: [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md)

> 中心问题:Ramanujan 型公式发现能否被还原为机械流水线?"灵感"在其中是哪几步、
> 能否被机器复现并测出签名?

## 现状

| 组件 | 状态 |
|---|---|
| `validator.py` | ✅ 50 位验证门,Ramanujan/Chudnovsky 双锚点 PASS |
| `family_gen.py` | ✅ Heegner CM 点 → θ 常数 → 奇异模 → j;d=163 锚点 PASS(j = −640320³,误差 2.4e-101) |
| `series_gen.py` | ✅ **D1 GATE PASS**:从 d 出发经 z=1728/j 与 ₃F₂ 系数求和,Chudnovsky 系数 (13591409, 545140134) 以 96.9 位整数控复现 |
| T0 合成族扫描 | ⏳ 下一个工作单元(图族 + 规范型,P1/P2) |
| T2 A/B 引擎(灵感签名 P5) | ⏳ D1 后 |

## 过程中抓到的三个 bug(锚点自测的价值)

1. θ 函数 nome 是 `exp(πiτ)` 而非 `exp(2πiτ)`——平方 nome 使 d=163 的 j 差 17 个数量级;
2. Heegner j 的虚部是浮点噪声,整数立方根检查必须取实部;
3. **恒等式方向**:由 `1/π = 12·T/640320^{3/2}` 得 `T = 640320^{3/2}/(12π)`,
   不是 `π·640320^{3/2}/12`——数值对照(A·S₀ ≈ 1.359e7)当场揭穿。

## 定律衔接

- 本 track 实验结论写回 [Mushroom-Body Program](https://github.com/aujurd22/flymemory)
  的 `research/RESEARCH.md`(L 系列定律;L1 形态定律与 L5 聚合定律已在此确立)。
- 计划的 P1–P7 预言注册表见 docs/RESEARCH_PLAN.md(先注册后实验)。
