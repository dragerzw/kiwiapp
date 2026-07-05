terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS Region to deploy the state backend"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project (used for naming the state bucket)"
  type        = string
  default     = "kiwiapp"
}

data "aws_caller_identity" "current" {}

# ─── S3 STATE BUCKET ───
resource "aws_s3_bucket" "terraform_state" {
  # checkov:skip=CKV_AWS_145: KMS CMK is not required for this state bucket, AES256 is sufficient.
  # checkov:skip=CKV2_AWS_62: Event notifications not needed for terraform state.
  # checkov:skip=CKV2_AWS_61: Lifecycle config not required as state shouldn't expire.
  # checkov:skip=CKV_AWS_18: Access logging not strictly necessary for this private bucket.
  # checkov:skip=CKV_AWS_144: Cross-region replication not required for our current scale.
  bucket = "${var.project_name}-terraform-state-${data.aws_caller_identity.current.account_id}"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "enforce_tls" {
  bucket = aws_s3_bucket.terraform_state.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "EnforceTLSRequestsOnly"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.terraform_state.arn,
          "${aws_s3_bucket.terraform_state.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}

# ─── DYNAMODB LOCK TABLE ───
resource "aws_dynamodb_table" "terraform_locks" {
  # checkov:skip=CKV_AWS_119: AWS owned KMS key is sufficient, CMK not required.
  name         = "${var.project_name}-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }
}

output "state_bucket_name" {
  value       = aws_s3_bucket.terraform_state.bucket
  description = "S3 bucket for Terraform state — pass to -backend-config on init"
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.terraform_locks.name
  description = "DynamoDB table for state locking — pass to -backend-config on init"
}
