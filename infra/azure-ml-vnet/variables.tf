variable "name_prefix" {
  type    = string
  default = "revpred"
}

variable "location" {
  type    = string
  default = "eastus2"
}

variable "resource_group_name" {
  type    = string
  default = "rg-revenue-prediction-network"
}

variable "vnet_address_space" {
  type    = list(string)
  default = ["10.40.0.0/16"]
}

variable "aml_subnet_prefix" {
  type    = string
  default = "10.40.1.0/24"
}

variable "pe_subnet_prefix" {
  type    = string
  default = "10.40.2.0/24"
}

variable "tags" {
  type = map(string)
  default = {
    workload    = "revenue-prediction-accelerator"
    data        = "synthetic"
    environment = "shared"
    profile     = "byo-vnet"
  }
}
