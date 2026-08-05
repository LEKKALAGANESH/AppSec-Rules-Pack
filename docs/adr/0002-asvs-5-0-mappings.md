# ADR-0002 — Migrate framework mappings to OWASP ASVS 5.0

- **Status:** Accepted
- **Date:** 2026-05-29 proposed · 2026-06-02 accepted and executed · 2026-06-03 re-verified
- **Related:** [ADR-0001](0001-engine-agnostic-validator.md)

## Context

The baseline rules mapped OWASP ASVS in **v4 notation** (for example `V4.1`). The current
stable standard is **ASVS 5.0.0** (May 2025), which reorganised the standard into **17
chapters** (V1–V17) with a full renumbering.

For an AppSec product, shipping outdated standard identifiers is a factual-accuracy problem
before it is anything else.

**Correction recorded 2026-06-03:** an earlier version of this ADR claimed OWASP publishes no
v4-to-v5 crosswalk. That was wrong. OWASP does publish an official mapping
(`5.0/mappings/mapping_v5.0.0_to_v4.0.3.yml`), and the assigned identifiers were verified
against it.

## Decision

1. **Remap** `mappings.owasp_asvs` on every rule to **ASVS 5.0** identifiers, assigned **by
   topic** against the 5.0.0 chapter sources and then **verified** against both the 5.0.0
   section structure and the official v5.0.0-to-v4.0.3 mapping.
2. **Record the standard version** in the docs and as a YAML comment rather than as a new
   schema field, so the rule contract is not disturbed.
3. **No regex change:** 5.0 identifiers (`Vn.m` / `Vn.m.p`) already match the existing
   pattern `^V\d+(\.\d+){1,2}$`.
4. Keep mapping-format checks as **warnings**, not errors, so an unusual but valid identifier
   is never blocked.

## Alternatives considered

- **(A) Stay on ASVS v4.** Rejected: outdated information costs credibility.
- **(B) Support v4 and v5 simultaneously.** Rejected for now: doubles the validation surface
  and the content for a superseded version. Reconsider only if a real consumer is pinned
  to v4.
- **(C) Migrate to v5 with the version declared — chosen.** Fixes accuracy and keeps
  traceability.

## Consequences

- **Positive:** mappings are current and verifiable, which is the precondition for the
  mapping-coverage report and for the optional Top 10:2025 field.
- **Negative:** the remap was assigned by topic rather than mechanically item-by-item from
  the official map. Mitigated by verifying every identifier against the 5.0.0 section
  structure and the official mapping. Final confidence: high.
- **Verification (2026-06-03):** all 19 `owasp_asvs` identifiers were checked and found
  correct with no ID changes. Examples: `V1.2` *Injection Prevention* (5.0 folds XSS in here,
  with no separate XSS section); `V1.3` *Sanitization* §1.3.6 for SSRF; `V2.4`
  *Anti-automation* for rate limiting; `V3.3` *Cookie Setup* and `V3.5` *Browser Origin
  Separation* for session and CSRF; `V8` *Authorization*.

## Note on what a mapping means here

Mappings are **evidence aids for review**. They are not a claim of conformance to ASVS. See
`CONTRIBUTING.md` for the assignment convention: categories are chosen **by topic**, not by
CWE membership.
