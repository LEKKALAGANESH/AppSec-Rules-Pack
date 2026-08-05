# Security Policy

## Supported Versions

`appsec-rules-pack` is published on PyPI. Security fixes target the current `0.3.x`
release line and `master`.

| Version | Supported |
| ------- | --------- |
| 0.3.x   | ✅        |
| 0.2.x   | ❌        |
| 0.1.x   | ❌        |

Earlier builds and pre-release commits are not maintained; upgrade to the latest
`0.3.x` release.

## Reporting a Vulnerability

Report suspected vulnerabilities privately through GitHub Security Advisories
(the repository "Security" tab, "Report a vulnerability"). Include the affected
version or commit, reproduction steps, and expected impact.

Do not include proprietary source code, private findings, credentials, customer
data, or exploit payloads from systems you do not own.

## Scope

In scope:

- Rule schema validation.
- Rule pack integrity and unsafe rule metadata.
- CLI behavior for local validation.

Out of scope:

- Claims that downstream code is secure because it maps to this rules pack.
