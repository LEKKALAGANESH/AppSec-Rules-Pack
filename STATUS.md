# Project Status

Current state of the project, kept consistent with `README.md`, `ROADMAP.md`, and
`TECHNICAL_SPEC.md`. Release-by-release detail lives in [`CHANGELOG.md`](CHANGELOG.md);
this file describes where the project stands and what is known to be true right now.

## Where it stands

**Released:** `appsec-rules-pack` **0.3.1**, published to PyPI via Trusted Publishing
(OIDC, no long-lived credential). The release workflow publishes the wheel, the sdist, a
CycloneDX SBOM, and `appsec-baseline.yaml` as GitHub Release assets. Its SLSA
build-provenance step covers all four assets. Provenance is verified through GitHub
Artifact Attestations; downloading a release asset alone does not verify it.

**What ships:** a JSON Schema rule contract, a Python 3.12+ validator with a Typer CLI, and
derivation-only export and reporting commands. The distribution contains the validator and
the schema — not the rules; the baseline pack is attached to each release and lives in
[`rules/appsec-baseline.yaml`](rules/appsec-baseline.yaml).

**The baseline pack:** 19 generic rules spanning access control, injection and XSS, SSRF,
authentication, session hardening, secrets, file handling, logging, dependency risk,
configuration, CSRF, webhook integrity, excessive data exposure, mass assignment, open
redirect, and rate limiting. Every rule ships a compliant and a violating example.

**Validator coverage:** JSON Schema validation, duplicate rule IDs within a file and across
a validated directory, exception-window warnings, exception-policy consistency, framework
mapping format checks, rule-lifecycle consistency, and sensitive-value detection. Single-file
and directory validation, `--fail-on-warnings`, `--require-examples`, `--version`, and
`--format json` for CI.

**Derived artifacts:** `export index`, `export semgrep`, and `export sarif` produce the
drift-tested files under [`exports/`](exports/). `report coverage` summarizes mapping
metadata. The Semgrep output is a clearly-labelled non-runnable scaffold and the SARIF
output is a rule catalog with no results; the validator never executes rules or scans code
([ADR-0001](docs/adr/0001-engine-agnostic-validator.md)).

