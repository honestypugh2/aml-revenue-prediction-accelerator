# Security & networking

> All sample data is synthetic. This document describes how to harden a real
> deployment. Follow the authoritative Microsoft guidance linked below.

## Principles

- **No secrets in source.** Subscription/tenant/client IDs, secrets, tokens, SAS
  tokens, storage keys, connection strings, and workspace/Fabric/Lakehouse IDs
  are placeholders supplied via environment variables at runtime.
- **Managed identity first.** Authentication uses `DefaultAzureCredential`
  (managed identity on a jump box, Azure CLI, or environment credentials). The
  code never reads secrets from source.
- **Least privilege.** Grant the minimum RBAC roles required; scope them to the
  resource group / resource.
- **Network isolation for production.** Use a managed VNet or BYO VNet, private
  endpoints, and private DNS. Disable public network access on Storage, Key
  Vault, and the workspace where possible.

## Infrastructure profiles

| Profile | Directory | Isolation |
| --- | --- | --- |
| Quickstart | `infra/terraform-quickstart/`, `infra/bicep/quickstart/` | Public workspace for quick starts / learning |
| Secure (Managed VNet) | `infra/terraform/`, `infra/bicep/secure/` | Managed VNet, private endpoints, firewalled Storage/KV/ACR, Bastion + jump box |
| BYO VNet foundation | `infra/azure-ml-vnet/` | Standalone VNet, delegated subnet, NSG, route table, managed identity |

## Recommended RBAC (production)

- Subscription: `Contributor` or `Owner` (resource management),
  `User Access Administrator` (role assignments) — for the deploying principal.
- Resource group: `Contributor`, `AzureML Data Scientist`,
  `AzureML Compute Operator`.
- Storage (workspace managed identity): `Storage Blob Data Contributor` and
  `Storage File Data Privileged Contributor` on the default storage account —
  required for job submission.

## Managed network / private endpoints

Follow the official guidance for required outbound rules and private link:

- Managed network guidance (required rules):
  https://learn.microsoft.com/azure/machine-learning/how-to-managed-network
- Private endpoint / private link:
  https://learn.microsoft.com/azure/machine-learning/how-to-configure-private-link
- Secure workspace tutorial:
  https://learn.microsoft.com/azure/machine-learning/tutorial-create-secure-workspace

## Application-level security

- Input data is validated at the boundary via Pandera contracts before use.
- `revenue_prediction.security` provides redaction and a neutrality/secret
  scanner used by pre-commit to prevent accidental leakage of secrets or
  contact information.
- The code avoids OWASP Top 10 issues relevant to this codebase (no string-built
  queries, no untrusted deserialization of remote input, no secrets in logs).

## Cost and cleanup

See [`docs/operations/cost-and-cleanup.md`](../operations/cost-and-cleanup.md)
to avoid leaving expensive resources (compute clusters, online endpoints,
Bastion) running.
