"""The rules pack printed in the README must actually validate.

A new user's only path to authoring a pack is the example in the README: the schema
describes the contract but not in a copyable form, and the baseline pack is 19 rules
long. An example that drifts out of sync with the schema sends every new user into the
same wall of validation errors, and nothing else in the suite would notice.

The example is delimited by an HTML marker so this test binds to the intended block
rather than to whichever fenced YAML happens to come first.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from appsec_rules_pack.validator import validate_rules_payload

README = Path("README.md")
MARKER = "<!-- readme-example:minimal-pack"

# The marker line, then the next ```yaml ... ``` fence.
EXAMPLE_PATTERN = re.compile(
    re.escape(MARKER) + r"[^\n]*\n\s*```yaml\n(?P<body>.*?)\n```",
    re.DOTALL,
)


@pytest.fixture(scope="module")
def example_pack() -> dict:
    text = README.read_text(encoding="utf-8")
    match = EXAMPLE_PATTERN.search(text)
    assert match is not None, (
        f"README lost the '{MARKER}' marker or its yaml block. The example is a "
        "documented contract; move the marker with it rather than deleting it."
    )
    payload = yaml.safe_load(match.group("body"))
    assert isinstance(payload, dict)
    return payload


def test_readme_example_pack_validates_cleanly(example_pack: dict) -> None:
    result = validate_rules_payload(example_pack)

    assert result.ok, [f"{issue.level} {issue.path}: {issue.message}" for issue in result.issues]
    assert result.rule_count == 1
    assert result.warning_count == 0


def test_readme_example_pack_survives_require_examples(example_pack: dict) -> None:
    """`--require-examples` is what CI runs, so the documented pack must not trip it.

    The minimal pack ships no `examples` block, so this documents the expected outcome:
    a warning, not an error, and only under the opt-in flag.
    """

    result = validate_rules_payload(example_pack, require_examples=True)

    assert not any(issue.level == "error" for issue in result.issues)
