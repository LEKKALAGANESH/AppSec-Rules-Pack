"""Negative and edge-case tests for safe failure behavior."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from appsec_rules_pack.cli import app
from appsec_rules_pack.validator import validate_rules_file

runner = CliRunner()

VALID_PACK = """\
pack:
  id: edge-pack
  name: Edge Case Pack
  version: 0.1.0
  mode: advisory
  owner: appsec
  description: Minimal valid pack used by edge-case tests.
rules:
  - id: APPSEC-EDGE-001
    title: Minimal valid rule
    description: A minimal but schema-valid rule used to exercise edge cases.
    severity: low
    category: configuration
    status: enabled
    enforcement: advisory
    targets:
      - general
    mappings:
      owasp_asvs:
        - V14.1
      owasp_api_top_10_2023:
        - API8:2023
      cwe:
        - CWE-16
      nist_ssdf:
        - PW.9
    evidence:
      required:
        - Evidence item.
      signals:
        - Signal item.
    match:
      type: review
      includes:
        - Included surface.
      excludes:
        - Excluded surface.
    remediation:
      guidance: Apply the documented secure configuration guidance for this rule.
      validation:
        - Validation step.
    exceptions:
      allowed: true
      max_days: 30
      required_fields:
        - owner
        - justification
        - expires_at
"""


def test_empty_file_fails_without_crashing(tmp_path: Path) -> None:
    target = tmp_path / "empty.yaml"
    target.write_text("\n", encoding="utf-8")

    result = validate_rules_file(target)

    assert not result.ok
    assert result.rule_count == 0
    assert any("expected object" in issue.message for issue in result.issues)


def test_non_mapping_rule_entry_fails_safely(tmp_path: Path) -> None:
    target = tmp_path / "badrule.yaml"
    target.write_text(
        "pack:\n"
        "  id: x\n"
        "  name: Test Pack\n"
        "  version: 0.1.0\n"
        "  mode: advisory\n"
        "  owner: ab\n"
        "  description: short description here\n"
        "rules:\n"
        "  - just-a-string\n",
        encoding="utf-8",
    )

    result = validate_rules_file(target)

    assert not result.ok
    assert any(issue.path == ("rules", 0) for issue in result.issues)


def test_yml_extension_is_recognized(tmp_path: Path) -> None:
    target = tmp_path / "pack.yml"
    target.write_text(VALID_PACK, encoding="utf-8")

    result = runner.invoke(app, ["validate", str(tmp_path)])

    assert result.exit_code == 0
    assert "1 file" in result.output


def test_uppercase_extension_is_recognized(tmp_path: Path) -> None:
    target = tmp_path / "PACK.YAML"
    target.write_text(VALID_PACK, encoding="utf-8")

    result = runner.invoke(app, ["validate", str(tmp_path)])

    assert result.exit_code == 0
    assert "1 file" in result.output


def test_directory_with_valid_and_empty_file_fails(tmp_path: Path) -> None:
    (tmp_path / "valid.yaml").write_text(VALID_PACK, encoding="utf-8")
    (tmp_path / "empty.yaml").write_text("\n", encoding="utf-8")

    result = runner.invoke(app, ["validate", str(tmp_path)])

    assert result.exit_code == 1
    assert "2 files" in result.output
    assert "empty.yaml" in result.output


def test_unparseable_file_does_not_abort_the_rest_of_the_directory(tmp_path: Path) -> None:
    """One malformed file must not stop the others from being validated.

    Directory validation is the documented way to check a rules directory in CI. If a
    YAML syntax error aborted the scan, a single broken file would hide every other
    file's findings and the report would be silently incomplete.
    """

    (tmp_path / "valid.yaml").write_text(VALID_PACK, encoding="utf-8")
    (tmp_path / "broken.yaml").write_text("pack: [unterminated\n", encoding="utf-8")

    result = runner.invoke(app, ["validate", str(tmp_path)])

    assert result.exit_code == 1
    assert "could not parse YAML file" in result.output
    assert "broken.yaml" in result.output
    # The valid file was still parsed and its rule counted, rather than being skipped.
    assert "2 files, 1 rule" in result.output


def test_unparseable_file_is_isolated_in_json_output(tmp_path: Path) -> None:
    import json

    (tmp_path / "valid.yaml").write_text(VALID_PACK, encoding="utf-8")
    (tmp_path / "broken.yaml").write_text("pack: [unterminated\n", encoding="utf-8")

    result = runner.invoke(app, ["validate", str(tmp_path), "--format", "json"])

    assert result.exit_code == 1
    report = json.loads(result.output)
    assert report["summary"] == {
        "files": 2,
        "rules": 1,
        "errors": 1,
        "warnings": 0,
        "ok": False,
    }

    per_file = {entry["path"]: entry for entry in report["files"]}
    assert per_file["valid.yaml"]["rules"] == 1
    assert per_file["valid.yaml"]["errors"] == 0
    assert per_file["broken.yaml"]["errors"] == 1
