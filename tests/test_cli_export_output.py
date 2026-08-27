"""The CLI `--output` write path for every derived artifact, byte for byte.

The drift tests compare each committed artifact against the in-memory builder, so a
break in the CLI's file-writing path would not fail them: `export semgrep --output`
and `export sarif --output` had no test at all. These tests exercise the documented
regeneration commands instead, and compare raw bytes rather than parsed content,
because a derived artifact should be reproducible on every platform.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from appsec_rules_pack.cli import app

runner = CliRunner()

BASELINE = Path("rules/appsec-baseline.yaml")

EXPORTS: list[tuple[str, Path]] = [
    ("index", Path("exports/appsec-baseline.index.json")),
    ("semgrep", Path("exports/semgrep/appsec-baseline.semgrep.yaml")),
    ("sarif", Path("exports/sarif/appsec-baseline.sarif.json")),
]
EXPORT_IDS = [command for command, _ in EXPORTS]


@pytest.mark.parametrize(("command", "committed"), EXPORTS, ids=EXPORT_IDS)
def test_export_output_matches_committed_artifact_byte_for_byte(
    command: str, committed: Path, tmp_path: Path
) -> None:
    # A nested target also covers the parent-directory creation in the write path.
    out = tmp_path / "nested" / committed.name

    result = runner.invoke(app, ["export", command, str(BASELINE), "--output", str(out)])

    assert result.exit_code == 0, result.output
    assert out.read_bytes() == committed.read_bytes()


@pytest.mark.parametrize("command", EXPORT_IDS)
def test_export_output_is_written_with_lf_endings(command: str, tmp_path: Path) -> None:
    """Path.write_text translates "\\n" to the platform separator unless told otherwise.

    Without an explicit newline the exports came out entirely CRLF on Windows while the
    repository stores LF, so the same command produced different bytes per platform.
    """

    out = tmp_path / "out"

    result = runner.invoke(app, ["export", command, str(BASELINE), "--output", str(out)])

    assert result.exit_code == 0, result.output
    assert b"\r\n" not in out.read_bytes()


def test_report_coverage_output_is_written_with_lf_endings(tmp_path: Path) -> None:
    out = tmp_path / "coverage.json"

    result = runner.invoke(
        app,
        ["report", "coverage", str(BASELINE), "--format", "json", "--output", str(out)],
    )

    assert result.exit_code == 0, result.output
    assert b"\r\n" not in out.read_bytes()


def test_report_coverage_text_format_honors_output(tmp_path: Path) -> None:
    """`--output` without `--format json` used to be silently ignored.

    The text report went to stdout, the exit code stayed 0, and the named file was
    never created — the user believed the report had been saved.
    """

    out = tmp_path / "coverage.txt"

    result = runner.invoke(app, ["report", "coverage", str(BASELINE), "--output", str(out)])

    assert result.exit_code == 0, result.output
    content = out.read_text(encoding="utf-8")
    assert "Mapping coverage for" in content
    assert "owasp_asvs" in content
    # The report body belongs in the file; stdout confirms the write instead.
    assert "Wrote coverage report to" in result.output
    assert "Mapping coverage for" not in result.output
