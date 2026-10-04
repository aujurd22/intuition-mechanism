# intuition-pack

System-One 判官质检套件：让"AI 觉得对"变成可检验、可校准、带审计轨迹的判断。

## 8 个 MCP 工具

```
pack_probe              你的域是压缩域吗？（学习曲线自动判定——只在压缩域赚钱）
pack_build              蒸馏对比示例包 + charter + 验证器规格
verify / score          机械判定 + 完整审计轨迹 + 弃权原语
regression              机械门禁——不过不许部署
route_text              零 LLM 机械触发路由（CJK 用 alnum-lookaround）
needs_verification_check  Jev-nouli 对齐弃权检查
```

## 快速开始

1. MCP 注册：ZCode 配置里把 `server.py` 挂为 MCP server（见文件头注释）；
2. `pack_probe` 检查任务域 → 压缩域才值得上判官；
3. `pack_build` 蒸馏对比教材 → `verify` 上岗，每道判断代码复核。

## 状态

- 12+ 域 probe 矩阵完成（COMPRESSION ×3 / SATURATED ×6 / DISTRIBUTIONAL ×1 / BORDERLINE ×2）
- 对比 Jev（arXiv 2609.37647）：ECE 0.0075 vs 0.028、延迟 0.37ms 本地、$0 成本
- 边界定律：压缩域集合随模型进步收缩 → 耐久资产 = 探测器 + 流水线速度
- 权威存储：本地文件（本目录 store.py），flymemory 只做审计镜像

诚实条款：协议对齐 ≠ 能力对齐——ECE 来自残差饱和映射（scope 显式声明），非学习校准。
详细成果与实验地图见仓库根 README。
