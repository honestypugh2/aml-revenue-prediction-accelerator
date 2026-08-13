# Terraform — Quickstart (public workspace)

Minimal, public-access Azure Machine Learning workspace for **learning and
demos with synthetic data**. No VNet, no private endpoints. **Not for
production.**

## Resources

- Resource group
- Storage account (default datastore, **identity-based** — shared keys disabled,
  with RBAC data roles for the workspace/compute identities)
- Key Vault
- Container Registry
- Application Insights
- Azure Machine Learning workspace (system-assigned identity)
- **Compute cluster** for training/batch jobs (scales to **zero** when idle)
- **Compute instance** for notebooks/EDA (personal, assigned to the deployer;
  disable with `create_compute_instance = false`)
- **RBAC**: `Storage Blob Data Contributor` + `Storage File Data Privileged
  Contributor` granted to the workspace identity, the cluster identity, and
  (optionally) the deploying user — everything job submission needs

This is a **one-command, end-to-end** learning environment: after `apply` you
can register the environment/data, then run data prep, exploration, training,
validation, evaluation, and batch inference with no further setup.

## Prerequisites

- Terraform >= 1.5
- Azure CLI (`az login`)
- Subscription roles sufficient to create the above **and assign roles**
  (`Contributor` + `User Access Administrator`, or `Owner`)

## Deploy

```bash
cp terraform.tfvars.example terraform.tfvars   # edit values
az login
terraform init
terraform plan
terraform apply
```

## Configure the accelerator

```bash
export RPA_AZURE_ML__SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
export RPA_AZURE_ML__RESOURCE_GROUP="$(terraform output -raw resource_group_name)"
export RPA_AZURE_ML__WORKSPACE_NAME="$(terraform output -raw workspace_name)"
uv run revenue-prediction info --env dev
```

## Grant storage permissions

Handled automatically: the workspace and compute-cluster identities (and,
unless disabled, the deploying user) receive `Storage Blob Data Contributor` and
`Storage File Data Privileged Contributor` on the storage account — required for
identity-based job submission. See
[`docs/security/networking.md`](../../docs/security/networking.md).

## Cost control

- The compute cluster scales to **0 nodes** when idle
  (`compute_cluster_idle_before_scale_down`, default `PT120S`).
- The **compute instance runs (and bills) while started** — stop it in Studio
  when idle, or set `create_compute_instance = false`.
- ACR is Standard and Storage is LRS (cheapest suitable tiers for a demo).

## Clean up

```bash
terraform destroy
```

> `terraform destroy` permanently deletes these resources. Ensure no other
> workloads depend on them.

> Note: These Terraform files follow the `azurerm` provider conventions. Run
> `terraform init && terraform validate` in your environment before applying.
