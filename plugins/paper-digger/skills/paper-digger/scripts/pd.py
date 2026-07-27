#!/usr/bin/env python3
"""Run Paper Digger directly from an installed Agent Skill."""

from __future__ import annotations

import sys
from pathlib import Path

SKILL_SCRIPTS = Path(__file__).resolve().parent
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))

from paper_digger.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
