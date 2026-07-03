# Security Policy

Status: Draft ATOS v1.1 governance document

## Scope

Repository access, local tools, AI agents, secrets, external services and data files used by Austin Trading Engine work.

## Rules

- No secrets, tokens or credentials in repository files.
- No broker credentials are permitted in this project scope.
- No paper-trading API credentials are permitted in this project scope.
- Access to repository and tools is limited to authorised Austin Trading Team operators.
- Security-sensitive changes require review by the Security Owner.
- Suspected credential exposure requires immediate revocation and incident note.

## AI Tooling

AI agents may inspect and edit repository files only within the approved project scope. They must not connect the project to execution, broker or paper-trading systems.
