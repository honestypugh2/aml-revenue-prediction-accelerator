variable "name_prefix" {
  type        = string
  default     = "revpred"
  description = "Short, lowercase prefix used to derive resource names."
  validation {
    condition     = can(regex("^[a-z][a-z0-9]{2,10}$", var.name_prefix))
    error_message = "name_prefix must be 3-11 lowercase alphanumeric characters starting with a letter."
  }
}

variable "location" {
  type        = string
  default     = "eastus2"
  description = "Azure region."
}

variable "resource_group_name" {
  type        = string
  default     = "rg-revenue-prediction-secure"
  description = "Resource group to create."
}

variable "vnet_address_space" {
  type        = list(string)
  default     = ["10.30.0.0/16"]
  description = "Address space for the VNet."
}

variable "subnet_private_endpoints" {
  type        = string
  default     = "10.30.1.0/24"
  description = "Subnet CIDR for private endpoints."
}

variable "subnet_jumpbox" {
  type        = string
  default     = "10.30.2.0/24"
  description = "Subnet CIDR for the jump box."
}

variable "subnet_bastion" {
  type        = string
  default     = "10.30.3.0/26"
  description = "AzureBastionSubnet CIDR (must be /26 or larger)."
}

variable "jumpbox_admin_username" {
  type        = string
  default     = "azureuser"
  description = "Admin username for the jump box VM."
}

variable "jumpbox_vm_size" {
  type        = string
  default     = "Standard_D2s_v5"
  description = "VM size for the jump box."
}

variable "tags" {
  type = map(string)
  default = {
    workload    = "revenue-prediction-accelerator"
    data        = "synthetic"
    environment = "prod"
    profile     = "secure"
  }
  description = "Tags applied to all resources."
}
