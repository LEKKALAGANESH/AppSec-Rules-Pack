"""Shared helpers for tests that shell out to a child Python process.

Decoding child output with the platform's locale encoding is not portable. On
Windows the parent decodes as cp1252 while the child may emit UTF-8 (for example
when ``PYTHONIOENCODING`` is set in the environment, or when Rich draws its help
panels with box-drawing characters). ``subprocess.run(text=True)`` then raises
``UnicodeDecodeError`` inside its reader thread, silently leaves ``stdout`` as
``None``, and turns a real assertion into a confusing ``TypeError``.

``run_python`` pins UTF-8 on both ends so the decode result never depends on the
machine's locale.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run_python(
    args: list[str],
    *,
    cwd: Path | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run ``python <args>`` and capture its output as UTF-8 text.

    The child is told to emit UTF-8 and the parent is told to decode UTF-8, so the
    round trip is deterministic on every platform. Undecodable bytes are replaced
    rather than raising, so a test failure reports the assertion that actually
    failed instead of an encoding error.
    """

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    if extra_env:
        env.update(extra_env)

    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        check=False,
        cwd=cwd,
        env=env,
        encoding="utf-8",
        errors="replace",
    )
