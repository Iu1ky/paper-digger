# Paper Digger

Paper Digger 把“从选题到投稿”包装成一套 checkpoint-gated 的 Agent Skills、研究 agent 和零依赖 Python 运行时。核心原则是：先做最便宜的决定性验证，证据不足就缩窄主张或停下，不把演示、草稿或计划冒充研究结果。

The same seven skills run across mainstream coding agents through the open
Agent Skills format. Native manifests are included for Codex, Claude Code, and
Gemini CLI.

## 能做什么

- 从研究者约束出发生成、反驳并确认研究方向。
- 基于官网选择 venue，并把官方模版作为写作前闸门。
- 建立可证伪的假设、实验矩阵和唯一的 kill-early 最小验证。
- 运行 dry experiments，设计 wet protocols，记录理论假设与 conjecture。
- 把只有经过验证的结果收入 evidence bank。
- 在 4 个节点红队审计价值、新颖性、严谨性、诚信和思维固定。
- 维护跨会话 `state.json`、`ROADMAP.md` 与人工 checkpoint。
- 默认采用有界 `standard` effort 和 compact context，避免无收益的全量
  agent fan-out、递归日志扫描及大数组注入上下文。

## 兼容层

| 宿主 | 分发方式 | 内容 |
|---|---|---|
| Codex / ChatGPT | Codex marketplace plugin | 7 skills + 便携运行时 |
| Claude Code | Claude marketplace plugin | 7 skills + `paper-digger` subagent |
| Gemini CLI | Gemini extension（从本地 clone 安装） | 7 skills + preview subagent |
| GitHub Copilot / Cursor / OpenCode | Agent Skills via `gh skill` | 7 skills + 便携运行时 |
| Windsurf / Cline / Roo / Continue / Junie / OpenHands 等 | `gh skill --agent <host>` | 按宿主路径安装同一份 skills |
| 通用 agent / SDK | Agent Skills 规范或 `.agents/skills` | 直接加载 `SKILL.md` |

“兼容”指使用宿主官方发现路径和 Agent Skills 格式；并不表示每个宿主都提供网页检索、并行 subagent、GPU 或付费论文访问。缺失能力会触发 skill 内定义的降级或 blocker。

## 安装

### Codex 原生插件

```bash
codex plugin marketplace add Iu1ky/paper-digger
codex plugin add paper-digger@paper-digger
```

新开一个任务后，用 `$paper-digger` 启动或恢复项目。

### Claude Code 插件

```bash
claude plugin marketplace add Iu1ky/paper-digger
claude plugin install paper-digger@paper-digger
```

可调用 `/paper-digger:paper-digger`，或让 Claude 使用
`paper-digger:paper-digger` agent。

### 任意 GitHub CLI 支持的 coding agent

GitHub CLI 2.90+ 会自动选择每个宿主的正确目录：

```bash
git clone https://github.com/Iu1ky/paper-digger.git
cd paper-digger
./install.sh --agent cursor --scope user
```

把 `cursor` 换成 `github-copilot`、`codex`、`claude-code`、
`gemini-cli`、`opencode`、`windsurf`、`cline`、`roo`、`continue`、
`junie`、`openhands` 或 `universal`。项目级安装示例：

```bash
./install.sh \
  --agent github-copilot \
  --scope project \
  --project-dir /path/to/your-project
```

Windows 可运行同样的 Python 入口：

```powershell
python scripts/install_skills.py --agent cursor --scope user
```

维护者测试未发布改动时可加 `--from-local`；普通用户应保留默认的 GitHub
来源，这样 `gh skill update` 能追踪 tag 和 commit。

也可直接用 `gh skill install Iu1ky/paper-digger` 进入交互式选择。

### Gemini CLI extension

```bash
git clone https://github.com/Iu1ky/paper-digger.git
gemini extensions install ./paper-digger/plugins/paper-digger
```

### 只安装 `pd` CLI

```bash
uv tool install paper-digger
# 或
pipx install paper-digger
```

Agent Skill 已内置同一运行时，因此使用 skill 时不必安装 PyPI 包。

## 最小用法

```bash
pd init --project my-study --field "machine learning" --effort standard --root .
pd status --root .
pd status --full --root .  # 仅在确需完整决策和路线图时
pd advance --root .
pd gate --root .
```

`lean` 用于快速摸底，`standard` 是默认档，`deep` 只在用户明确要求、
结论冲突、完整性风险或最终投稿审计时升级。常规状态输出只给当前阶段和
最小工作集路径；原始日志、预测和大指标数组保留为带 SHA-256 的 artifact。

未安装 CLI 时，skill 会运行自己的
`plugins/paper-digger/skills/paper-digger/scripts/pd.py`。

## 单一源码结构

```text
.agents/plugins/marketplace.json       Codex marketplace
.claude-plugin/marketplace.json        Claude marketplace
plugins/paper-digger/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── gemini-extension.json
├── agents/paper-digger.md
└── skills/
    ├── paper-digger/
    │   ├── SKILL.md
    │   ├── references/
    │   └── scripts/paper_digger/
    └── paper-digger-{ideate,venue,plan,experiment,theory,evaluate}/
```

Python 包源码位于主 skill 的 `scripts/` 内；PyPI wheel 和所有 agent
分发渠道使用同一份代码，不维护第二套运行时。

## 开发与验证

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check .
uv run black --check .
python scripts/check_release.py
python scripts/build_release.py
gh skill publish --dry-run
claude plugin validate --strict plugins/paper-digger
```

发布细节见 [PUBLISHING.md](PUBLISHING.md)。隐私、使用边界和漏洞报告分别见
[PRIVACY.md](PRIVACY.md)、[TERMS.md](TERMS.md) 和
[SECURITY.md](SECURITY.md)。

## License

Apache-2.0. See [LICENSE](LICENSE).
