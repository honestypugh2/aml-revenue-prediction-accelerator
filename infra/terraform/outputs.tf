output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "workspace_name" {
  value       = azurerm_machine_learning_workspace.this.name
  description = "Set as RPA_AZURE_ML__WORKSPACE_NAME."
}

output "workspace_id" {
  value = azurerm_machine_learning_workspace.this.id
}

output "vnet_name" {
  value = azurerm_virtual_network.this.name
}

output "jumpbox_name" {
  value = azurerm_windows_virtual_machine.jumpbox.name
}

output "jumpbox_identity_client_id" {
  value       = azurerm_user_assigned_identity.jumpbox.client_id
  description = "Use with `az login --identity --username <client_id>` on the jump box."
}

output "jumpbox_admin_password" {
  value       = random_password.jumpbox.result
  sensitive   = true
  description = "Generated jump box admin password (sensitive). Rotate after first use."
}
