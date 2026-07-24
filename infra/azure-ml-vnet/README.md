# Terraform — BYO VNet foundation

A **standalone networking layer** for teams that bring their own VNet to an
Azure Machine Learning deployment. It provisions only the network primitives and
a managed identity; it does **not** create the workspace.

## Resources

- VNet with two subnets:
  - `snet-aml-compute` (with `Microsoft.Storage`, `Microsoft.KeyVault`,
    `Microsoft.ContainerRegistry` service endpoints),
  - `snet-private-endpoints`.
- NSG with the Azure Machine Learning service-tag inbound rules
  (`AzureMachineLearning`, `BatchNodeManagement`).
- Route table associated with the compute subnet.
- User-assigned managed identity for the workspace.

## Usage

```bash
cp terraform.tfvars.example terraform.tfvars
az login
terraform init
terraform plan
terraform apply
```

Then wire the outputs (`aml_subnet_id`, `private_endpoints_subnet_id`,
`workspace_identity_id`) into your workspace deployment (Bicep, Terraform, or
portal), attaching the workspace to this VNet with private endpoints.

## Notes

- Adjust address spaces to avoid overlap with existing networks.
- For fully-locked-down egress, pair this with a firewall/NAT gateway and the
  approved-outbound rules from the
  [managed network guidance](https://learn.microsoft.com/azure/machine-learning/how-to-managed-network).
- Not executed in the authoring environment (no Terraform binary present). Run
  `terraform validate` before applying.
