# Contributing

Contributions are welcome through GitHub issues and pull requests.

1. Fork and clone the repository.
2. Install development dependencies with `uv sync --extra dev`.
3. Keep portable logic under `plugins/paper-digger/`; host adapters must remain
   thin.
4. Add or update tests for behavioral changes.
5. Run the full validation sequence documented in `README.md`.

Research-workflow changes must preserve human checkpoints, provenance, and
claim boundaries. A test passing on synthetic data is not evidence that a
research claim is true.
