---
name: paper-digger-evaluate
description: Use when judging whether research work is worth continuing — at idea-confirmation, after minimal validation, at preliminary results, or at final results — scoring value/novelty/logic/level and screening for data fabrication, method fiction, citation hallucination, and fixed thinking. Triggers on 评价节点, 价值评估, 是否值得做, 是否低水平, 诚信稽核, research red-team, kill-early, go/no-go.
---

# Paper Digger Evaluate — 研究期价值与诚信红队

在 4 个节点对「当前工作」做**对抗式、多维度**评价,回答:*这值得做/做得够好吗?* 和 *我们是不是在自欺/造假?* —— 输出可执行 verdict。**区别于** Phase 8 的投稿期外部审稿模拟,这是**研究期内部红队**。

## 运行时

定位同级 `paper-digger` skill。调用 `paper_digger.*` API 前，把它的 `scripts/` 目录加入 Python `sys.path` 或 `PYTHONPATH`；不要依赖全局安装。向 lens 只提供 claim、指标摘要、路径、哈希和必要片段，不内联原始日志或大数组。

## 两轴 rubric

**Axis A — 价值与水平**
- A1 价值/意义("so what?",抓无意义的工作)· A2 新颖性(抓低水平/增量)· A3 严谨与逻辑(抓逻辑问题)· A4 水平/雄心 · A5 证据充分性(随节点)

**Axis B — 诚信与认知失效**
- B1 数据伪造 · B2 方法虚构 · B3 引用幻觉 · B4 思维固定(主动生成 ≥2 个反框架/竞争解释,检验 tunnel vision)

## 4 个节点(逐节点换侧重,见 `NODE_FOCUS`)

- 节点 ① idea 确定:重 A1 价值 / A2 新颖 / B4 思维固定 → 立项 / 改框架 / 换题
- 节点 ② 最小验证完成:重 A5 证据 / B1 伪造 / B2 方法虚构 → 继续 / 修正 / kill-early
- 节点 ③ 初步成果:重 A3 逻辑 / A4 水平 / B1 / B3 → 继续 / 补实验 / 重定位
- 节点 ④ 最终成果:全轴审计 + "so what?" 终检 → 进入写作 / 返工 / 放弃

## 执行流程

1. 读取节点的 `NODE_FOCUS` 维度,确定本轮重点。
2. 按 effort 运行对抗式 lens:
   - `lean`:先跑 1 个综合 lens；节点②/④或出现诚信信号时至少再跑 1 个独立 integrity lens。
   - `standard`:默认 2 个独立 lens（价值/证据、诚信/反框架）。
   - `deep`:仅在节点④、verdict 冲突、诚信红旗或用户明确要求时扩展到 novelty、rigor、integrity、fixed-thinking 4 个 lens。
   每个 lens 使用 fresh context、默认怀疑并产出 `{lens, axis: A|B, verdict: GREEN|YELLOW|RED, must_fix: [...], rationale}`。
3. 汇总并落盘:用 `paper_digger.evaluate.record(workspace, node, lens_verdicts, now=...)` —— 它做 `aggregate`(worst-of + 任一 Axis-B RED 置 `blocking_integrity`),写 `08_evaluation/eval_node<N>.md`,并把 verdict 追加进 `state.json` 的 `evaluations[]`。
4. 在 checkpoint 呈现 verdict + 必修项。**RED 不自动 kill**,由人拍板(GREEN 通过 / YELLOW 带必修项继续 / RED 强烈建议 pivot 或 kill)。

## 铁律

- 评价 lens 必须**独立、对抗**,不得附和「我们很看好」的框架(避免自评盲点)。
- 任一 Axis-B(诚信)RED 即 `blocking_integrity`,必须在 checkpoint 显著标出。
- 结论只依据真实证据(`evidence/` + verification);不臆测、不放水。
