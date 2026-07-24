# Infrastructure as Code

Deploy the Azure Machine Learning workspace and dependencies for the accelerator.
**Synthetic data only.** Production deployments must follow the official
secure-workspace guidance.

## Profiles

| Profile | Path | Isolation | Use |
| --- | --- | --- | --- |
| Quickstart (Terraform) | [`terraform-quickstart/`](terraform-quickstart/) | Public | Learning / demos |
| Quickstart (Bicep) | [`bicep/`](bicep/) with `quickstart.bicepparam` | Public | Learning / demos |
| Secure (Terraform) | [`terraform/`](terraform/) | Managed VNet + private endpoints + Bastion/jump box | Production-like |
| Secure (Bicep) | [`bicep/`](bicep/) with `secure.bicepparam` | Managed VNet, firewalled deps | Production-like |
| BYO VNet foundation | [`azure-ml-vnet/`](azure-ml-vnet/) | Networking layer only | Bring-your-own-VNet |

Both Bicep and Terraform are provided so teams can use their preferred tool. The
approach (three-tier: quickstart, secure managed VNet, BYO VNet) is adapted from
the MIT-licensed reference repository; see
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) and
[ADR 0002](../docs/architecture/adr/0002-reference-repository-reuse.md).

## Bicep quickstart

```bash
az group create -n rg-revenue-prediction-quickstart -l eastus2
az deployment group create \
  -g rg-revenue-prediction-quickstart \
  -f infra/bicep/main.bicep \
  -p infra/bicep/quickstart.bicepparam
```

## Bicep secure

```bash
az group create -n rg-revenue-prediction-secure -l eastus2
az deployment group create \
  -g rg-revenue-prediction-secure \
  -f infra/bicep/main.bicep \
  -p infra/bicep/secure.bicepparam
```

> The secure Bicep template firewalls dependencies and enables managed VNet. For
> full private-endpoint + Bastion/jump-box topology, use the secure Terraform
> profile, which implements the complete network.

## Terraform

See each subdirectory's README for prerequisites, deployment, and cleanup.

## Validation status

- **Bicep**: compiled with `az bicep build` in the authoring environment
  (`main.bicep`, `quickstart.bicepparam`, `secure.bicepparam` — no errors).
- **Terraform**: written to `azurerm` provider conventions but **not** executed
  in the authoring environment (no Terraform binary available). Run
  `terraform init && terraform validate` in your environment before applying.

## Required permissions and post-deploy steps

See [`docs/security/networking.md`](../docs/security/networking.md) for RBAC and
the critical storage role assignments required for job submission, and
[`docs/operations/cost-and-cleanup.md`](../docs/operations/cost-and-cleanup.md)
to control cost.
