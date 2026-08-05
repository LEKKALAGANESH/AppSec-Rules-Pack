"""An unwritable `--output` must produce an actionable error, not a traceback.

Found by exploratory testing: pointing `--output` at an existing directory escaped as a
raw Python traceback (PermissionError on Windows, IsADirectoryError on POSIX). A user
running the documented regeneration command in CI would get a stack trace instead of a
message naming the path and the reason.

Every command that writes a file is covered, so a new writing command cannot quietly
reintroduce the raw failure.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from appsec_rules_pack.cli import app

runner = CliRunner()

PASS_FIXTURES_DIR = Path("tests/fixtures/pass")

WRITING_COMMANDS: list[tuple[str, list[str]]] = [
    ("export-index", ["export", "index", str(PASS_FIXTURES_DIR)]),
    ("export-semgrep", ["export", "semgrep", str(PASS_FIXTURES_DIR)]),
    ("export-sarif", ["export", "sarif", str(PASS_FIXTURES_DIR)]),
    ("report-coverage", ["report", "coverage", str(PASS_FIXTURES_DIR), "--format", "json"]),
]
COMMAND_IDS = [name for name, _ in WRITING_COMMANDS]


@pytest.mark.parametrize(("name", "argv"), WRITING_COMMANDS, ids=COMMAND_IDS)
def test_output_pointing_at_a_directory_fails_cleanly(
    name: str, argv: list[str], tmp_path: Path
) -> None:
    target = tmp_path / "already-a-directory"
    target.mkdir()

    result = runner.invoke(app, [*argv, "--output", str(target)])

    assert result.exit_code == 1
    assert "Write failed: cannot write to" in result.output
    assert str(target) in result.output
    # The point of the fix: the user sees a message, not an interpreter dump.
    assert "Traceback" not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)


def test_successful_write_still_reports_the_original_message(tmp_path: Path) -> None:
    """The error path must not have changed the success contract."""

    out = tmp_path / "nested" / "index.json"

    result = runner.invoke(app, ["export", "index", str(PASS_FIXTURES_DIR), "--output", str(out)])

    assert result.exit_code == 0
    assert "Wrote index for 1 file to" in result.output
    assert out.read_bytes()
