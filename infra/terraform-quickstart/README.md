# Terraform — Quickstart (public workspace)

Minimal, public-access Azure Machine Learning workspace for **learning and
demos with synthetic data**. No VNet, no private endpoints. **Not for
production.**

## Resources

- Resource group
- Storage account (default datastore)
- Key Vault
- Container Registry
- Application Insights
- Azure Machine Learning workspace (system-assigned identity)

## Prerequisites

- Terraform >= 1.5
- Azure CLI (`az login`)
- Subscription roles sufficient to create the above (Contributor + ability to
  assign roles)

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

## Grant storage permissions (required for job submission)

The workspace managed identity needs `Storage Blob Data Contributor` and
`Storage File Data Privileged Contributor` on the storage account. See
[`docs/security/networking.md`](../../docs/security/networking.md).

## Clean up

```bash
terraform destroy
```

> `terraform destroy` permanently deletes these resources. Ensure no other
> workloads depend on them.

> Note: These Terraform files follow the `azurerm` provider conventions but were
> not executed in the authoring environment (no Terraform binary present). Run
> `terraform init && terraform validate` in your environment before applying.
