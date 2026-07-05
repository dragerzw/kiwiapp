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

variable "client_bucket_force_destroy" {
  type        = bool
  default     = false
  description = "Allow Terraform to destroy the bucket even if it has objects (true for staging)"
}

variable "domain_names" {
  type        = list(string)
  default     = []
  description = "Custom domain aliases for the CloudFront distribution (e.g. [\"kiwiapp.thedrageradvantage.com\"])"
}

variable "acm_certificate_arn" {
  type        = string
  default     = null
  description = "ACM certificate ARN in us-east-1 for the CloudFront custom domain. Required when domain_names is non-empty."
}

data "aws_caller_identity" "current" {}

locals {
  has_custom_domain = length(var.domain_names) > 0 && var.acm_certificate_arn != null
}

# ─── S3 BUCKET ───
resource "aws_s3_bucket" "client" {
  # checkov:skip=CKV_AWS_145: AES256 is sufficient; CMK not required.
  # checkov:skip=CKV2_AWS_62: Event notifications not needed.
  # checkov:skip=CKV2_AWS_61: Lifecycle config not required.
  # checkov:skip=CKV_AWS_18: Access logging not strictly necessary.
  # checkov:skip=CKV_AWS_144: Cross-region replication not required.
  bucket        = "kiwi-${var.environment}-client-${data.aws_caller_identity.current.account_id}"
  force_destroy = var.client_bucket_force_destroy
}

resource "aws_s3_bucket_versioning" "client" {
  bucket = aws_s3_bucket.client.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_ownership_controls" "client" {
  bucket = aws_s3_bucket.client.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_public_access_block" "client" {
  bucket                  = aws_s3_bucket.client.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "client" {
  bucket = aws_s3_bucket.client.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ─── CLOUDFRONT ───
resource "aws_cloudfront_origin_access_control" "client" {
  name                              = "kiwi-${var.environment}-oac"
  description                       = "OAC for KiwiApp client S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "client" {
  # checkov:skip=CKV_AWS_86: Access logging not strictly necessary.
  # checkov:skip=CKV_AWS_310: Origin failover not required for simple SPA.
  # checkov:skip=CKV_AWS_68: WAF cost prohibitive for this tier.
  # checkov:skip=CKV2_AWS_32: Response headers policy not required.
  # checkov:skip=CKV2_AWS_47: AMR for Log4j not required for static SPA.
  # checkov:skip=CKV_AWS_374: Geo restriction intentionally disabled.
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  # Custom domain aliases when a cert is provided
  aliases = local.has_custom_domain ? var.domain_names : []

  origin {
    domain_name              = aws_s3_bucket.client.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.client.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.client.id

    s3_origin_config {
      origin_access_identity = ""
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.client.id}"

    # AWS managed CachingOptimized policy
    cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"

    viewer_protocol_policy = "redirect-to-https"
    compress               = true
  }

  # React Router SPA — redirect all 403/404 → index.html
  custom_error_response {
    error_caching_min_ttl = 300
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
  }

  custom_error_response {
    error_caching_min_ttl = 300
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # Use custom cert when domain is configured; otherwise use CloudFront default
  viewer_certificate {
    cloudfront_default_certificate = !local.has_custom_domain
    acm_certificate_arn            = local.has_custom_domain ? var.acm_certificate_arn : null
    ssl_support_method             = local.has_custom_domain ? "sni-only" : null
    minimum_protocol_version       = local.has_custom_domain ? "TLSv1.2_2021" : "TLSv1"
  }
}

# ─── S3 BUCKET POLICY — CloudFront OAC only ───
resource "aws_s3_bucket_policy" "client" {
  bucket = aws_s3_bucket.client.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyInsecureConnections"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.client.arn,
          "${aws_s3_bucket.client.arn}/*"
        ]
        Condition = {
          Bool = { "aws:SecureTransport" = "false" }
        }
      },
      {
        Sid    = "AllowCloudFrontOAC"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.client.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn"     = aws_cloudfront_distribution.client.arn
            "AWS:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

# ─── OUTPUTS ───
output "cloudfront_domain" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.client.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (used for cache invalidation in deploy workflow)"
  value       = aws_cloudfront_distribution.client.id
}

output "cloudfront_distribution_arn" {
  description = "CloudFront ARN (used by IAM-OIDC module)"
  value       = aws_cloudfront_distribution.client.arn
}

output "client_bucket_name" {
  description = "S3 bucket name for client assets"
  value       = aws_s3_bucket.client.bucket
}

output "client_bucket_arn" {
  description = "S3 bucket ARN (used by IAM-OIDC module)"
  value       = aws_s3_bucket.client.arn
}
