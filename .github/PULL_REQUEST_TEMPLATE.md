## Summary

-

## Validation

- [ ] `python -m ruff check .`
- [ ] `python -m pytest --cov=appsec_rules_pack --cov-report=term-missing`
- [ ] `python -m appsec_rules_pack validate rules --require-examples --fail-on-warnings`
- [ ] `python -m build`
- [ ] New behavior has automated tests; bug fixes have a regression test or an explained verification alternative.

## Security And Data Safety

- [ ] No secrets, credentials, customer data, private findings, or proprietary
      identifiers were added.
- [ ] New or changed rules include evidence, remediation, validation guidance, and
      framework mappings where applicable.
- [ ] Documentation and examples match the implemented behavior.
