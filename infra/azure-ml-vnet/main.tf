# -----------------------------------------------------------------------------
# BYO VNet foundation: a standalone networking layer for teams that bring their
# own VNet to an Azure Machine Learning deployment. Provisions a VNet, an AML
# compute subnet, a private-endpoints subnet, an NSG with service-tag rules, a
# route table, and a user-assigned managed identity. It does NOT create the
# workspace itself — wire these outputs into your workspace deployment.
# -----------------------------------------------------------------------------

resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_virtual_network" "this" {
  name                = "${var.name_prefix}-byo-vnet"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  address_space       = var.vnet_address_space
  tags                = var.tags
}

resource "azurerm_subnet" "aml" {
  name                 = "snet-aml-compute"
  resource_group_name  = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = [var.aml_subnet_prefix]

  service_endpoints = [
    "Microsoft.Storage",
    "Microsoft.KeyVault",
    "Microsoft.ContainerRegistry",
  ]
}

resource "azurerm_subnet" "pe" {
  name                 = "snet-private-endpoints"
  resource_group_name  = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = [var.pe_subnet_prefix]
}

resource "azurerm_network_security_group" "aml" {
  name                = "${var.name_prefix}-nsg-aml"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags

  # Inbound rules required by Azure Machine Learning compute (service tags).
  security_rule {
    name                       = "AzureMLInbound"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "44224"
    source_address_prefix      = "AzureMachineLearning"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "BatchNodeManagementInbound"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["29876", "29877"]
    source_address_prefix      = "BatchNodeManagement"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "aml" {
  subnet_id                 = azurerm_subnet.aml.id
  network_security_group_id = azurerm_network_security_group.aml.id
}

resource "azurerm_route_table" "aml" {
  name                = "${var.name_prefix}-rt-aml"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags
}

resource "azurerm_subnet_route_table_association" "aml" {
  subnet_id      = azurerm_subnet.aml.id
  route_table_id = azurerm_route_table.aml.id
}

resource "azurerm_user_assigned_identity" "workspace" {
  name                = "${var.name_prefix}-id-workspace"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags
}
