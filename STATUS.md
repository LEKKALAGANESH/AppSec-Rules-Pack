# AppSec Rules Pack Status

## Current Status

- Project 12 contains a Python 3.12 rules-pack validator, JSON Schema contract,
  a baseline AppSec rules pack of 19 rules across all schema categories, a Typer
  CLI, docs, unit fixtures, a coverage gate, and a hardened CI workflow.
- Validator coverage includes schema validation, duplicate rule IDs within a file
  and across a validated directory, exception-window warnings, exception-policy
  consistency checks, framework mapping format validation, sensitive-value
  detection, single-file and directory CLI validation, `--fail-on-warnings`,
  `--require-examples`, `--version`, and `--format json` output.
- Every baseline rule ships a compliant and a violating code example; the schema
  enforces the example shape and `--require-examples` flags enabled rules that omit it.
- Derivation-only `export index`, `export semgrep`, and `export sarif` subcommands plus a
  `report coverage` subcommand produce drift-tested `exports/` artifacts: a JSON rule index,
  a clearly-labelled NON-runnable Semgrep scaffold, and a SARIF rule catalog with no results.
  The validator stays engine-agnostic and never executes rules or scans code (ADR-0001).
- The project is now tracked in its own standalone Git repository with a hardened
  CI/CD surface (build/lint/test CI, a security pipeline, and OpenSSF Scorecard),
  Dependabot, CODEOWNERS, and community-health files.
- The GitHub repository `lucashgrifoni/AppSec-Rules-Pack` is **public** as of 2026-06-02,
  with About metadata populated (description, website, topics). `master` is
  branch-protected as of 2026-06-03 via the `master-protection` ruleset (MEL-001):
  require PR (1 review), require the `Lint, test, and validate rules` status check,
  block force-push and deletion, with repository-admin bypass for the owner.
- Published to PyPI as `appsec-rules-pack` **0.2.0** on 2026-06-03 via the `publish-pypi.yml`
  workflow (Trusted Publishing / OIDC, no long-lived token). The v0.2.0 GitHub Release carries
  the wheel, sdist, and a CycloneDX SBOM, with a SLSA build-provenance attestation. Installable
  with `pip install appsec-rules-pack`.
- A landing page is published on GitHub Pages at
  https://lucashgrifoni.github.io/AppSec-Rules-Pack/ (the repository "website" points to it).
  It is deployed from an orphan `gh-pages` branch (index.html + .nojekyll only); the local
  `gitpage/` source stays git-ignored on `master`, so the package repo remains clean.

## Last Increment

- 2026-08-05 (v0.3.0 **published**): the signed `v0.3.0` tag drove `publish-pypi.yml` end to
  end — build, CycloneDX SBOM, SLSA build-provenance attestation, PyPI publish via OIDC
  Trusted Publishing, and a GitHub Release. PyPI serves `appsec-rules-pack` 0.3.0 (wheel +
  sdist); the Release carries the wheel, sdist, SBOM, and — new in this version — the
  baseline pack itself as `appsec-baseline.yaml` (45,090 bytes). The remote reports the tag
  as `verified: true`. Validated as an end user afterwards, not merely by a green workflow:
  from an empty directory, `pip install appsec-rules-pack` gave 0.3.0, the README's exact
  `curl` URL fetched the baseline from the Release, and the installed CLI validated it at
  19 rules / 0 errors / 0 warnings, then produced a coverage report and a SARIF catalog.
  The `Python 3.13 compatibility` check was added to the ruleset once it passed remotely,
  bringing required status checks to 14.
- 2026-08-05 (v0.3.0 prepared): bumped the package and pack version to 0.3.0. The schema
  `$id` deliberately **stays** at the v0.2.0 tag: its own `$comment` policy moves it only
  when the schema changes in a way that affects consumers, and `git diff v0.2.0..HEAD --
  src/appsec_rules_pack/schemas/` is empty. Attached the baseline pack to the GitHub
  Release, mapped `APPSEC-SSRF-001` to `A01:2025` (2025 mapping coverage 16/19 -> 17/19),
  raised the coverage gate 90% -> 95%, and added a Python 3.13 CI job. Also widened the
  `master-protection` ruleset from 1 required status check to 13: the two cross-platform
  jobs plus the ten unconditional Security CI/CD jobs. `OpenSSF Scorecard` and
  `policy-gate` are deliberately excluded — neither runs on every pull request (Scorecard
  has no `pull_request` trigger; policy-gate is path-filtered), so requiring them would
  block every PR on a check that never reports.

