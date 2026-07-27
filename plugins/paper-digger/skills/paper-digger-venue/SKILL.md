---
name: paper-digger-venue
description: Use when choosing a target journal or conference for a confirmed research idea — comparing candidate venues on scope fit, tier, timeline and submission norms, and recording each venue's official template. Triggers on 确认目标期刊, 选刊, 选会议, target venue, which journal, which conference, venue selection, 投稿目标.
---

# Paper Digger Venue — 确认目标期刊/会议(Phase 2)

输入 confirmed idea(`01_ideation/confirmed_idea.md` + `state.decisions.idea`)与领域,输出一个选定的 venue + 其**官方模版信息**(供 Phase 6 模版闸门用)。

## 运行时与来源

定位同级 `paper-digger` skill，把它的 `scripts/` 加入 Python import path 后调用 `paper_digger.venue.*`。使用宿主可用网页工具查 venue 官网、CFP、作者指南和官方模版页；网页能力缺失时保持 `verified=false` 并记录 blocker。

## 候选与分析(prompt-driven)
列出候选 venue(会议 + 期刊),用宿主网页工具抓 CFP / 作者指南 / 模版页;有学术 API(见 `state.capabilities`)时补 venue 元数据。每个候选评估:
- **scope** 契合(idea 与 venue 范围)· **tier** 档次匹配 · **timeline** deadline/周期是否合适 · **readiness** 当前工作离该 venue 的 bar 有多近(各 0–5)
- 录用规范、典型方法与篇幅;并**记录官方模版**:`template = {available, url, format(latex/word/overleaf), verified}`。

每个候选产出一张 candidate dict(四项分数**嵌套在 `scores` 键下**,供 `save_venue_analysis` 用):
`{name, type, scores: {scope, tier, timeline, readiness}, template: {available, url, format, verified}, deadline}`

## 流程
1. 打分排序:`paper_digger.venue.save_venue_analysis(workspace, candidates)` —— 内部 `rank_venues` 按 `FIT_WEIGHTS` 加权,写 `02_venue/venue_analysis.md`(含 template? 列)。
2. 标出不契合点(scope 偏离 / 档次错配 / 来不及 deadline)。
3. **checkpoint**:呈现排序 + 契合分析 + 各 venue 模版可得性,**由人选定**。
4. 落定:`paper_digger.venue.confirm_venue(workspace, venue)` —— 写 `02_venue/confirmed_venue.md`,并把 venue + `template` 存进 `state.venue`、置 `state.decisions.venue`。

## 下游
- `state.venue.template` 喂 **Phase 6 模版闸门**(取得并校验官方模版再起草)。
- venue 名/类型喂 PaperSpine 的 scene 配置与 ARS disclosure 的 venue。

## 铁律
- 不臆造 venue 事实(scope/deadline/模版)—— 一律以官网/CFP 为准,拿不准就标注、去查。
- 选定前必过 checkpoint,由人拍板。
