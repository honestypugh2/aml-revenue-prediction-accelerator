output "resource_group_name" {
  value       = azurerm_resource_group.this.name
  description = "Resource group containing the workspace."
}

output "workspace_name" {
  value       = azurerm_machine_learning_workspace.this.name
  description = "Azure Machine Learning workspace name (set as RPA_AZURE_ML__WORKSPACE_NAME)."
}

output "workspace_id" {
  value       = azurerm_machine_learning_workspace.this.id
  description = "Full resource ID of the workspace."
}

output "storage_account_name" {
  value = azurerm_storage_account.this.name
}

output "key_vault_name" {
  value = azurerm_key_vault.this.name
}

output "container_registry_name" {
  value = azurerm_container_registry.this.name
}

output "compute_cluster_name" {
  value       = azurerm_machine_learning_compute_cluster.cluster.name
  description = "Training/batch compute cluster (scales to zero when idle)."
}

output "compute_instance_name" {
  value       = try(azurerm_machine_learning_compute_instance.instance[0].name, null)
  description = "Personal compute instance for notebooks/EDA (null when disabled)."
}

output "aml_studio_url" {
  value       = "https://ml.azure.com/home?wsid=${azurerm_machine_learning_workspace.this.id}&tid=${data.azurerm_client_config.current.tenant_id}"
  description = "Deep link to the workspace in Azure ML Studio."
}