- 2026-08-05 (first-use experience, found by using the CLI as a new user): installed the
  published package into a clean venv and followed only the public docs. Three defects that
  no automated test caught. (1) The first documented command failed: `validate
  rules/appsec-baseline.yaml` does not exist for someone who installed from PyPI, because
  the distribution ships no rules pack — README now says so and separates repo-relative
  examples from a PyPI install. (2) There was no copyable example of a valid pack; writing
  one from the README's prose produced eight schema errors, since the prose describes
  concepts (`evidence`, `match`, `remediation`) and not their shapes. README now carries a
  complete minimal pack, validated by `tests/test_readme_example.py` so it cannot drift.
  (3) A rule with an empty `match` printed the same error three times and counted three
  errors; identical schema errors at the same path are now reported once.
  Exploratory testing then found that an unwritable `--output` (for example an existing
  directory) escaped as a Python traceback; all four writing commands now emit a clean
  message and exit 1. Suite is 130 tests at 97.46% coverage.
- 2026-08-05 (repository visibility, root cause of a red security pipeline): the repository
  had reverted to **private** — a recurrence of HF-09. Code scanning requires a public
  repository or GHAS, so every SARIF upload failed (Semgrep, CodeQL, Trivy x3, KICS) and
  OpenSSF Scorecard could not read commits. Workflow permissions were never the problem
  (`security-events: write` was correctly declared throughout). Anonymous visitors got a 404
  while the landing page and the PyPI project links kept pointing at the repository. Made
  public again with owner authorization; **Security CI/CD and Scorecard are now green**.
  Neither workflow is a required check, which is why it went unnoticed.

- 2026-08-05 (semantic-check degradation): covered how the semantic checks behave when the
  schema has already rejected the payload — reachable on every invalid pack, since both run
  over the same payload. Each check skips rules it cannot read (non-dict entries, non-string
  IDs, non-mapping `exceptions`/`mappings`) rather than raising, which is what lets one
  `validate` run report all schema errors at once instead of aborting on the first malformed
  rule. A new semantic check written without a type guard would previously have crashed the
  whole run on any invalid pack with nothing to catch it: every existing fixture keeps
  `rules` a list of dicts. Suite is now 121 tests at 97.42% coverage; no behaviour changed.
- 2026-08-05 (untested behaviour pinned down): added tests for two behaviours that had no
  coverage at all. Directory validation keeps going when one YAML file is unparseable —
  it reports the parse error, still validates the rest, and still counts their rules; a
  regression there would let one broken file silently truncate a CI report. The
  derivation-only exports now have a degradation contract under malformed or partial packs
  (they run without schema validation, so this is reachable): unknown severity falls back
  to `warning` with no invented `security-severity`, a missing pack version falls back to
  `0.0.0`, and non-list mappings are skipped rather than raising. `reporter.py`,
  `sarif_export.py`, and `semgrep_scaffold.py` are now at 100% coverage; the suite is 114
  tests at 96.20% overall. No behaviour changed — these tests describe what already
  happens, verified by running it first.
- 2026-08-05 (reproducible exports + untested write paths): made every `--output` write
  emit LF on all platforms (`Path.write_text` was translating to CRLF on Windows), so the
  documented regeneration commands produce byte-identical artifacts everywhere. Verified
  with `git hash-object --no-filters` against the committed blobs: identical. Added tests
  for the CLI `--output` path of all three exports — `export semgrep --output` and
  `export sarif --output` had none, because the drift tests compare the committed file to
  the in-memory builder and never touch the writer. `report coverage` now warns on stderr
  when a pack yields zero rules, instead of printing a healthy-looking `0/0`; exit code
  intentionally unchanged. Suite is now 106 tests at 94.36% coverage.
