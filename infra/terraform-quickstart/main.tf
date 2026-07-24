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

resource "azurerm_application_insights" "this" {
  name                = "${var.name_prefix}-ai-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  application_type    = "web"
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
  name                     = "${var.name_prefix}st${local.suffix}"
  location                 = azurerm_resource_group.this.location
  resource_group_name      = azurerm_resource_group.this.name
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  allow_nested_items_to_be_public = false
  tags                     = var.tags
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
  name                    = "${var.name_prefix}-mlw-${local.suffix}"
  location                = azurerm_resource_group.this.location
  resource_group_name     = azurerm_resource_group.this.name
  application_insights_id = azurerm_application_insights.this.id
  key_vault_id            = azurerm_key_vault.this.id
  storage_account_id      = azurerm_storage_account.this.id
  container_registry_id   = azurerm_container_registry.this.id
  public_network_access_enabled = true
  tags                    = var.tags

  identity {
    type = "SystemAssigned"
  }
}

data "azurerm_client_config" "current" {}