**Repository posture:** public, verified on 2026-10-04. The `master-protection` ruleset
requires one code-owner approval, approval of the latest push, an up-to-date branch, and
fourteen status checks ([ruleset](https://github.com/lucashgrifoni/AppSec-Rules-Pack/rules/17222248)).
An administrator bypass exists; this campaign does not use it. Visibility alone does not
establish that CI passes.

## Verified checks

Measured 2026-10-04 on Linux with Python 3.12.14, from source based on
`8d5d205a92aac5c988cdce90401d3876675b1f55`. Results below describe this documentation
revision; earlier Windows and release checks are historical, not rerun claims.

| Check | Result |
| --- | --- |
| `ruff check .` | Clean |
| `pytest --cov=appsec_rules_pack --cov-report=term-missing` | 149 passed; 97.22% coverage (gate 95%) |
| `validate rules --require-examples --fail-on-warnings` | 1 file, 19 rules, 0 errors, 0 warnings |
| `report coverage rules/appsec-baseline.yaml` | ASVS, API Top 10, CWE, SSDF: 19/19; optional Top 10:2025: 18/19 |
| `exports/` regeneration | All three exports regenerated; byte-comparison drift tests pass |
| `python -m build` | Wheel and source distribution built successfully |
| `twine check` and clean-venv wheel install | Not rerun in this documentation check |
| CLI exit codes | Baseline: 0; missing-title fixture: 1; output recorded in `docs/assets/cli-demo.svg` |
| Repository visibility | Public on 2026-10-04 |
| Remote security CI | Latest measured [Security CI/CD 36372233927](https://github.com/lucashgrifoni/AppSec-Rules-Pack/actions/runs/36372233927), 2026-09-28: failed at CodeQL on `8d5d205`. No fresh passing security run has been verified |
| Remote Scorecard | [Run 36376195346, attempt 2](https://github.com/lucashgrifoni/AppSec-Rules-Pack/actions/runs/36376195346), rerun on 2026-10-04: passed on `8d5d205` |

The v0.3.1 release and prior end-user installation checks are documented in
[`CHANGELOG.md`](CHANGELOG.md). See the README's release-verification instructions for
checking the provenance of a downloaded asset independently.

## Performance and capacity

Validation cost is linear in the number of rules — roughly constant per-rule work, with no
super-linear step as packs grow. The JSON Schema is compiled once and reused (`lru_cache`),
duplicate-ID detection is a single hash-map pass, and repeated validation shows no heap
growth (measured stable over 2000 in-process runs). A pack of a few thousand rules validates
in well under a second in-process; the CLI adds fixed Python-interpreter start-up on top.
Any realistic rules pack sits far inside a CI quality-gate budget, so the pack size is not a
practical constraint. These are relative characteristics, not a per-machine benchmark.

## Risks and limits

- Cross-file duplicate ID detection applies only when validating a directory containing two
  or more YAML rule packs. Single-file validation stays file-local.
- The rule model is generic and review-oriented. The pack does not execute rules or scan
  code in any engine; the Semgrep scaffold carries placeholder patterns and the SARIF export
  has an empty `results` array.
- Negative fixtures deliberately assert message stability, so changing a validator message
  means updating its tests and CLI expectations together.
- Framework mapping format checks are warnings rather than errors, so an unusual but valid
  identifier is never blocked. Review warnings when contributing.
- Framework mappings are evidence aids for review, not a claim of conformance. They are
  assigned by topic; see `CONTRIBUTING.md` for the convention.
- `owasp_top_10_2025` is optional. `APPSEC-FILE-001` remains unmapped after the topic
  review below; `APPSEC-RATELIMIT-001` now maps to `A10:2025`.
- Historical checks recorded two blockers from 2026-08-10 to 2026-08-27, cleared when
  the repository became public:
  GitHub Actions had stopped allocating runners entirely (every job of every workflow ended
  in about three seconds with no runner and no steps executed), and code scanning was
  unavailable, so SARIF uploads and `SAST - CodeQL` could not succeed at all. They are
  historical context for older runs. Current CI needs its own dated verification.
- The 2026-08-27 `OpenSSF Scorecard` review recorded 13 alerts. Those historical counts
  have not been rechecked in this documentation revision. `Maintained` cleared on its own;
  it had been a stale artifact of the period when Scorecard could not evaluate a private
  repository. The rest are accepted
  positions rather than defects, and are recorded here so they are owned rather than merely
  open:
  - `Branch-Protection` previously scored 8/10. It objected that administrators can bypass
    the `master-protection` ruleset, and that only one approving review is required. Both
    are deliberate: this is a single-maintainer project, so a second reviewer does not exist
    and removing the admin bypass would leave nobody able to merge. The residual risk is
    that a mistaken or compromised maintainer action has no second pair of eyes. Revisit if
    the project gains a second maintainer.
  - `Pinned-Dependencies` previously scored 7/10, with eleven instances. It is narrower than
    it looks: every GitHub Action is already pinned to an immutable commit SHA. What is
    unpinned is `pip install` inside `run:` steps. Pinning those by hash means a
    `--require-hashes` requirements file covering the full transitive set, which is a real
    change of dependency strategy -- today the loose ranges are what let CI notice upstream
    breakage early, and there is deliberately no lockfile. It would, as a side effect, give
    `SCA - Trivy` a manifest to scan. Open decision, not an oversight.
  - `Fuzzing` is a true absence. The validator parses untrusted YAML, so a fuzzing harness
    over the loader and schema path is a reasonable future addition rather than a fix.
- The prior workflow review found two required checks with no applicable files.
  `SCA - Trivy` finds no dependency manifest it can parse (the project uses a setuptools
  `pyproject.toml` with no lockfile), and `IaC and Pipeline - Trivy` finds no supported configuration file (there is
  no Dockerfile, Terraform, or Kubernetes manifest here, and Trivy's misconfiguration
  scanner does not cover GitHub Actions workflows). Their historical passing results
  represented zero scanned files.
  Real SCA coverage comes from `pip-audit`; real workflow coverage from KICS and actionlint.
  Both become meaningful the moment a lockfile or a container/IaC file is added.

## OWASP Top 10:2025 mapping decisions

Reviewed on 2026-10-04 against the [official Top 10:2025](https://owasp.org/Top10/2025/)
and the [topic-based convention](CONTRIBUTING.md#framework-mapping-convention). A mapping
connects a rule to a relevant topic; it is not a claim that the rule covers a category fully.

- **`APPSEC-RATELIMIT-001`: map to `A10:2025` (Mishandling of Exceptional Conditions).**
  The category's [How to prevent](https://top10.owasp.org/2025/A10_2025-Mishandling_of_Exceptional_Conditions/#how-to-prevent)
  explicitly says to “add rate limiting, resource quotas, throttling, and other limits”
  to prevent exceptional conditions. It connects those limits to resilience, denial of
  service, brute force, and excessive cloud costs. That directly matches this rule's
  rate limits, quotas, and rejection/backoff when limits are exceeded. Use this one
  category rather than accumulating mappings for each endpoint or CWE.
- **`APPSEC-FILE-001`: keep `owasp_top_10_2025` absent.** The rule combines file-type and
  size validation, storage isolation, and safe path handling. [A01 Broken Access Control](https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/#description)
  centers on permission boundaries, while [A06 Insecure Design](https://top10.owasp.org/2025/A06_2025-Insecure_Design/#description)
  distinguishes missing control design from implementation defects. Those topics overlap
  parts of this rule, but neither is a clean description of its combined file-handling
  scope. A01 listing CWE-22 and A06 listing CWE-434 is not sufficient under the project's
  topic-based convention. Keep the more specific ASVS, API Top 10, and CWE mappings
  instead of forcing a single broad category.

The resulting optional mapping coverage is 18 of 19 rules. An absent mapping is a
recorded scope decision, not a failed validation or a claim that the control is unnecessary.

## Next steps

- Deepen the reference exports — real Semgrep detection patterns or an OPA/Rego mapping —
  kept strictly separate from the validator so the contract stays engine-agnostic.
- Extend mapping coverage: further ASVS chapters and NIST SSDF task-level mapping.
- Stabilize the expanded contract and cut `v1.0` with frozen schema guarantees, once it has
  had real-world use.

## Working on this project

```bash
python -m pip install -e ".[dev]"
python -m pytest --cov=appsec_rules_pack --cov-report=term-missing
python -m appsec_rules_pack validate rules --require-examples --fail-on-warnings
```

See `CONTRIBUTING.md` for the full set of required checks.
