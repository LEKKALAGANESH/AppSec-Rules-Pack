"""Packaging checks for distribution readiness."""

from __future__ import annotations

from pathlib import Path

from helpers import run_python

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_package_builds_wheel(tmp_path: Path) -> None:
    result = run_python(
        ["-m", "build", "--outdir", str(tmp_path), str(REPO_ROOT)],
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    wheels = list(tmp_path.glob("*.whl"))
    assert len(wheels) == 1
    assert wheels[0].name.startswith("appsec_rules_pack-")
