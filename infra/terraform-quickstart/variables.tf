variable "name_prefix" {
  type        = string
  description = "Short, lowercase prefix used to derive resource names."
  default     = "revpred"
  validation {
    condition     = can(regex("^[a-z][a-z0-9]{2,10}$", var.name_prefix))
    error_message = "name_prefix must be 3-11 lowercase alphanumeric characters starting with a letter."
  }
}

variable "location" {
  type        = string
  description = "Azure region."
  default     = "eastus2"
}

variable "resource_group_name" {
  type        = string
  description = "Resource group to create for the workspace."
  default     = "rg-revenue-prediction-quickstart"
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to all resources."
  default = {
    workload    = "revenue-prediction-accelerator"
    data        = "synthetic"
    environment = "dev"
    profile     = "quickstart"
  }
}
