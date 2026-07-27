#!/usr/bin/env python3
"""Build a deterministic standalone plugin archive."""

from __future__ import annotations

import argparse
import hashlib
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "paper-digger"
EXTRA_FILES = ("LICENSE", "PRIVACY.md", "TERMS.md", "SECURITY.md")
FIXED_TIME = (2026, 7, 27, 0, 0, 0)


def add_bytes(
    archive: zipfile.ZipFile, name: str, data: bytes, executable: bool
) -> None:
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    mode = 0o755 if executable else 0o644
    info.external_attr = (mode & 0xFFFF) << 16
    archive.writestr(info, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = project["project"]["version"]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = args.output_dir / f"paper-digger-plugin-{version}.zip"
    sums_path = args.output_dir / "SHA256SUMS"

    for path in (archive_path, sums_path):
        if path.exists():
            path.unlink()

    with zipfile.ZipFile(archive_path, "w") as archive:
        for path in sorted(PLUGIN.rglob("*")):
            if (
                not path.is_file()
                or "__pycache__" in path.parts
                or any(part.endswith(".egg-info") for part in path.parts)
                or path.suffix in {".pyc", ".pyo"}
                or path.name == ".DS_Store"
            ):
                continue
            relative = Path("paper-digger") / path.relative_to(PLUGIN)
            executable = relative.as_posix().endswith("/scripts/pd.py")
            add_bytes(archive, relative.as_posix(), path.read_bytes(), executable)
        for name in EXTRA_FILES:
            add_bytes(
                archive,
                (Path("paper-digger") / name).as_posix(),
                (ROOT / name).read_bytes(),
                False,
            )

    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    sums_path.write_text(f"{digest}  {archive_path.name}\n", encoding="utf-8")
    print(archive_path)
    print(sums_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
