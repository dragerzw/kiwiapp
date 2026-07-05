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
  description = "Deployment environment (e.g., staging, production)"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  type        = list(string)
  description = "List of CIDR blocks for public subnets"
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  type        = list(string)
  description = "List of CIDR blocks for private subnets"
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "excluded_availability_zones" {
  type        = list(string)
  description = "Availability zones to exclude for this region/account"
  default     = []
}

data "aws_availability_zones" "available" {
  state         = "available"
  exclude_names = var.excluded_availability_zones
}

locals {
  sorted_azs               = sort(data.aws_availability_zones.available.names)
  required_subnet_az_count = max(length(var.public_subnets), length(var.private_subnets))
  has_required_azs         = length(local.sorted_azs) >= local.required_subnet_az_count
}

resource "aws_vpc" "main" {
  # checkov:skip=CKV2_AWS_11: VPC Flow logs are cost prohibitive for this tier.
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  lifecycle {
    precondition {
      condition     = local.has_required_azs
      error_message = "Not enough available availability zones remain after exclusions to distribute subnets across distinct AZs."
    }
  }

  tags = {
    Name        = "kiwi-${var.environment}-vpc"
    Environment = var.environment
    Project     = "kiwiapp"
  }
}

# Restrict the default security group — defence in depth
resource "aws_default_security_group" "default" {
  vpc_id  = aws_vpc.main.id
  ingress = []
  egress  = []
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "kiwi-${var.environment}-igw"
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  # checkov:skip=CKV_AWS_130: Public IP on launch is intended for public subnets.
  count                   = length(var.public_subnets)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnets[count.index]
  availability_zone       = local.has_required_azs ? local.sorted_azs[count.index] : null
  map_public_ip_on_launch = true

  tags = {
    Name        = "kiwi-${var.environment}-public-${count.index + 1}"
    Environment = var.environment
    Type        = "Public"
  }
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnets)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnets[count.index]
  availability_zone = local.has_required_azs ? local.sorted_azs[count.index] : null

  tags = {
    Name        = "kiwi-${var.environment}-private-${count.index + 1}"
    Environment = var.environment
    Type        = "Private"
  }
}

# ─── ROUTE TABLES ───
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name        = "kiwi-${var.environment}-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private route table — outbound routing added by the nat-instance module
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "kiwi-${var.environment}-private-rt"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs (for ALB)"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs (for ECS tasks and RDS)"
  value       = aws_subnet.private[*].id
}

output "private_route_table_id" {
  description = "Private route table ID — passed to nat-instance module to add 0.0.0.0/0 route"
  value       = aws_route_table.private.id
}
