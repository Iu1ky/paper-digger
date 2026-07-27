# Changelog

All notable changes to Paper Digger are documented here.

## [0.1.3] - 2026-07-27

- Retry transient GitHub install failures up to six times with bounded
  exponential backoff.
- Suppress repeated network error payloads during retry to keep install logs
  compact.
- Document pinned-release upgrade and unpin behavior.

## [0.1.2] - 2026-07-27

- Reduce projected always-on Claude plugin context from about 669 to 386
  tokens by tightening trigger metadata without merging phase-specific skills.
- Enforce a 300-character release budget for every skill description.

## [0.1.1] - 2026-07-27

- Bound model fan-out with lean, standard, and deep effort modes.
- Add compact resume context and artifact-backed metric summaries.
- Pin all cross-agent installs to one resolved release and retry transient
  network failures.

## [0.1.0] - 2026-07-27

### Added

- Seven Agent Skills covering orchestration, ideation, venue selection,
  planning, experiments, theory, and research-time evaluation.
- Self-contained zero-dependency Python runtime and `pd` CLI.
- Codex and Claude Code plugin manifests and marketplaces.
- Gemini CLI extension and portable research-agent definition.
- GitHub CLI installation path for mainstream coding agents.
- Release validation, deterministic plugin archive, CI, privacy, security, and
  publishing documentation.
