terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Configure via: terraform init -backend-config=backend.conf
  # See terraform/README.md for full init instructions.
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}

# ─── VARIABLES ───
variable "environment" {
  type    = string
  default = "production"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "db_password" {
  type      = string
  sensitive = true
  description = "MySQL root password for RDS. Store in 1Password/local secret — never commit."
}

variable "create_oidc_provider" {
  type        = bool
  default     = true
  description = "true = fresh AWS account with no GitHub OIDC provider yet"
}

variable "eip_allocation_id" {
  type        = string
  default     = null
  description = "Optional Elastic IP allocation ID to pin the NAT instance's outbound IP"
}

# ─── NETWORKING ───
module "networking" {
  source      = "../../modules/networking"
  environment = var.environment
  vpc_cidr    = "10.0.0.0/16"
}

# ─── NAT (cheap fck-nat t4g.nano instead of $32/mo AWS NAT Gateway) ───
# NOTE: Single NAT instance is a deliberate cost-optimisation.
# Upgrade to per-AZ NAT Gateways when multi-AZ HA becomes a hard requirement.
module "nat" {
  source                 = "../../modules/nat-instance"
  environment            = var.environment
  vpc_id                 = module.networking.vpc_id
  public_subnet_id       = module.networking.public_subnet_ids[0]
  private_route_table_id = module.networking.private_route_table_id
  eip_allocation_id      = var.eip_allocation_id

  # Ensure the NAT route exists before ECS tasks try to pull images from ECR
  depends_on = [module.networking]
}

# ─── DNS + ACM CERTIFICATE ───
# Creates the ACM cert for both subdomains and Route 53 alias A records.
# This module must be applied before compute/frontend since they consume the cert ARN.
module "dns" {
  source = "../../modules/dns"

  environment        = var.environment
  hosted_zone_name   = "thedrageradvantage.com"
  frontend_subdomain = "kiwiapp"
  api_subdomain      = "api.kiwiapp"

  # These are wired after compute and frontend are created (Terraform handles the ordering)
  cloudfront_domain = module.frontend.cloudfront_domain
  alb_dns_name      = module.compute.alb_dns_name
  alb_zone_id       = module.compute.alb_zone_id
}

# ─── COMPUTE (ECS Fargate + ALB + ECR) ───
module "compute" {
  source      = "../../modules/compute"
  environment = var.environment
  vpc_id      = module.networking.vpc_id

  public_subnet_ids  = module.networking.public_subnet_ids
  private_subnet_ids = module.networking.private_subnet_ids

  # ALB uses the ACM cert from the dns module for HTTPS
  alb_certificate_arn = module.dns.certificate_arn

  # ECS execution role can read all SSM params under /kiwiapp/production/*
  ecs_execution_ssm_parameter_path_prefixes = ["/kiwiapp/${var.environment}"]

  # Ensure NAT is ready before ECS tasks launch (otherwise ECR pulls fail)
  depends_on = [module.nat]
}

# ─── DATABASE (RDS MySQL 8.0) ───
module "database" {
  source             = "../../modules/database"
  environment        = var.environment
  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids

  # Only ECS Fargate tasks can connect to MySQL on port 3306
  ecs_security_group_id = module.compute.ecs_security_group_id
  db_password           = var.db_password
}

# ─── FRONTEND (S3 + CloudFront) ───
module "frontend" {
  source      = "../../modules/frontend"
  environment = var.environment

  # Custom domain — cert from dns module
  domain_names        = ["kiwiapp.thedrageradvantage.com"]
  acm_certificate_arn = module.dns.certificate_arn

  # Allow Terraform destroy of bucket contents in non-production
  client_bucket_force_destroy = var.environment != "production"
}

# ─── GITHUB ACTIONS OIDC IAM ───
module "github_oidc" {
  source      = "../../modules/iam-oidc"
  environment = var.environment

  github_repository       = "dragerzw/kiwiapp"
  create_oidc_provider    = var.create_oidc_provider
  github_job_workflow_ref = "dragerzw/kiwiapp/.github/workflows/deploy.yml@refs/heads/main"

  ecr_repository_arn          = module.compute.ecr_repository_arn
  ecs_service_arn             = module.compute.ecs_service_arn
  s3_bucket_arn               = module.frontend.client_bucket_arn
  cloudfront_distribution_arn = module.frontend.cloudfront_distribution_arn
  ecs_task_execution_role_arn = module.compute.ecs_task_execution_role_arn
  ecs_task_role_arn           = module.compute.ecs_task_role_arn
}

# ─── OUTPUTS (copy these into GitHub Secrets after apply) ───
output "github_actions_role_arn" {
  description = "→ GitHub Secret: AWS_ROLE_ARN"
  value       = module.github_oidc.github_actions_role_arn
}

output "ecr_repository_url" {
  description = "→ GitHub Secret: ECR_REPOSITORY_URL"
  value       = module.compute.ecr_repository_url
}

output "ecs_cluster_name" {
  description = "→ GitHub Secret: ECS_CLUSTER_NAME"
  value       = module.compute.ecs_cluster_name
}

output "ecs_service_name" {
  description = "→ GitHub Secret: ECS_SERVICE_NAME"
  value       = module.compute.ecs_service_name
}

output "ecs_task_family" {
  description = "→ GitHub Secret: ECS_TASK_DEFINITION"
  value       = module.compute.ecs_task_family
}

output "s3_bucket_name" {
  description = "→ GitHub Secret: S3_BUCKET_NAME"
  value       = module.frontend.client_bucket_name
}

output "cloudfront_distribution_id" {
  description = "→ GitHub Secret: CLOUDFRONT_DISTRIBUTION_ID"
  value       = module.frontend.cloudfront_distribution_id
}

output "frontend_url" {
  description = "Live frontend URL"
  value       = "https://${module.dns.frontend_fqdn}"
}

output "api_url" {
  description = "Live API URL — set as VITE_API_BASE_URL in GitHub Secrets"
  value       = "https://${module.dns.api_fqdn}"
}

output "rds_connection_url_template" {
  description = "DATABASE_URL template — substitute <PASSWORD> then store in SSM"
  sensitive   = true
  value       = module.database.rds_connection_url_template
}
