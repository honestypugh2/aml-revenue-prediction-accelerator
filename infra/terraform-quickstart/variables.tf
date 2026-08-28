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

variable "create_compute_instance" {
  type        = bool
  description = "Create a personal compute instance (notebooks/EDA) assigned to the deploying user."
  default     = true
}

variable "compute_instance_vm_size" {
  type        = string
  description = "VM size for the personal compute instance."
  default     = "Standard_DS3_v2"
}

variable "compute_cluster_name" {
  type        = string
  description = "Name of the training/batch compute cluster (unique within the workspace)."
  default     = "cpu-cluster"
  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9-]{1,15}$", var.compute_cluster_name))
    error_message = "compute_cluster_name must be 2-16 chars, start with a letter, alphanumeric or hyphen."
  }
}

variable "compute_cluster_vm_size" {
  type        = string
  description = "VM size for training/batch compute cluster nodes."
  default     = "Standard_DS3_v2"
}

variable "compute_cluster_min_nodes" {
  type        = number
  description = "Minimum nodes; 0 lets the cluster scale to zero when idle (cost control)."
  default     = 0
}

variable "compute_cluster_max_nodes" {
  type        = number
  description = "Maximum nodes the cluster can scale up to."
  default     = 2
}

variable "compute_cluster_idle_before_scale_down" {
  type        = string
  description = "ISO-8601 idle duration before the cluster scales down (e.g. PT120S)."
  default     = "PT120S"
}

variable "assign_current_user_storage_roles" {
  type        = bool
  description = "Grant the deploying user Blob/File data roles so local data-asset uploads work."
  default     = true
}

variable "storage_public_network_access" {
  type        = bool
  description = "Enable the storage account public endpoint (quickstart/demo profile only)."
  default     = true
}

variable "storage_extra_tags" {
  type        = map(string)
  description = "Extra tags for the storage account, e.g. a policy-exemption tag."
  default = {
    SecurityControl = "Ignore"
  }
}
