# CI Integration Example

This template shows how a downstream repository can validate an AppSec rules
directory in GitHub Actions.

Pin `appsec-rules-pack` to a reviewed release version before using it in a production
quality gate.

```yaml
name: Validate AppSec Rules

on:
  pull_request:
  push:
    branches: [main, master]

permissions:
  contents: read

jobs:
  appsec-rules:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Check out repository
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
        with:
          persist-credentials: false

      - name: Set up Python
        uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6
        with:
          python-version: "3.12"

      - name: Install AppSec Rules Pack
        run: python -m pip install "appsec-rules-pack==0.3.1"

      - name: Validate rules
        run: appsec-rules validate rules --require-examples --fail-on-warnings --format json
```

For local development inside this repository, install the project in editable mode
and validate the bundled baseline rules:

```bash
python -m pip install -e ".[dev]"
python -m appsec_rules_pack validate rules --require-examples --fail-on-warnings --format json
```

Both examples apply the repository's strict validation flags: enabled rules need
compliant and violating examples, and warnings produce a failing exit code.
`tests/test_documented_gates.py` executes these documented commands against valid,
missing-example, and warning cases to keep the examples aligned with that contract.
