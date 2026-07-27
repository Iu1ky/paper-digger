# Paper Digger repository instructions

The canonical distributable is `plugins/paper-digger/`.

- Keep every reusable workflow in `plugins/paper-digger/skills/*`; do not add a
  second copy under `.agents`, `.claude`, or another host-specific directory.
- Keep the Python package under
  `plugins/paper-digger/skills/paper-digger/scripts/paper_digger/` so a copied
  Agent Skill remains self-contained.
- Product-specific files may only be thin manifests or UI metadata.
- Preserve checkpoint gates and evidence boundaries. Never weaken a blocker to
  make a test or demo look complete.
- Run `uv run pytest -q`, Ruff, Black, `scripts/check_release.py`, the Agent
  Skills validator, and both plugin validators before release.
- Use the tagged GitHub repository as the default installer source so
  `gh skill update` retains stable provenance. `--from-local` is only for
  development checks.
- Do not edit `dist/`; regenerate it with `scripts/build_release.py`.
