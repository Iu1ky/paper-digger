---
name: paper-digger-experiment
description: Use when executing an approved experiment plan, recording artifact-backed metrics, and verifying evidence. Triggers on 跑实验, 执行实验, run experiments, evidence bank.
---

# Paper Digger Experiment — 实验执行(Phase 5a)

读 `state.experiments`(由 `paper-digger-plan` 种入,status=`planned`)+ `04_plan/research_plan.md` 的执行顺序,逐个执行,把结果汇入 evidence bank 并**对抗式验证**。**先跑最小验证 → 评价节点② → kill-early**。(SSH 远程算力本版不接,后续 plan 再加。)

## 运行时与宿主适配

定位同级 `paper-digger` skill，并把它的 `scripts/` 加入 Python import path 后调用 `paper_digger.*`。默认用批处理脚本执行同构 runs；只有需要独立改代码或分析且 effort 预算允许时才委托隔离 agent/worktree。任何宿主都必须保留真实命令、退出状态、指标文件和 verifier 结论。

## 三模式(按每个实验的 `mode`)
- **dry(计算型)**:把同构重复实验交给一个可复现批处理脚本；不要为每个 seed/arm 启动 agent。每个单元都要**真写真跑**,回报 `{command, metrics, success, notes}`。
- **wet(物理/湿/人类受试)**:不亲自跑 —— 产出 protocol + 对照/power + pre-registration + **分析流水线脚本**;用户执行回传数据后再分析。
- **theory**:转交 `paper-digger-theory`(Phase 5b)。

## 流程(每个实验)
1. `paper_digger.experiment.start_run(workspace, exp_id)` → status `running`,建 `05_experiments/runs/<exp_id>/`。
2. 按 mode 执行,把结果交 `paper_digger.experiment.record_run(workspace, exp_id, result)` → 写 `result.md` + 追加 `evidence_bank.md`,status `awaiting_verification`。
3. 先运行确定性 verifier（退出状态、schema、hash、样本数、泄漏检查）。对最小验证、异常结果、代码/数据变更或支撑核心 claim 的结果，再用一个独立 adversarial verifier lens；普通重复 run 复用同一验证协议，不重复全文审阅。随后调用 `paper_digger.experiment.record_verification(workspace, exp_id, verdict)` → status `verified` 或 `refuted`。

## 评价节点 ②③④(研究期红队)
- 跑完**最小验证**(`is_min_validation`)→ **节点②**(`paper-digger-evaluate` node=2,重 A5 证据 / B1 伪造 / B2 方法虚构)→ kill-early:RED 强烈建议停。
- 阶段性成果 → **节点③**;全部完成 → **节点④**(进入写作前的 go/no-go)。

## 铁律
- **结果只来自真实运行或用户数据** —— 绝不编造 metrics(对应 B1 数据伪造)。
- 进 evidence bank 的结果必须过对抗式验证;`refuted` 的结果**不得**用于写作。
- 大数组、预测和完整日志只写 artifact；evidence bank 只记指标摘要、相对路径和 SHA-256。
- 按依赖序执行;**最小验证未 `verified` 前不铺开后续实验**。
