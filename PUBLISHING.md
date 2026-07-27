# Publishing Paper Digger

## Release gate

From a clean worktree:

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check .
uv run black --check .
python scripts/check_release.py
gh skill publish --dry-run
claude plugin validate --strict plugins/paper-digger
python scripts/build_release.py
```

Inspect `dist/SHA256SUMS` and install the archive into a temporary location
before tagging. When developing inside Codex, also run the bundled
`plugin-creator` validator against `plugins/paper-digger`.

## GitHub and Agent Skills

`gh skill publish --tag v0.1.2` validates the skills, adds the
`agent-skills` repository topic when approved, and creates the GitHub release.
Upload the generated plugin archive and `SHA256SUMS` to that release.

The release tag, Python package version, Codex manifest, Claude manifest,
Gemini manifest, and both marketplace entries must match.

## PyPI

Configure PyPI Trusted Publishing for the GitHub repository before the first
upload. Build with `uv build`, inspect both artifacts, then publish with
`uv publish` or the official PyPI publish action. PyPI distributes the optional
`pd` CLI; the GitHub release and marketplaces distribute the Agent Skills.

## Codex public directory

The repository is already a local Codex marketplace. Public-directory
submission still requires the publisher's verified OpenAI developer/business
identity, public website/privacy/terms URLs, a skills ZIP, starter prompts, and
activation tests. Form-ready cases live in
`release/activation-cases.json`.

## Claude and Gemini listings

- Claude Code users can add this GitHub repository as a marketplace directly.
  Submit the repository to any official community listing only after the tag is
  live.
- The Gemini extension root is `plugins/paper-digger/`. Test that directory
  locally before submitting it to the Gemini CLI extension gallery.

Never publish from an uncommitted worktree or reuse a tag for different bytes.
