# Paper Digger plugin

This directory is a self-contained Codex plugin, Claude Code plugin, and Gemini
CLI extension. It includes seven portable Agent Skills, one research-agent
definition, and a zero-dependency Python runtime.

From a clone of the repository:

```bash
# Local Codex marketplace
codex plugin marketplace add .
codex plugin add paper-digger@paper-digger

# Local Claude marketplace
claude plugin marketplace add .
claude plugin install paper-digger@paper-digger

# Gemini extension
gemini extensions install ./plugins/paper-digger
```

The main skill is `skills/paper-digger/SKILL.md`. It locates its runtime at
`skills/paper-digger/scripts/pd.py`, so installing or copying the skills does
not require a separate Python package.

The runtime defaults to bounded `standard` effort and compact status output.
Use `pd status --full` only when the complete roadmap and decision text are
needed; raw logs and large metric arrays stay in artifacts rather than routine
agent context.

Paper Digger has no hosted service or telemetry. See the bundled `PRIVACY.md`,
`TERMS.md`, `SECURITY.md`, and `LICENSE`.
