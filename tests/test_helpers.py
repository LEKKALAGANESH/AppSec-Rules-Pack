"""Regression tests for the subprocess helper's encoding contract.

These guard a real defect: decoding child output with the platform locale encoding
made the suite fail on Windows (cp1252) whenever the child emitted UTF-8. The
failure was doubly bad because ``subprocess.run`` swallowed the decode error in its
reader thread and left ``stdout`` as ``None``, so the reported error pointed at the
assertion instead of the encoding mismatch.
"""

from __future__ import annotations

from helpers import run_python

# Box-drawing characters are what Rich draws around Typer's help panels, and what
# actually broke cp1252 decoding in practice.
BOX_DRAWING = "┌─┐"


def test_run_python_round_trips_non_ascii_output() -> None:
    result = run_python(["-c", f"print({BOX_DRAWING!r})"])

    assert result.returncode == 0, result.stderr
    assert BOX_DRAWING in result.stdout


def test_run_python_never_returns_none_streams() -> None:
    """A decode failure must not silently degrade a stream to ``None``."""

    result = run_python(["-c", "print('\\u2500' * 40)"])

    assert isinstance(result.stdout, str)
    assert isinstance(result.stderr, str)
    assert result.stdout.count("─") == 40
