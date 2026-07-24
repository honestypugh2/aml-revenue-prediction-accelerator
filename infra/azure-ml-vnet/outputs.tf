output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "vnet_id" {
  value = azurerm_virtual_network.this.id
}

output "aml_subnet_id" {
  value       = azurerm_subnet.aml.id
  description = "Subnet for AML compute; wire into your workspace deployment."
}

output "private_endpoints_subnet_id" {
  value = azurerm_subnet.pe.id
}

output "workspace_identity_id" {
  value = azurerm_user_assigned_identity.workspace.id
}

output "workspace_identity_principal_id" {
  value = azurerm_user_assigned_identity.workspace.principal_id
}
