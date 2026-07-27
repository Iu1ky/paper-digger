"""Detect available retrieval and compute capabilities.

All detection is injectable so tests stay deterministic. ``websearch`` means
the host agent's built-in web/search capability, not a required external API.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable, Mapping
from typing import Any


def detect(
    env: Mapping[str, str] | None = None,
    which: Callable[[str], str | None] | None = None,
) -> dict[str, Any]:
    env = os.environ if env is None else env
    which = shutil.which if which is None else which
    websearch_env = env.get("PAPER_DIGGER_WEBSEARCH")
    websearch = (
        None
        if websearch_env is None
        else websearch_env.strip().lower() not in {"0", "false", "no", "off"}
    )
    return {
        # Host-native tools cannot be detected reliably from a child process.
        # Keep this unknown until the host or user reports the capability.
        "websearch": websearch,
        "scholar_api": bool(env.get("S2_API_KEY")),  # Tier 1 (optional)
        "exa": bool(env.get("EXA_API_KEY")),  # Tier 2 (optional)
        "firecrawl": bool(env.get("FIRECRAWL_API_KEY")),  # Tier 2 (optional)
        "ssh": which("ssh") is not None,  # optional remote compute
    }
