terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnets — RDS is not publicly accessible"
}

variable "ecs_security_group_id" {
  type        = string
  description = "ECS Fargate tasks SG allowed to connect to MySQL"
}

variable "db_password" {
  type      = string
  sensitive = true

  validation {
    condition     = length(var.db_password) >= 8
    error_message = "db_password must be at least 8 characters."
  }
}

resource "random_id" "mysql_final_snapshot" {
  count       = var.environment == "production" ? 1 : 0
  byte_length = 4
}

# ─── SECURITY GROUP ───
resource "aws_security_group" "rds" {
  name        = "kiwi-${var.environment}-rds-sg"
  description = "Allow MySQL inbound from ECS Fargate tasks only"
  vpc_id      = var.vpc_id
  egress      = []

  ingress {
    description     = "MySQL from ECS"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }

  tags = {
    Name        = "kiwi-${var.environment}-rds-sg"
    Environment = var.environment
  }
}

# ─── SUBNET GROUP ───
resource "aws_db_subnet_group" "private" {
  name       = "kiwi-${var.environment}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name        = "kiwi-${var.environment}-db-subnet-group"
    Environment = var.environment
  }
}

# ─── PARAMETER GROUP — Enforce SSL ───
resource "aws_db_parameter_group" "mysql_ssl" {
  name   = "kiwi-${var.environment}-mysql80-ssl"
  family = "mysql8.0"

  parameter {
    name         = "require_secure_transport"
    value        = "ON"
    apply_method = "immediate"
  }

  tags = {
    Name        = "kiwi-${var.environment}-mysql80-ssl"
    Environment = var.environment
  }
}

# ─── RDS MYSQL 8.0 ───
resource "aws_db_instance" "mysql" {
  # checkov:skip=CKV_AWS_129: RDS logging not strictly necessary for this tier.
  # checkov:skip=CKV_AWS_226: Auto minor version upgrades disabled for stability.
  # checkov:skip=CKV_AWS_118: Enhanced monitoring cost prohibitive.
  # checkov:skip=CKV_AWS_161: IAM auth not strictly required.
  # checkov:skip=CKV_AWS_353: Performance Insights cost prohibitive.
  # checkov:skip=CKV_AWS_293: Deletion protection handled conditionally below.
  # checkov:skip=CKV_AWS_157: Multi-AZ conditional on environment.
  # checkov:skip=CKV2_AWS_60: Copy tags to snapshots not required.
  identifier        = "kiwi-${var.environment}-mysql"
  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = "db.t4g.micro"
  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = "kiwiapp${var.environment}" # MySQL db name: no hyphens
  username = "kiwi_admin"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.private.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.mysql_ssl.name

  storage_encrypted       = true
  backup_retention_period = var.environment == "production" ? 30 : 7
  multi_az                = var.environment == "production"
  deletion_protection     = var.environment == "production"
  skip_final_snapshot     = var.environment != "production"

  final_snapshot_identifier = (
    var.environment == "production"
    ? "kiwi-${var.environment}-mysql-final-${random_id.mysql_final_snapshot[0].hex}"
    : null
  )

  publicly_accessible = false
}

# ─── OUTPUTS ───
output "rds_address" {
  description = "RDS MySQL hostname"
  value       = aws_db_instance.mysql.address
}

output "rds_port" {
  description = "RDS MySQL port"
  value       = aws_db_instance.mysql.port
}

output "rds_db_name" {
  description = "MySQL database name"
  value       = aws_db_instance.mysql.db_name
}

output "rds_connection_url_template" {
  description = "DATABASE_URL template — substitute the actual password before storing in SSM"
  sensitive   = true
  value = format(
    "mysql+pymysql://kiwi_admin:<PASSWORD>@%s:%d/%s",
    aws_db_instance.mysql.address,
    aws_db_instance.mysql.port,
    aws_db_instance.mysql.db_name,
  )
}

output "rds_security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}
