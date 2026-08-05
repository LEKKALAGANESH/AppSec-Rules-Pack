# ADR-0003 — Trusted Publishing, build attestations, and an SBOM on every release

- **Status:** Accepted
- **Date:** 2026-05-29 proposed · 2026-06-03 accepted and implemented in `publish-pypi.yml`
- **Related:** [ADR-0001](0001-engine-agnostic-validator.md)

## Context

The first release produced a wheel and an sdist with **no verifiable provenance and no SBOM**.
For an AppSec/DevSecOps project, that is a credibility problem: it should practise what it
recommends on its own supply chain.

Concrete, current mechanisms exist:

- **PyPI Trusted Publishing** (OIDC, tokenless) with **PEP 740 attestations**, emitted by
  default by `pypa/gh-action-pypi-publish`.
- **GitHub Artifact Attestations** (`actions/attest-build-provenance`), reaching **SLSA v1.0
  Build L2** directly, with L3 available through a reusable workflow. Attestations are
  available on public repositories.
- **CycloneDX** for the SBOM, and **OpenVEX** when there is actually a CVE to declare.

## Decision

Adopt the supply-chain posture incrementally:

1. **Now:** publish to PyPI through **Trusted Publishing (OIDC)** with PEP 740 attestations;
   attach **GitHub build-provenance attestations** for the wheel and sdist (**SLSA Build L2**);
   attach a **CycloneDX SBOM** to every GitHub Release.
2. **At v1.0:** move to **SLSA Build L3** through a reusable provenance workflow; keep the
   SBOM per release; emit **VEX** only when a relevant CVE exists.
3. **No long-lived secrets:** use OIDC and ephemeral signing throughout. No static publish
   token.

## Alternatives considered

- **(A) Sign with a long-lived private key.** Rejected: key management is a liability, and
  ephemeral OIDC-backed signing is strictly better here.
- **(B) Do not publish, or publish without provenance.** Rejected: contradicts the roadmap
  and the positioning, and reduces trust.
- **(C) Trusted Publishing + attestations + SBOM — chosen.** Current practice, no long-lived
  secrets, independently verifiable.

## Consequences

- **Positive:** the release is verifiable with `gh attestation verify`, installable from PyPI,
  and carries an SBOM. What the project says and what it does line up.
- **Negative:** it requires configuring the Trusted Publisher on PyPI and the right workflow
  permissions (`id-token: write`, `attestations: write`). A misconfiguration is easy, so the
  flow is exercised with a dry run before a real tag.
- **Validation:** install from PyPI into a clean virtual environment, verify the attestations,
  and check the SBOM.
