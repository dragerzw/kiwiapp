terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "environment" {
  type        = string
  description = "Deployment environment"
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_id" {
  type        = string
  description = "Public subnet ID where the NAT instance will live"
}

variable "private_route_table_id" {
  type        = string
  description = "Private route table ID to update with the NAT route"
}

variable "eip_allocation_id" {
  type        = string
  description = "Optional Elastic IP allocation ID for a static outbound IP"
  default     = null
}

# fck-nat: community-maintained, highly available NAT instance on a t4g.nano
# ~$3/mo vs ~$32/mo for AWS Managed NAT Gateway. Same approach used by Edutrend.
module "fck_nat" {
  # checkov:skip=CKV_TF_1: Registry module versioning is acceptable here.
  source  = "RaJiska/fck-nat/aws"
  version = "1.3.0"

  name      = "kiwi-${var.environment}-nat"
  vpc_id    = var.vpc_id
  subnet_id = var.public_subnet_id

  # Automatically adds 0.0.0.0/0 → NAT ENI route to the private route table
  update_route_tables = true
  route_tables_ids    = { "private_route" = var.private_route_table_id }

  eip_allocation_ids = var.eip_allocation_id != null ? [var.eip_allocation_id] : []

  instance_type = "t4g.nano"
}
