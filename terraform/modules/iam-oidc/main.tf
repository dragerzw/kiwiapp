terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

variable "environment" { type = string }

variable "github_repository" {
  type        = string
  description = "GitHub repo in org/repo format (e.g. dragerzw/kiwiapp)"
}

variable "github_job_workflow_ref" {
  type        = string
  description = "Allowed workflow ref: org/repo/.github/workflows/deploy.yml@refs/heads/main"
}

variable "create_oidc_provider" {
  type        = bool
  default     = false
  description = "Set to true if this AWS account does not yet have a GitHub OIDC provider"
}

variable "ecr_repository_arn"          { type = string }
variable "ecs_service_arn"             { type = string }
variable "s3_bucket_arn"               { type = string }
variable "cloudfront_distribution_arn" { type = string }
variable "ecs_task_execution_role_arn" { type = string }
variable "ecs_task_role_arn"           { type = string }

# ─── GITHUB OIDC PROVIDER ───
data "tls_certificate" "github" {
  count = var.create_oidc_provider ? 1 : 0
  url   = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_openid_connect_provider" "github" {
  count           = var.create_oidc_provider ? 1 : 0
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.github[0].certificates[length(data.tls_certificate.github[0].certificates) - 1].sha1_fingerprint]
}

data "aws_iam_openid_connect_provider" "github" {
  count = var.create_oidc_provider ? 0 : 1
  url   = "https://token.actions.githubusercontent.com"
}

locals {
  oidc_provider_arn = (
    var.create_oidc_provider
    ? aws_iam_openid_connect_provider.github[0].arn
    : data.aws_iam_openid_connect_provider.github[0].arn
  )
}

# ─── GITHUB ACTIONS DEPLOY ROLE ───
resource "aws_iam_role" "github_actions" {
  name = "kiwi-${var.environment}-github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = local.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringLike = {
            # Scoped to this repo + GitHub environment only
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_repository}:environment:${var.environment}"
          }
          StringEquals = {
            "token.actions.githubusercontent.com:aud"              = "sts.amazonaws.com"
            "token.actions.githubusercontent.com:job_workflow_ref" = var.github_job_workflow_ref
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "github_actions" {
  name = "kiwi-${var.environment}-github-actions-policy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # ECR auth token — can't be scoped to a single repo
      {
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      # ECR image operations on kiwi ECR repo only
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetRepositoryPolicy",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:BatchGetImage"
        ]
        Resource = var.ecr_repository_arn
      },
      # ECS service update for rolling deploys
      {
        Effect = "Allow"
        Action = ["ecs:UpdateService", "ecs:DescribeServices"]
        Resource = var.ecs_service_arn
      },
      # Task definition operations — resource-level permissions not supported by AWS
      # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/security_iam_id-based-policy-examples.html
      {
        Effect   = "Allow"
        Action   = ["ecs:DescribeTaskDefinition", "ecs:RegisterTaskDefinition"]
        Resource = "*"
      },
      # S3 sync for frontend assets
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket", "s3:GetBucketLocation"]
        Resource = var.s3_bucket_arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:AbortMultipartUpload"]
        Resource = "${var.s3_bucket_arn}/*"
      },
      # CloudFront cache invalidation after frontend deploy
      {
        Effect   = "Allow"
        Action   = "cloudfront:CreateInvalidation"
        Resource = var.cloudfront_distribution_arn
      },
      # Allow passing ECS roles to the task — constrained to ecs-tasks.amazonaws.com
      {
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = [var.ecs_task_execution_role_arn, var.ecs_task_role_arn]
        Condition = {
          StringEquals = {
            "iam:PassedToService" = "ecs-tasks.amazonaws.com"
          }
        }
      }
    ]
  })
}

output "github_actions_role_arn" {
  description = "IAM role ARN assumed by GitHub Actions via OIDC"
  value       = aws_iam_role.github_actions.arn
}
