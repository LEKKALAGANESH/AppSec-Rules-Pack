# ADR-0001 — The validator stays engine-agnostic; interoperability lives in `exports/`

- **Status:** Accepted
- **Date:** 2026-05-29 proposed · 2026-06-03 accepted
- **Related:** [ADR-0004](0004-ci-gate-consumes-json.md), the non-goals in `TECHNICAL_SPEC.md`

## Context

This project is, by design, a **rule contract plus a deterministic validator**, aimed at
review and quality gates. `TECHNICAL_SPEC.md` and `ROADMAP.md` both declare it a non-goal to
embed a scanner execution engine (Semgrep, CodeQL, OPA/Rego, SARIF emission) in the
validator.

The planned adoption and interoperability work — a rule index, a Semgrep mapping, a SARIF
export — could, if positioned badly, turn the project into "yet another scanner" and
dissolve what makes it useful.

SARIF describes **engine results**, not rules. That reinforces the boundary: emitting SARIF
findings belongs to an engine, not to a validator that never executes anything.

## Decision

The validator stays **engine-agnostic and deterministic**. Every interoperability capability
lives in a **separate, optional, derived `exports/` layer** that:

1. **derives** artifacts from the rules pack, and never executes rules;
2. is documented as reference material, not as a bundled engine;
3. adds no dependency on any engine runtime to the validator;
4. is covered by **drift tests**, so an export always reflects the pack it came from.

## Alternatives considered

- **(A) Embed an engine in the validator** — execute Semgrep/CodeQL and emit SARIF results.
  Rejected: violates a stated non-goal, enlarges the dependency and attack surface, and
  confuses both the positioning and the contract.
- **(B) Offer no interoperability at all.** Rejected: limits adoption for no reason.
  Derivation is safe and genuinely useful.
- **(C) A separate `exports/` layer — chosen.** Keeps the identity intact while still
  enabling real downstream use.

## Consequences

- **Positive:** the identity is preserved, the validator's surface stays small, the
  engine-agnostic contract holds, and adoption is possible without coupling.
- **Negative:** anyone expecting a ready-made scanner needs an external engine. Holding the
  line requires review discipline, because scope creep into the validator is the natural
  drift.
- **Follow-up:** every pull request touching the exports must be checked against this
  boundary explicitly.

## How it shows up in the code

The Semgrep export is a clearly-labelled **non-runnable scaffold** with placeholder patterns,
and the SARIF export is a **rule catalog with an empty `results` array**. Both are derived
and drift-tested; neither is a working detection.
