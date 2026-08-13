# -----------------------------------------------------------------------------
# QUICKSTART profile: minimal, public Azure Machine Learning workspace.
# For learning and demos with synthetic data only. NOT for production.
# -----------------------------------------------------------------------------

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

locals {
  suffix = random_string.suffix.result
}

resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_log_analytics_workspace" "this" {
  name                = "${var.name_prefix}-law-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_application_insights" "this" {
  name                = "${var.name_prefix}-ai-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.this.id
  tags                = var.tags
}

resource "azurerm_key_vault" "this" {
  name                      = "${var.name_prefix}-kv-${local.suffix}"
  location                  = azurerm_resource_group.this.location
  resource_group_name       = azurerm_resource_group.this.name
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  purge_protection_enabled  = true
  enable_rbac_authorization = true
  tags                      = var.tags
}

resource "azurerm_storage_account" "this" {
  name                            = "${var.name_prefix}st${local.suffix}"
  location                        = azurerm_resource_group.this.location
  resource_group_name             = azurerm_resource_group.this.name
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  # This subscription's policy enforces keyless storage; the provider uses Entra
  # (storage_use_azuread) and the workspace/compute identities get RBAC data
  # roles below for identity-based datastore access.
  shared_access_key_enabled = false
  tags                      = var.tags
}

resource "azurerm_container_registry" "this" {
  name                = "${var.name_prefix}acr${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  sku                 = "Standard"
  admin_enabled       = false
  tags                = var.tags
}

resource "azurerm_machine_learning_workspace" "this" {
  name                          = "${var.name_prefix}-mlw-${local.suffix}"
  location                      = azurerm_resource_group.this.location
  resource_group_name           = azurerm_resource_group.this.name
  application_insights_id       = azurerm_application_insights.this.id
  key_vault_id                  = azurerm_key_vault.this.id
  storage_account_id            = azurerm_storage_account.this.id
  container_registry_id         = azurerm_container_registry.this.id
  public_network_access_enabled = true
  tags                          = var.tags

  identity {
    type = "SystemAssigned"
  }
}

data "azurerm_client_config" "current" {}

# --- Identity-based access to the default datastore ---------------------------
# Shared storage keys are disabled, so jobs authenticate with the workspace and
# compute managed identities. Azure ML auto-assigns the *workspace* identity the
# storage data roles on the default account, so we only grant the compute
# cluster identity and the deploying user below.

# --- Training / batch compute cluster (scales to zero when idle) --------------
resource "azurerm_machine_learning_compute_cluster" "cluster" {
  name                          = var.compute_cluster_name
  location                      = azurerm_resource_group.this.location
  machine_learning_workspace_id = azurerm_machine_learning_workspace.this.id
  vm_size                       = var.compute_cluster_vm_size
  vm_priority                   = "Dedicated"

  scale_settings {
    min_node_count                       = var.compute_cluster_min_nodes
    max_node_count                       = var.compute_cluster_max_nodes
    scale_down_nodes_after_idle_duration = var.compute_cluster_idle_before_scale_down
  }

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

resource "azurerm_role_assignment" "cluster_blob" {
  scope                            = azurerm_storage_account.this.id
  role_definition_name             = "Storage Blob Data Contributor"
  principal_id                     = azurerm_machine_learning_compute_cluster.cluster.identity[0].principal_id
  skip_service_principal_aad_check = true
}

resource "azurerm_role_assignment" "cluster_file" {
  scope                            = azurerm_storage_account.this.id
  role_definition_name             = "Storage File Data Privileged Contributor"
  principal_id                     = azurerm_machine_learning_compute_cluster.cluster.identity[0].principal_id
  skip_service_principal_aad_check = true
}

# --- Personal compute instance for notebooks / exploration -------------------
resource "azurerm_machine_learning_compute_instance" "instance" {
  count                         = var.create_compute_instance ? 1 : 0
  name                          = "ci-${local.suffix}"
  machine_learning_workspace_id = azurerm_machine_learning_workspace.this.id
  virtual_machine_size          = var.compute_instance_vm_size
  authorization_type            = "personal"

  assign_to_user {
    object_id = data.azurerm_client_config.current.object_id
    tenant_id = data.azurerm_client_config.current.tenant_id
  }

  tags = var.tags
}

# --- Optional: let the deploying user upload data assets from their machine --
resource "azurerm_role_assignment" "user_blob" {
  count                = var.assign_current_user_storage_roles ? 1 : 0
  scope                = azurerm_storage_account.this.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "user_file" {
  count                = var.assign_current_user_storage_roles ? 1 : 0
  scope                = azurerm_storage_account.this.id
  role_definition_name = "Storage File Data Privileged Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}
