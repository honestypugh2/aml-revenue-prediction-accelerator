# Security Policy

## Scope and intent

This accelerator is a **development and educational** artifact that ships with
**synthetic data only**. It is not a production-ready system and must be
reviewed by qualified security, privacy, compliance, and operational
stakeholders before any production use.

## Reporting a vulnerability

Please report suspected security issues privately to the repository maintainers
via the repository's private security advisory feature. Do **not** open a public
issue for undisclosed vulnerabilities. Include:

- a description of the issue and its impact,
- steps to reproduce,
- affected files or components,
- any suggested remediation.

We aim to acknowledge reports promptly and provide a remediation timeline.

## Secrets and data handling

- **No secrets are committed.** All subscription IDs, tenant IDs, client IDs,
  secrets, tokens, SAS tokens, storage keys, connection strings, and workspace,
  Fabric, and Lakehouse identifiers are represented by placeholders and supplied
  only via environment variables at runtime.
- `.env` is git-ignored; only `.env.example` (placeholders) is committed.
- Authentication uses `DefaultAzureCredential` (Azure CLI, managed identity, or
  environment credentials). The code never reads secrets from source.
- A redaction/neutrality scanner (`revenue_prediction.security`) helps prevent
  accidental logging of secrets or personally identifiable contact information.

## Secure deployment guidance

For production workloads, follow the official Microsoft guidance referenced in
[`docs/security/`](docs/security/), including network isolation (managed VNet or
BYO VNet), private endpoints, private DNS, least-privilege RBAC, and monitoring.

## OWASP alignment

Application code is written to avoid the OWASP Top 10 categories relevant to
this codebase (e.g. injection, sensitive-data exposure, security
misconfiguration). Infrastructure templates default to private, firewalled
configurations in the secure profiles.
