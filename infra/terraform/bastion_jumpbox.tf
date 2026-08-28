# -----------------------------------------------------------------------------
# Azure Bastion + Windows jump box for private access to the workspace. Human
# users sign in interactively; the attached identity is for automation.
# -----------------------------------------------------------------------------

resource "azurerm_public_ip" "bastion" {
  name                = "${var.name_prefix}-pip-bastion-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = var.tags
}

resource "azurerm_bastion_host" "this" {
  name                = "${var.name_prefix}-bastion-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  sku                 = "Standard"
  tags                = var.tags

  ip_configuration {
    name                 = "bastion-ipcfg"
    subnet_id            = azurerm_subnet.bastion.id
    public_ip_address_id = azurerm_public_ip.bastion.id
  }
}

resource "azurerm_user_assigned_identity" "jumpbox" {
  name                = "${var.name_prefix}-id-jumpbox-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags
}

# Jump box identity: least-privilege data-plane roles for day-to-day work.
resource "azurerm_role_assignment" "jumpbox_ml_ds" {
  scope                = azurerm_machine_learning_workspace.this.id
  role_definition_name = "AzureML Data Scientist"
  principal_id         = azurerm_user_assigned_identity.jumpbox.principal_id
}

resource "azurerm_network_interface" "jumpbox" {
  name                = "${var.name_prefix}-nic-jumpbox-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = azurerm_subnet.jumpbox.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "random_password" "jumpbox" {
  length      = 24
  special     = true
  min_upper   = 2
  min_lower   = 2
  min_numeric = 2
  min_special = 2
}

resource "azurerm_windows_virtual_machine" "jumpbox" {
  name                  = "${var.name_prefix}-jb"
  location              = azurerm_resource_group.this.location
  resource_group_name   = azurerm_resource_group.this.name
  size                  = var.jumpbox_vm_size
  admin_username        = var.jumpbox_admin_username
  admin_password        = random_password.jumpbox.result
  network_interface_ids = [azurerm_network_interface.jumpbox.id]
  tags                  = var.tags

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.jumpbox.id]
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsDesktop"
    offer     = "windows-11"
    sku       = "win11-23h2-pro"
    version   = "latest"
  }
}
