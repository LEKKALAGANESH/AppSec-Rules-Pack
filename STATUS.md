# Project Status

Current state of the project, kept consistent with `README.md`, `ROADMAP.md`, and
`TECHNICAL_SPEC.md`. Release-by-release detail lives in [`CHANGELOG.md`](CHANGELOG.md);
this file describes where the project stands and what is known to be true right now.

## Where it stands

**Released:** `appsec-rules-pack` **0.3.1**, published to PyPI via Trusted Publishing
(OIDC, no long-lived credential). Each GitHub Release carries the wheel, the sdist, a
CycloneDX SBOM, a SLSA build-provenance attestation, and the baseline pack itself as
`appsec-baseline.yaml`.

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

**Derived artifacts:** `export index`, `export semgrep`, `export sarif`, and
`report coverage` produce the drift-tested files under [`exports/`](exports/). The Semgrep
output is a clearly-labelled non-runnable scaffold and the SARIF output is a rule catalog
with no results — the validator never executes rules or scans code
([ADR-0001](docs/adr/0001-engine-agnostic-validator.md)).

**Repository posture:** public, with `master` protected by a ruleset requiring a pull
request and fourteen status checks (build/lint/test, both cross-platform jobs, the Python
3.13 job, and the security pipeline's ten unconditional jobs). The repository owner retains
an admin bypass by design, so owner pushes are still possible; every other actor must open a
pull request that passes the checks.

## Verified checks

Last measured 2026-08-27 on Windows 11 with Python 3.12.10, and confirmed on CI the same
day after the repository was made public.

| Check | Result |
| --- | --- |
| `ruff check .` | clean |
| `pytest --cov` | 149 passed, 97.22% coverage (gate 95%) |
| `validate rules --require-examples --fail-on-warnings` | 1 file, 19 rules, 0 errors, 0 warnings |
| `report coverage` | ASVS, API Top 10, CWE, SSDF at 19/19; optional Top 10:2025 at 17/19 |
| `exports/` regeneration | no content drift, byte-identical output on every platform |
| `python -m build` + `twine check` | wheel and sdist PASSED |
| Clean-venv install of the built wheel | `appsec-rules` console script works, schema bundled |
| Exit codes | 0 on a valid pack, non-zero on an invalid one |
| Remote CI | `CI`, `Security CI/CD` and `Policy Gate` all green on `a850223` (runs 33077333996, 33077333970, 33077333954). `Security CI/CD` is green with every scanner job executed, including `SAST - CodeQL`. |

The published release was also validated as an end user: from an empty directory,
`pip install appsec-rules-pack` followed by the documented download of the baseline from the
release assets validates at 19 rules, 0 errors, 0 warnings.

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
- `owasp_top_10_2025` is optional and intentionally absent on two rules where no category
  matches without stretching.
- Two blockers held remote verification from 2026-08-10 to 2026-08-27 and are now resolved.
  Both came from the repository being private, and both cleared when it was made public:
  GitHub Actions had stopped allocating runners entirely (every job of every workflow ended
  in about three seconds with no runner and no steps executed), and code scanning was
  unavailable, so SARIF uploads and `SAST - CodeQL` could not succeed at all. They are
  recorded here because the history matters for reading older runs, not because anything is
  still open.
- `OpenSSF Scorecard` recomputed on 2026-08-27, after the repository became public, and
  reports 13 open alerts. `Maintained` cleared on its own; it had been a stale artifact of
  the period when Scorecard could not evaluate a private repository. The rest are accepted
  positions rather than defects, and are recorded here so they are owned rather than merely
  open:
  - `Branch-Protection`, score 8/10, is accurate. It objects that administrators can bypass
    the `master-protection` ruleset, and that only one approving review is required. Both
    are deliberate: this is a single-maintainer project, so a second reviewer does not exist
    and removing the admin bypass would leave nobody able to merge. The residual risk is
    that a mistaken or compromised maintainer action has no second pair of eyes. Revisit if
    the project gains a second maintainer.
  - `Pinned-Dependencies`, score 7/10, eleven instances, is also accurate but narrower than
    it looks: every GitHub Action is already pinned to an immutable commit SHA. What is
    unpinned is `pip install` inside `run:` steps. Pinning those by hash means a
    `--require-hashes` requirements file covering the full transitive set, which is a real
    change of dependency strategy -- today the loose ranges are what let CI notice upstream
    breakage early, and there is deliberately no lockfile. It would, as a side effect, give
    `SCA - Trivy` a manifest to scan. Open decision, not an oversight.
  - `Fuzzing` is a true absence. The validator parses untrusted YAML, so a fuzzing harness
    over the loader and schema path is a reasonable future addition rather than a fix.
- Two required checks currently measure nothing on this repository. `SCA - Trivy` finds no
  dependency manifest it can parse (the project uses a setuptools `pyproject.toml` with no
  lockfile), and `IaC and Pipeline - Trivy` finds no supported configuration file (there is
  no Dockerfile, Terraform, or Kubernetes manifest here, and Trivy's misconfiguration
  scanner does not cover GitHub Actions workflows). Both pass, and both scan zero files.
  Real SCA coverage comes from `pip-audit`; real workflow coverage from KICS and actionlint.
  Both become meaningful the moment a lockfile or a container/IaC file is added.

## Next steps

- Deepen the reference exports — real Semgrep detection patterns or an OPA/Rego mapping —
  kept strictly separate from the validator so the contract stays engine-agnostic.
- Extend mapping coverage: further ASVS chapters and NIST SSDF task-level mapping.
- Decide `owasp_top_10_2025` for `APPSEC-FILE-001` and `APPSEC-RATELIMIT-001` against the
  written mapping convention.
- Stabilize the expanded contract and cut `v1.0` with frozen schema guarantees, once it has
  had real-world use.

## Working on this project

```bash
python -m pip install -e ".[dev]"
python -m pytest --cov=appsec_rules_pack --cov-report=term-missing
python -m appsec_rules_pack validate rules --require-examples --fail-on-warnings
```

See `CONTRIBUTING.md` for the full set of required checks.
