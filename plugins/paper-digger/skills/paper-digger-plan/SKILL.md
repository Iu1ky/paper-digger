---
name: paper-digger-plan
description: Use when converting a confirmed idea and venue into falsifiable hypotheses, an experiment matrix, dependencies, and one kill-early test. Triggers on 研究计划, 实验矩阵, experiment plan, 最小验证.
---

# Paper Digger Plan — 安排计划(Phase 4)

输入 confirmed idea(`01_ideation/`)+ confirmed venue(`02_venue/`)+ Phase 3 文献 gap map,输出一份研究计划:**假设 → 实验矩阵 → 依赖图 → 里程碑**,并**指定一个最小验证实验**(kill-early)。

## 运行时

定位同级 `paper-digger` skill，把它的 `scripts/` 加入 Python import path 后调用 `paper_digger.plan.*`。不要求系统已安装全局 `pd` 包。

## 实验矩阵
每个实验是一张 dict:
`{id, question, mode: dry|wet|theory, method, success_criteria, deps: [id], est_cost, is_min_validation}`
- **mode**:`dry`(代码/仿真/数据分析,可真跑)· `wet`(物理/湿/人类受试,出 protocol 由人执行)· `theory`(推导)。
- **success_criteria**:这个实验「算成功」的明确判据(避免事后挪动靶子)。
- **deps**:依赖的实验 id(决定执行顺序与可并行集)。
- **is_min_validation**:**恰好一个**实验标 True —— 最便宜、最能证伪核心主张的那个,先跑它,触发评价节点②(kill-early)。

## 流程
1. 从 idea/venue/gap 提炼可证伪的**假设/主张**。
2. 为每个假设设计实验,填实验矩阵;**指定**一个 `is_min_validation`。
3. 校验 + 排序 + 落盘:`paper_digger.plan.save_plan(workspace, hypotheses, experiments)` —— 内部 `validate_matrix`(模式合法、id 唯一、deps 存在、恰好一个最小验证)+ `dependency_order`(拓扑序,有环报错),写 `04_plan/research_plan.md`。
4. **checkpoint**:呈现假设 + 矩阵 + 执行顺序 + 预估成本,**由人批准**。
5. 落定:`paper_digger.plan.confirm_plan(workspace, experiments)` —— 把矩阵种入 `state.experiments`(status=`planned`)、置 `state.decisions.plan_approved`,供 `paper-digger-experiment` 执行。

## 铁律
- **先有判据再做实验**:`success_criteria` 必须在执行前定死。
- **恰好一个最小验证**:它是 kill-early 的触发点;没有就不算计划完成。
- 不臆造可行性:`est_cost`/`mode` 要诚实(算力/湿实验/时间约束见 `00_profile/`)。
