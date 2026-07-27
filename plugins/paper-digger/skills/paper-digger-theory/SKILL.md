---
name: paper-digger-theory
description: Use when deriving or proving theoretical results — building an assumptions ledger, decomposing into lemmas, proving each step (or flagging it a conjecture), and validating with numerical/symbolic checks and counterexample search. Triggers on 理论推导, 证明, 定理, derivation, theorem, proof, lemma, 假设台账, 理论验证, theory.
---

# Paper Digger Theory — 理论推导(Phase 5b)

读 plan 的理论目标,做**结构化推导**并**验证**。无 hand-waving —— 每一步要么 `proven`,要么显式标 `conjecture`,没有第三种。

## 运行时与并行

定位同级 `paper-digger` skill，把它的 `scripts/` 加入 Python import path 后调用 `paper_digger.theory.*`。默认先完成一条主推导路线；仅在推导卡住、结论脆弱、反例出现、`deep` 或用户明确要求时，再从同一假设台账启动独立替代路线。

## 推导
- **假设台账(assumptions ledger)**:把所有前提显式列成 `{id, statement}`;之后每一步只能依赖台账里的假设。
- **引理分解**:把目标拆成引理/步骤,每步 `{id, statement, justification, status: proven|conjecture}`。
- **按需多路线**:先走最直接路线；触发升级条件后才探索替代路线并比较。

## 验证(对抗式)
- 数值/符号 sanity check(如 sympy);**反例搜索**(Devil's advocate 主动找反例);与已知**极限/特例**一致性。
- 每条验证记 `{check, passed, notes}`。

## 流程
1. `paper_digger.theory.save_derivation(workspace, assumptions, steps)` —— 内部 `validate_derivation`(每步必有 `proven|conjecture` status,无 hand-waving;id 唯一),写 `05_theory/assumptions_ledger.md` + `05_theory/derivations.md`(并标出仍 open 的 conjecture)。
2. `paper_digger.theory.record_validation(workspace, validations)` —— 写 `05_theory/validation.md`。
3. `unproven_steps` 仍为 `conjecture` 的步骤,在 checkpoint / 写作中**显式标注为未证**,不得当成定理。

## 铁律
- **不许 hand-waving**:每步 `proven` 或显式 `conjecture`;没有第三种。
- conjecture 进写作必须**显式标注未证**,不得伪装成已证定理。
- 推导只依赖**假设台账**里列出的前提;新前提先进台账。
