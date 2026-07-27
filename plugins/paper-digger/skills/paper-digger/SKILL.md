---
name: paper-digger
description: Use when starting or resuming a multi-phase Paper Digger workspace from research direction through submission. Triggers on resume Paper Digger, full research lifecycle, 全流程论文, 恢复研究项目.
---

# Paper Digger — 学术研究全流程编排

Paper Digger 是 checkpoint-gated 的研究编排 skill。它拥有方向探索、选刊、计划、实验、理论、跨会话状态和研究期红队；文献、写稿、配图、润色、审稿与排版优先复用宿主已有能力，但**不要求**任何特定第三方 skill。

## 先定位便携运行时

将包含本 `SKILL.md` 的目录记为 `<PD_SKILL>`。不要假设当前工作目录就是 skill 目录。

- 首选运行：`python3 <PD_SKILL>/scripts/pd.py <command> ...`
- 如果用户另行安装了 PyPI CLI，`pd <command> ...` 与上式等价。
- 调用 Python API 时，把 `<PD_SKILL>/scripts` 加入 `PYTHONPATH`，再 `import paper_digger`。
- 不得因为系统里没有全局 `pd` 命令就跳过状态维护；随 skill 分发的运行时不需要安装依赖。

## Phase 0 — 立项与统筹

1. 确认项目 slug、领域、约束（算力、湿实验、时间、目标档次）和项目根目录。
2. 运行：
   `python3 <PD_SKILL>/scripts/pd.py init --project <slug> --field "<field>" --effort standard --root <project-root>`
3. 在 `<project-root>/paper-digger/` 检查编号目录、`state.json`、`ROADMAP.md` 和 `README.md`。
4. 把研究者画像写入 `00_profile/`。持续维护 `ROADMAP.md`、`README.md`、`state.json`；用
   `python3 <PD_SKILL>/scripts/pd.py status --root <project-root>` 恢复精简上下文；仅在确需完整决策和路线图时加 `--full`。

## Effort 与上下文预算

- `lean`：快速摸底；1 个主分析 + 至多 1 个反方，不做推测性 fan-out。
- `standard`（默认）：先用至多 3 个独立 reasoning passes 收敛；有冲突或红旗再升级。
- `deep`：仅由用户明确要求，或在结论冲突、完整性风险、最终投稿审计时升级；宿主支持多 agent 不等于自动使用。
- 恢复时只读 `pd status` 列出的 context paths。不得递归扫描 `runs/`、原始日志或大型 JSON；先读摘要，再按具体 claim 定向打开路径、哈希对应的证据片段。
- 原始数组和完整日志留在 artifact 文件；常用上下文只保留标量指标、短摘要、路径和 SHA-256。

## Phase 1–10

用 `python3 <PD_SKILL>/scripts/pd.py advance --root <project-root>`（可加 `--to N`）推进阶段。每个 checkpoint 停下等待人工决定。

| Phase | 主流程 | 必须闸门 |
|---|---|---|
| 1 方向与 idea | `paper-digger-ideate`，末尾运行 `paper-digger-evaluate` 节点① | 选 idea |
| 2 选刊/会 | `paper-digger-venue`，记录官方模版状态 | 选 venue |
| 3 文献深挖 | 宿主可用的学术检索/深度研究 skill；无则用内置检索工具并建立可核验 gap map | 来源可追溯 |
| 4 计划 | `paper-digger-plan`，指定唯一最小验证 | 批准计划 |
| 5 执行 | `paper-digger-experiment` / `paper-digger-theory`，运行节点②③④ | 证据是否充分 |
| 6 写稿 | 先过模版闸门，再用可用写作/图表 skill；无则按证据库直接起草 | 模版 READY |
| 7 润色 | 可用学术润色 skill；无则逐段做 claim-preserving edit | 不扩大主张 |
| 8 审稿 | 先做一次整体 triage，再对被标红的维度运行独立 reviewer；`deep`/最终审计才跑完整 ensemble | 审稿决定 |
| 9 修改 | 可用 revision skill；无则按问题—证据—改动台账修订，必要时回 Phase 5 | 每轮确认 |
| 10 定稿 | 可用 LaTeX/格式转换/disclosure skill；无则按 venue 官网逐项核验 | 发布前检查 |

## Phase 6 模版闸门

起草前运行 `python3 <PD_SKILL>/scripts/pd.py gate --root <project-root>`：

- `available=false`：没有官方模版，依据 venue 官方指南起草，状态 READY。
- `available=true` 且未验证：状态 BLOCKED。用宿主网页工具从 venue 官网取得模版到 `06_manuscript/template/`，核对版本和 track。
- 核对完成后运行 `python3 <PD_SKILL>/scripts/pd.py gate --verify --root <project-root>`。

网页工具不可用时，记录具体 URL/待核验项并保持 BLOCKED；不得把搜索摘要或第三方模版当成官方模版。

## 委托和降级

- 只探测**当前阶段所需**的能力，并选一个主执行 skill/tool；不要枚举或加载全部宿主能力。
- 仅当路线不明确或主能力缺失时，读取 [references/delegation.md](references/delegation.md)。
- effort 预算允许且任务确实独立时，才把检索、红队或实验单元放进隔离上下文。
- 宿主不支持 subagent 时，按同一 rubric 依次运行独立 lens，并明确重置假设；流程不能因此停止。
- 上游产物是下游唯一输入边界：confirmed idea、confirmed venue、verified evidence、evaluation verdict。

## Phase 9 修改循环

1. 用 `paper_digger.loop.record_review_round(workspace, decision, notes=...)` 记录本轮；`decision` 为 `accept|minor_revision|major_revision|reject`。
2. 用 `paper_digger.loop.needs_more_experiments(decision)` 判断是否补实验。
3. 若需补实验，用 `paper_digger.loop.loop_back_to_experiments(workspace)` 回 Phase 5，重跑相关实验和评价节点③/④，再复审。
4. `accept` 才进入 Phase 10；`reject` 在 checkpoint 由人决定 pivot 或换 venue。

## 铁律

- **Checkpoint-gated**：选 idea、选 venue、批计划、证据充分性、审稿决定和每轮修改必须人工确认。
- **反捏造**：结果只能来自真实运行或用户数据；引用必须可核验；未证步骤必须标为 conjecture。
- **无必需 API/MCP**：外部 API、MCP、SSH 和专用 skill 都是可选增强；缺失时按明确的本地降级路径执行。
- **不伪装完成**：无网页、算力、数据、伦理许可或官方模版时，写清 blocker 和下一步，不虚构通过。
