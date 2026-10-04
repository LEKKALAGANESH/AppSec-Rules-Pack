"""Record real validation output for the README demo from the repository root."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

from rich.console import Console

ROOT = Path(__file__).resolve().parents[2]
COMMANDS = (
    (["validate", "rules", "--require-examples", "--fail-on-warnings"], 0),
    (["validate", "tests/fixtures/fail/missing-required-field.yaml"], 1),
)


def main() -> None:
    console = Console(record=True, width=100, color_system=None)
    env = {**os.environ, "NO_COLOR": "1", "PYTHONPATH": str(ROOT / "src")}
    for args, expected_code in COMMANDS:
        console.print("$ python -m appsec_rules_pack " + shlex.join(args), markup=False)
        result = subprocess.run(
            [sys.executable, "-m", "appsec_rules_pack", *args],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        console.print(result.stdout, end="", markup=False, highlight=False)
        console.print(f"[exit {result.returncode}]\n", markup=False)
        if result.returncode != expected_code:
            raise SystemExit(f"Unexpected exit code: {result.returncode}")
    svg = console.export_svg(title="AppSec Rules Pack CLI")
    # Remove insignificant XML whitespace; captured CLI text is unchanged.
    svg = "\n".join(line.rstrip() for line in svg.splitlines()) + "\n"
    (ROOT / "docs/assets/cli-demo.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
