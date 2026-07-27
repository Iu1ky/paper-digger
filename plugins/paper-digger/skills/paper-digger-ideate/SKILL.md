---
name: paper-digger-ideate
description: Use when finding or choosing a research direction or idea from scratch — generating candidate ideas from multiple angles, scoring them on novelty/feasibility/impact/fit, and converging to one or two to pursue. Triggers on 方向确定, idea发掘, 选题, 找研究方向, 确定idea, research ideation, brainstorm research ideas, what should I work on.
---

# Paper Digger Ideate — 方向确定与 idea 发掘(Phase 1)

模糊前端:从研究者画像出发,**发散**生成候选 idea,**收敛**到 1–2 个值得做的。确定前必须跑**评价节点①**(paper-digger-evaluate),再由人在 checkpoint 拍板。

## 运行时与检索

定位同级 `paper-digger` skill，把它的 `scripts/` 加入 Python import path 后调用 `paper_digger.*`。使用宿主可用的网页/学术检索工具并优先原始论文、官方索引和 DOI；没有网页能力时，不做新颖性确认，只输出待检索问题和 blocker。

## 输入
研究者画像(领域、兴趣、约束:算力?湿实验?时间?目标档次),来自 `00_profile/` 或现问。

## 发散(独立多角度)
按 `state.effort` 选择预算；不要仅因宿主支持 subagent 就全量并行:
- `lean`:2 个差异最大的 lens，最多 4 张卡。
- `standard`:3 个 lens，最多 6 张卡。
- `deep`:仅在用户明确要求、top 候选接近或新颖性未决时使用全部 5 个 lens。

可选 lens:
- gap-driven(文献空白)· method-transfer(他领域方法迁移)· cross-disciplinary(交叉)· contrarian(反主流假设)· trend-driven(新兴趋势)

用宿主网页/学术检索能力落地;有学术 API(见 `state.capabilities`)时增强。每个候选产出一张 **idea card**:
`{id, one_liner, novelty_claim, why_now, required_evidence, feasibility_note, risk, scores: {novelty, feasibility, impact, fit}}`(各 0–5)。

## 收敛
1. 打分排序:`paper_digger.ideate.save_idea_cards(workspace, cards)` —— 内部 `rank_ideas` 按 NFIF 加权(`NFIF_WEIGHTS`),写 `01_ideation/idea_cards.md`。
2. 用一次 Devil's-advocate 复核 top 候选:真的新吗?是否已被做过?是否非真问题?
3. **评价节点①**:对 top 1–2 候选跑 `paper-digger-evaluate`(node=1,重 A1 价值 / A2 新颖 / B4 思维固定),拿 verdict。
4. **checkpoint**:呈现排序 + verdict + 必修项,**由人选定** 1(或 2)个。
5. 落定:`paper_digger.ideate.confirm_idea(workspace, idea_id, summary=...)` —— 写 `01_ideation/confirmed_idea.md` 并置 `state.decisions.idea`。

## 铁律
- **不臆造**:新颖性主张要有文献依据;拿不准就标注、去查,绝不编。
- **节点①必过**:确定 idea 前必须跑评价;RED 强烈建议换框架/换题(人拍板)。
- 发散阶段保持多样性,避免一上来锚定单一框架(对应 B4 思维固定)。
