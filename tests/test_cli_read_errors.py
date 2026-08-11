"""An unreadable rules file must produce an actionable error, not a traceback.

Found by exploratory testing: a rules file that is not valid UTF-8 escaped as a raw
``UnicodeDecodeError`` traceback from every command, and a file that fails YAML parsing
did the same from the export and report commands (``validate`` already reported it).
A user pointing the documented commands at a file saved with the wrong encoding would
get an interpreter dump instead of a message naming the file and the reason.

Every command that reads rule files is covered, so a new reading command cannot
quietly reintroduce the raw failure.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from appsec_rules_pack.cli import app
from appsec_rules_pack.validator import validate_rules_file

runner = CliRunner()

READING_COMMANDS: list[tuple[str, list[str]]] = [
    ("validate", ["validate"]),
    ("export-index", ["export", "index"]),
    ("export-semgrep", ["export", "semgrep"]),
    ("export-sarif", ["export", "sarif"]),
    ("report-coverage", ["report", "coverage"]),
]
COMMAND_IDS = [name for name, _ in READING_COMMANDS]


def _write_non_utf8_pack(tmp_path: Path) -> Path:
    target = tmp_path / "latin1.yaml"
    target.write_bytes(b"pack:\n  id: caf\xe9\n")
    return target


def _write_unparsable_pack(tmp_path: Path) -> Path:
    target = tmp_path / "broken.yaml"
    target.write_text("pack: [unclosed", encoding="utf-8")
    return target


def _write_deeply_nested_pack(tmp_path: Path) -> Path:
    target = tmp_path / "deep.yaml"
    depth = 5000
    target.write_text("pack: " + "[" * depth + "]" * depth + "\n", encoding="utf-8")
    return target


@pytest.mark.parametrize(("name", "argv"), READING_COMMANDS, ids=COMMAND_IDS)
def test_a_non_utf8_file_fails_cleanly(name: str, argv: list[str], tmp_path: Path) -> None:
    target = _write_non_utf8_pack(tmp_path)

    result = runner.invoke(app, [*argv, str(target)])

    assert result.exit_code == 1
    assert "could not decode" in result.output
    # The point of the fix: the user sees a message, not an interpreter dump.
    assert "Traceback" not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)


@pytest.mark.parametrize(("name", "argv"), READING_COMMANDS, ids=COMMAND_IDS)
def test_an_unparsable_yaml_file_fails_cleanly(name: str, argv: list[str], tmp_path: Path) -> None:
    target = _write_unparsable_pack(tmp_path)

    result = runner.invoke(app, [*argv, str(target)])

    assert result.exit_code == 1
    assert "could not parse YAML" in result.output
    assert "Traceback" not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)


@pytest.mark.parametrize(("name", "argv"), READING_COMMANDS, ids=COMMAND_IDS)
def test_a_deeply_nested_file_fails_cleanly(name: str, argv: list[str], tmp_path: Path) -> None:
    """PyYAML's recursive composer raises ``RecursionError`` past ~1000 nesting levels.

    ``RecursionError`` is neither ``OSError`` nor ``yaml.YAMLError``, so a hostile or
    corrupted file escaped as a raw interpreter dump from every command.
    """

    target = _write_deeply_nested_pack(tmp_path)

    result = runner.invoke(app, [*argv, str(target)])

    assert result.exit_code == 1
    assert "nesting depth exceeds the supported limit" in result.output
    assert "Traceback" not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)


def test_validate_reports_a_non_utf8_file_as_a_validation_issue(tmp_path: Path) -> None:
    """The library-level validator returns an issue instead of raising."""

    target = _write_non_utf8_pack(tmp_path)

    validation = validate_rules_file(target)

    assert validation.error_count == 1
    assert validation.rule_count == 0
    assert "could not decode" in validation.issues[0].message
