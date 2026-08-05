"""How the derivation-only exports behave on malformed or partial packs.

`export sarif`, `export semgrep`, and `report coverage` derive from pack metadata
without running schema validation first, so they can be pointed at a pack that
`validate` would reject. These tests pin down what they produce in that case, so the
degradation stays deliberate: the exports skip what they cannot read and fall back to
documented defaults instead of raising or inventing content.
"""

from __future__ import annotations

from typing import Any

from appsec_rules_pack.reporter import build_coverage
from appsec_rules_pack.sarif_export import build_sarif
from appsec_rules_pack.semgrep_scaffold import build_semgrep_scaffold


def _pack(rules: Any, version: Any = "1.0.0") -> dict[str, Any]:
    return {"pack": {"id": "degraded", "version": version}, "rules": rules}


def _driver(document: dict[str, Any]) -> dict[str, Any]:
    return document["runs"][0]["tool"]["driver"]


# --- SARIF -----------------------------------------------------------------------


def test_sarif_skips_payloads_whose_rules_are_not_a_list() -> None:
    document = build_sarif([_pack("not-a-list"), _pack(None), "not-even-a-mapping"])

    assert _driver(document)["rules"] == []
    # A catalog with no descriptors is still a valid SARIF document with no results.
    assert document["runs"][0]["results"] == []


def test_sarif_tool_version_falls_back_when_no_pack_declares_one() -> None:
    document = build_sarif([_pack([], version=None), {"rules": []}])

    assert _driver(document)["version"] == "0.0.0"


def test_sarif_descriptor_degrades_on_a_rule_missing_optional_metadata() -> None:
    rule = {"id": "APPSEC-X-001", "title": "t", "description": "d", "status": "enabled"}

    descriptor = _driver(build_sarif([_pack([rule])]))["rules"][0]

    # No category and no CWE list means the only tag left is the constant one.
    assert descriptor["properties"]["tags"] == ["security"]
    # An unknown severity must not invent a security-severity score...
    assert "security-severity" not in descriptor["properties"]
    # ...and must fall back to the documented default level.
    assert descriptor["defaultConfiguration"]["level"] == "warning"


def test_sarif_ignores_non_list_cwe_mappings() -> None:
    rule = {
        "id": "APPSEC-X-002",
        "status": "enabled",
        "category": "configuration",
        "severity": "high",
        "mappings": {"cwe": "CWE-16"},
    }

    descriptor = _driver(build_sarif([_pack([rule])]))["rules"][0]

    assert descriptor["properties"]["tags"] == ["security", "configuration"]
    assert "cwe" not in descriptor["properties"]
    assert descriptor["properties"]["security-severity"] == "8.0"


# --- Semgrep scaffold ------------------------------------------------------------


def test_semgrep_scaffold_skips_payloads_whose_rules_are_not_a_list() -> None:
    scaffold = build_semgrep_scaffold([_pack("not-a-list"), _pack(None), 42])

    assert scaffold == {"rules": []}


# --- Coverage report -------------------------------------------------------------


def test_coverage_treats_a_non_mapping_mappings_field_as_uncovered() -> None:
    rules = [{"id": "APPSEC-X-003", "mappings": "not-a-mapping"}]

    coverage = build_coverage([_pack(rules)])

    assert coverage["rules"] == 1
    assert coverage["frameworks"]["cwe"]["covered"] == 0
    assert coverage["frameworks"]["cwe"]["missing"] == ["APPSEC-X-003"]
