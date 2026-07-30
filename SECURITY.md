# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in the Austin Trading Engine (ATE),
please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email: paul@austintradingteam.com with a description of the issue,
steps to reproduce, and any relevant proof-of-concept material.

## Response Timeline

- **Acknowledgement:** within 48 hours
- **Initial assessment:** within 7 days
- **Fix or mitigation:** severity-dependent, communicated after assessment

## Scope

ATE is a diagnostic-only market analysis framework. It does not connect to
brokers, execute trades, or handle financial credentials. Security issues
relevant to ATE include:

- Repainting or lookahead bugs that could produce misleading diagnostic output
- Code injection via Pine Script or Python tooling
- Repository integrity issues (unauthorised modifications to release files)
- Sensitive data accidentally committed to the repository

## Out of Scope

- Broker connectivity, order execution, or trade management (not implemented)
- Live trading infrastructure (not in scope per Project Charter)
- Third-party services not part of this repository