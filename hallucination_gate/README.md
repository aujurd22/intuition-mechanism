# hallucination-gate v1

输出端收费站：任何 LLM 主张必须以四态之一出厂。

四态：VERIFIED（过验证门）/ REFUTED（否决，默认拦截）/ ABSTAIN（弃权）/ SPECULATION（猜测标签）。

四区路由（幻觉解剖）：
- zone 1 验证器可得域 → 执行机械验证器（复用 intuition_pack 验证器注册表）
- zone 2 长尾事实 → ABSTAIN（引用策略 v2 接入点）
- zone 3 影子规则 → ABSTAIN + 影子邻域对比（v2 接入点，P-LAW1 区）
- zone 4 洞见前沿 → SPECULATION（不可消灭，只分拣）

亮点：NEAR_INTEGER 三带判定（P142）映射到 ABSTAIN——近整数陷阱处机器自身置信 0.5，主张强制降级，不许以事实身份出厂。

MCP 注册：见 server.py 头注释。