- 2026-08-05 (test portability + cross-platform CI): fixed a defect that made the suite red
  on Windows while green on CI. Two tests shelled out with `subprocess.run(text=True)` and no
  explicit encoding, so the parent decoded with the platform locale (cp1252) while the child
  emitted UTF-8; the decode error was swallowed inside `subprocess`, leaving `stdout` as
  `None` and surfacing as a misleading `TypeError`. Both call sites now go through a shared
  `tests/helpers.py` that pins UTF-8 on both ends, with regression tests in
  `tests/test_helpers.py`. Added a `cross-platform` CI job (Ubuntu + Windows) so this class of
  defect fails remotely; the required status check `Lint, test, and validate rules` was
  deliberately left untouched, because renaming it would silently disable branch protection.
  Suite is now 98 tests at 92.73% coverage. **Not yet pushed** — awaiting owner approval.
- 2026-06-03 (v0.2.0 published): cut and published `appsec-rules-pack` 0.2.0 to PyPI via OIDC
  Trusted Publishing. Bumped the package and rules-pack content version to 0.2.0, moved the
  schema `$id` to the v0.2.0 tag (per the schema's versioning policy), regenerated the
  `exports/` JSON index and SARIF catalog, and finalized the CHANGELOG. The signed `v0.2.0`
  tag drove `publish-pypi.yml` end to end: build, CycloneDX SBOM, SLSA attestation, PyPI
  publish, and a GitHub Release (wheel + sdist + SBOM). Release run green.
- 2026-06-03 (release path validated): enabled `master` branch protection (MEL-001) and
  re-signed/force-pushed the `v0.1.0` tag (now verified on the remote, Release intact).
  Renamed the publish workflow `release.yml` -> `publish-pypi.yml` to match the cross-project
  convention and the PyPI Trusted Publisher's workflow-name field. Fixed the CycloneDX SBOM
  step (`cyclonedx-bom` 7.3.0 has no `--outfile`; use `--output-file`, pin the tool to 7.3.0)
  and validated build + SBOM + SLSA attestation green via a `workflow_dispatch` dry-run (the
  publish and Release-asset steps are tag-gated and correctly skip until a `v*` tag is pushed).
  The PyPI pending publisher is configured.
- 2026-06-02 (CI fix + history rewrite): switched the actionlint job to `egress-policy:
  audit` (digest-pinned image; fixes a flaky Docker-pull failure), and rewrote Git history
  to remove an accidentally-committed landing-page draft and strip an AI co-author trailer
  from the initial commit (root subject also corrected; the `v0.1.0` tag was re-pointed).
  All post-init commit SHAs changed, so SHAs in older notes below no longer resolve.
- 2026-06-02 (tooling + workflows): added derivation-only `report coverage`,
  `export semgrep` (non-runnable scaffold), and `export sarif` (rule catalog, no results)
  commands with drift-tested `exports/` artifacts; added reference `policy-gate.yml`
  (consumes validator JSON, ADR-0004) and `publish-pypi.yml` (SBOM + SLSA attestation + PyPI
  OIDC; PyPI publisher config is an owner handoff). Suite is now 96 tests at ~93% coverage.
- 2026-06-02 (rules v0.2 expansion): grew the baseline pack from 12 to 19 rules
  (`APPSEC-CSRF-001`, `APPSEC-ENUM-001`, `APPSEC-MSGAUTH-001`, `APPSEC-DATAEXPO-001`,
  `APPSEC-MASSASSIGN-001`, `APPSEC-REDIRECT-001`, `APPSEC-RATELIMIT-001`); added the
  optional `owasp_top_10_2025` mapping; added rule-lifecycle support (`deprecated` status +
  `deprecation` block); and extended the `category` vocabulary by five values. Suite is now
  83 tests at ~94% coverage; baseline 19 rules, 0 errors, 0 warnings.
- 2026-06-02 (pushed to `origin/master`): migrated all 12 baseline rules'
  `owasp_asvs` mappings to OWASP ASVS 5.0.0, re-derived by topic against the 5.0.0 chapter
  sources (OWASP publishes no official v4->v5 crosswalk). Regenerated
  `exports/appsec-baseline.index.json` and updated docs. Suite green: 78 tests at ~94%
  coverage; baseline 12 rules, 0 errors, 0 warnings. The repository was then made **public**
  and its About metadata (description, website, topics) populated.
- 2026-06-01 (pushed to `origin/master`): added two baseline rules,
  `APPSEC-SESSION-001` (session cookie/lifecycle hardening) and `APPSEC-XSS-001`
  (output encoding / XSS), bringing the pack to 12 rules; added an `export index` CLI
  subcommand plus a checked-in `exports/appsec-baseline.index.json` with a drift test;
  and replaced the schema `$id` placeholder with a canonical, tag-versioned URL
  (documented via a schema `$comment`). The suite is now 78 tests at ~94% coverage.
  The two new rules were prioritised from a read-only coverage validation of the pack
  against a vulnerable-app test suite (gaps: session, rate limiting, CSRF, enumeration,
  XSS, webhook authenticity, data exposure).
- Prior (v0.1.0, 2026-05-25): released v0.1.0 (tag + GitHub Release) with wheel/sdist
  assets and green remote CI/CD; added the optional `examples` field plus the
  `--require-examples` flag and `tests/test_examples.py`.

## Checks

- 2026-08-05 (local, Windows 11 / Python 3.12.10): full end-to-end battery green —
  `ruff` clean; 98 tests at 92.73% coverage (gate 90%); `validate rules --require-examples
  --fail-on-warnings` = 1 file, 19 rules, 0 errors, 0 warnings; JSON report keys stable;
  `exports/` regenerated with no content drift; `report coverage` = 19 rules with the three
  required framework mappings at 100% and the optional `owasp_top_10_2025` at 84%;
  `python -m build` + `twine check` PASSED for wheel and sdist; the built wheel installed
  into a clean venv exposes a working `appsec-rules` console script with the schema bundled;
  exit codes 0 (valid pack) and 1 (invalid pack) confirmed. Prior "96 tests green" entries
  were measured on CI (Ubuntu); the same suite was red on Windows until this increment.
- 2026-06-03 (v0.2.0 release): local suite green — 96 tests at 92.73% coverage (gate 90%),
  `ruff` clean, `validate rules --require-examples --fail-on-warnings` = 1 file, 19 rules,
  0 errors, 0 warnings, CLI `--version` = 0.2.0, `exports/` regenerated with no drift. The
  remote `publish-pypi.yml` run on tag `v0.2.0` (run 26891035504) succeeded across build,
  SBOM, SLSA attestation, PyPI publish, and GitHub Release. PyPI JSON API confirms
  `appsec-rules-pack` 0.2.0 with wheel + sdist.
- 2026-06-02 (final, post-history-rewrite): local suite green — 96 tests at ~93% coverage
  (gate 90%), `ruff` clean, `validate rules --require-examples --fail-on-warnings` = 19 rules,
  0 errors, 0 warnings, `exports/` artifacts with no drift. Remote CI/CD verified **green** on
  the rewritten `master` (`CI`, `Security CI/CD`, `OpenSSF Scorecard`). The actionlint job now
  uses `egress-policy: audit` (Docker-pull flake fixed); a one-time Gitleaks force-push
  base-range artifact (no real finding) cleared on the next normal push.
- `python -m pytest --cov` passed on 2026-06-01 with 78 tests at ~94% coverage
  (gate 90%); `ruff check .` clean; `validate rules --require-examples
  --fail-on-warnings` reported 1 file, 12 rules, 0 errors, 0 warnings; `export index`
  regenerates `exports/appsec-baseline.index.json` with no drift.
- 2026-06-02 (rules v0.2 expansion): `pytest --cov` 83 passed at ~94% (gate 90%); `ruff check .`
  clean; `validate ... --require-examples --fail-on-warnings` = 1 file, 19 rules, 0 errors,
  0 warnings; `export index` regenerated with no drift.
- 2026-06-02 (ASVS 5.0 remap): `pytest --cov` 78 passed at 93.71% (gate 90%); `ruff check .`
  clean; `validate ... --require-examples --fail-on-warnings` = 1 file, 12 rules, 0 errors,
  0 warnings; `export index` regenerated with no drift.
- 2026-06-02: changes pushed to `origin/master`; remote CI/CD verified **green**
  (`CI`, `Security CI/CD`, `OpenSSF Scorecard`, and `Dependency Graph` all succeeded).
- `python -m pytest` passed on 2026-05-25 with 69 tests.
- `python -m pytest --cov=appsec_rules_pack` reported 93% coverage on 2026-05-25
  (gate is 90%).
- `python -m ruff check .` passed on 2026-05-25.
- `$env:PYTHONPATH = "src"; python -m appsec_rules_pack validate rules --require-examples --fail-on-warnings`
  passed on 2026-05-25 with 1 file, 10 rules, 0 errors, and 0 warnings.
- `python -m build` produced a wheel and sdist with the schema bundled.
- On 2026-05-25 the GitHub remote CI/CD ran green on `master` (commit `fff996d`):
  `CI`, `Security CI/CD`, and `OpenSSF Scorecard` all succeeded. A `.gitleaks.toml`
  was added to allowlist the intentional fake-secret fixtures in
  `tests/test_validator_paths.py` (Gitleaks false positive), keeping secret scanning
  active everywhere else.

## Risks And Limits

- Cross-file duplicate ID detection applies only when validating a directory with
  two or more YAML rule packs; single-file validation remains file-local.
- The rule model is generic and review-oriented. The `exports/` Semgrep output is a
  NON-runnable scaffold (placeholder patterns) and the SARIF export is a rule catalog with
  no results; the pack does not execute rules or scan code in any engine (ADR-0001).
- Negative fixtures intentionally validate message stability, so future message
  changes must update tests and CLI expectations together.
- Mapping format checks are warnings, not errors, so unusual but valid identifiers
  are not blocked; review warnings during contribution.
- The CI/CD workflows run on the GitHub remote and are green on `master`. The repository
  is public and `master` is branch-protected as of 2026-06-03 (MEL-001, `master-protection`
  ruleset). The repository owner retains an admin bypass, so owner direct pushes are still
  possible by design; non-bypass actors must open a PR with a passing CI check.

## Next Steps

- ~~Enable branch protection and required status checks on `master`~~ — **done 2026-06-03**
  (MEL-001; `master-protection` ruleset, admin bypass for the owner).
- ~~Re-sign the `v0.1.0` tag~~ — **done 2026-06-03**; the tag was re-created at `489cea4`
  with a fresh SSH signature and force-pushed. The remote reports the tag as verified and
  the existing GitHub Release (wheel + sdist) is intact.
- ~~Configure the PyPI Trusted Publisher and cut a tagged release~~ — **done 2026-06-03**;
  `appsec-rules-pack` 0.2.0 is live on PyPI via OIDC Trusted Publishing, and `publish-pypi.yml`
  now creates the GitHub Release idempotently from the tag.
- **Owner action (external, cannot be done from the CLI):** provider credential hygiene is
  tracked outside this repository. Publishing needs no long-lived credential: releases go
  out through PyPI Trusted Publishing (OIDC), so any legacy API token can be deleted rather
  than rotated.
- **Owner action (push approval):** the 2026-08-05 increment is committed locally only. The
  new `cross-platform` CI job has never executed remotely, so its green state is unverified;
  it is intentionally *not* a required status check. After pushing and seeing it pass, decide
  whether to add `Cross-platform tests (windows-latest)` to the `master-protection` ruleset.
- Defer the v1.0 cut (MEL-013) until the expanded contract (new categories, rule lifecycle,
  optional 2025 mapping, and exports) has had real-world use.

## Resume Command

```powershell
cd "C:\Users\Lucas Grifoni\Downloads\My Projects - AppSec & DevSecOps\Projects List - Andamento\12.Projeto - AppSec Rules Pack"
python -m pytest --cov=appsec_rules_pack --cov-report=term-missing
```
