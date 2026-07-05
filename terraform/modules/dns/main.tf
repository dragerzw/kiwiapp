terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ─── VARIABLES ───
variable "environment" { type = string }

variable "hosted_zone_name" {
  type        = string
  description = "Root domain managed in Route 53 (e.g. thedrageradvantage.com)"
}

variable "frontend_subdomain" {
  type        = string
  description = "Subdomain for the React SPA (e.g. kiwiapp)"
}

variable "api_subdomain" {
  type        = string
  description = "Subdomain for the Flask API (e.g. api.kiwiapp)"
}

variable "cloudfront_domain" {
  type        = string
  description = "CloudFront distribution domain (from frontend module output)"
}

variable "cloudfront_zone_id" {
  type        = string
  description = "CloudFront hosted zone ID — always Z2FDTNDATAQYW2 for all distributions"
  default     = "Z2FDTNDATAQYW2"
}

variable "alb_dns_name" {
  type        = string
  description = "ALB DNS name (from compute module output)"
}

variable "alb_zone_id" {
  type        = string
  description = "ALB hosted zone ID (from compute module output)"
}

# ─── ROUTE 53 HOSTED ZONE ───
data "aws_route53_zone" "main" {
  name         = var.hosted_zone_name
  private_zone = false
}

# ─── ACM CERTIFICATE ───
# Single cert covering both frontend and API subdomains.
# Must be in us-east-1 for CloudFront (already enforced by the root module provider).
resource "aws_acm_certificate" "main" {
  domain_name               = "${var.frontend_subdomain}.${var.hosted_zone_name}"
  subject_alternative_names = ["${var.api_subdomain}.${var.hosted_zone_name}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "kiwi-${var.environment}-cert"
    Environment = var.environment
  }
}

# ─── DNS VALIDATION RECORDS ───
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.main.zone_id
}

resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for r in aws_route53_record.cert_validation : r.fqdn]
}

# ─── ROUTE 53 ALIAS RECORDS ───
# Frontend SPA → CloudFront
resource "aws_route53_record" "frontend" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${var.frontend_subdomain}.${var.hosted_zone_name}"
  type    = "A"

  alias {
    name                   = var.cloudfront_domain
    zone_id                = var.cloudfront_zone_id
    evaluate_target_health = false
  }
}

# API → ALB
resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${var.api_subdomain}.${var.hosted_zone_name}"
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# ─── OUTPUTS ───
output "certificate_arn" {
  description = "ACM certificate ARN — pass to compute (ALB) and frontend (CloudFront) modules"
  value       = aws_acm_certificate_validation.main.certificate_arn
}

output "frontend_fqdn" {
  description = "Fully-qualified frontend domain"
  value       = aws_route53_record.frontend.fqdn
}

output "api_fqdn" {
  description = "Fully-qualified API domain"
  value       = aws_route53_record.api.fqdn
}
