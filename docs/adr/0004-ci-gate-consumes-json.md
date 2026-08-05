# ADR-0004 — The CI policy gate consumes the validator's JSON; enforcement is not built in

- **Status:** Accepted
- **Date:** 2026-05-29 proposed · 2026-06-03 accepted and implemented in `policy-gate.yml`
- **Related:** [ADR-0001](0001-engine-agnostic-validator.md)

## Context

The roadmap calls for integration points where a CI policy gate consumes the JSON output to
block, warn, or baseline. The validator already emits `--format json` with a `summary`
(`files`, `rules`, `errors`, `warnings`, `ok`) and per-file issues.

There are two ways to offer gating: embed enforcement policy in the validator, or keep the
validator as a producer of **evidence** and leave the **gate decision** to an external
consumer.

The non-goal "no production enforcement built into the validator" and
[ADR-0001](0001-engine-agnostic-validator.md) both point the same way.

## Decision

The validator keeps **producing evidence** — text and `--format json` — and embeds **no
enforcement policy**. Block/warn/baseline behaviour ships as a **reference workflow** that
consumes the validator's JSON and decides the gate.

The policy — which severity blocks, what baseline is accepted, how exceptions work — lives in
the **consumer**, not in the validator.

## Alternatives considered

- **(A) Enforcement built into the validator** (policy flags, an internal baseline). Rejected:
  couples policy to the contract, contradicts a non-goal and ADR-0001, and forces one
  organisation's policy on everyone.
- **(B) No gate example at all.** Rejected: leaves users without a clear adoption path.
- **(C) A reference gate consuming the JSON — chosen.** Keeps the core clean and still gives
  a real, copyable path into CI.

## Consequences

- **Positive:** the core stays stable and engine-agnostic; each organisation defines its own
  policy; `--format json` gains a reference consumer; low regression risk in the validator.
- **Negative:** users must adopt and adapt the example, and baseline/exception semantics sit
  on the consumer's side, so they need documenting. The JSON output must stay **stable** —
  treat it as a contract.
- **Validation:** the example demonstrates blocking on an error and a configurable warning
  level, and the JSON shape is covered by a stability test.
