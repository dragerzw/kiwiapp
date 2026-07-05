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
variable "environment" {
  type        = string
  description = "Deployment environment (e.g., production)"
}
variable "vpc_id" {
  type        = string
  description = "VPC ID where compute resources are deployed"
}
variable "public_subnet_ids" {
  type        = list(string)
  description = "Public subnet IDs for the ALB"
}
variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs for ECS Fargate tasks"
}
variable "alb_certificate_arn" {
  type        = string
  default     = null
  description = "ACM certificate ARN for HTTPS on the ALB. Required for production."
}
variable "ecs_execution_ssm_parameter_path_prefixes" {
  type        = list(string)
  default     = []
  description = "SSM path prefixes expanded to wildcard ARNs the ECS execution role may read"
}
variable "ecs_execution_secret_arns" {
  type        = list(string)
  default     = []
  description = "Secrets Manager ARNs the ECS execution role may read"
}

# ─── DATA SOURCES ───
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

# ─── LOCALS ───
locals {
  container_name = "kiwi-api"
  app_port       = 5000

  has_alb_certificate = var.alb_certificate_arn != null && trimspace(var.alb_certificate_arn) != ""

  # Expand SSM path prefix wildcards to ARNs the execution role can read
  ecs_execution_ssm_path_arns = [
    for prefix in var.ecs_execution_ssm_parameter_path_prefixes :
    "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${trim(prefix, "/")}/*"
  ]

  ecs_execution_secret_policy_statements = concat(
    length(var.ecs_execution_secret_arns) > 0 ? [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = var.ecs_execution_secret_arns
      }
    ] : [],
    length(local.ecs_execution_ssm_path_arns) > 0 ? [
      {
        Effect   = "Allow"
        Action   = ["ssm:GetParameters", "ssm:GetParameter"]
        Resource = local.ecs_execution_ssm_path_arns
      }
    ] : []
  )

  # Cost mix: prefer Spot in non-prod, balanced in production
  fargate_on_demand_weight = var.environment == "production" ? 2 : 1
  fargate_spot_weight      = var.environment == "production" ? 1 : 3

  ecs_log_retention_days = var.environment == "production" ? 180 : 30
}

# ─── SECURITY GROUPS ───
resource "aws_security_group" "alb" {
  # checkov:skip=CKV_AWS_260: Port 80 required for HTTP→HTTPS redirect.
  name        = "kiwi-${var.environment}-alb-sg"
  description = "ALB public ingress"
  vpc_id      = var.vpc_id

  lifecycle {
    precondition {
      condition     = var.environment != "production" || local.has_alb_certificate
      error_message = "alb_certificate_arn must be set for production to enforce TLS."
    }
  }

  ingress {
    description = "HTTP inbound"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  dynamic "ingress" {
    for_each = local.has_alb_certificate ? [1] : []
    content {
      description = "HTTPS inbound"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  # Least-privilege egress: ALB only needs to reach ECS on the app port
  egress {
    description     = "Outbound to ECS tasks only"
    from_port       = local.app_port
    to_port         = local.app_port
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }
}

resource "aws_security_group" "ecs" {
  # checkov:skip=CKV_AWS_382: Full egress required for ECR pulls, DB connections, and external API (Alpha Vantage, Cognito).
  name        = "kiwi-${var.environment}-ecs-sg"
  description = "Fargate tasks security group"
  vpc_id      = var.vpc_id

  egress {
    description = "Allow all outbound for ECR pulls, DB connections, external APIs"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Separate resource to avoid circular dependency with ALB SG
resource "aws_security_group_rule" "ecs_ingress_alb" {
  type                     = "ingress"
  security_group_id        = aws_security_group.ecs.id
  description              = "Allow inbound from ALB only"
  from_port                = local.app_port
  to_port                  = local.app_port
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb.id
}

# ─── APPLICATION LOAD BALANCER ───
resource "aws_lb" "main" {
  # checkov:skip=CKV_AWS_91: Access logging not required for this tier.
  # checkov:skip=CKV2_AWS_20: HTTP redirect handled via dynamic block, checkov can't parse it.
  # checkov:skip=CKV2_AWS_28: WAF is cost prohibitive for this tier.
  name                       = "kiwi-${var.environment}-alb"
  internal                   = false
  load_balancer_type         = "application"
  security_groups            = [aws_security_group.alb.id]
  subnets                    = var.public_subnet_ids
  enable_deletion_protection = var.environment == "production"
  drop_invalid_header_fields = true
}

resource "aws_lb_target_group" "app" {
  # checkov:skip=CKV_AWS_378: HTTP behind ALB is intended; TLS terminates at the ALB.
  name        = "kiwi-${var.environment}-tg"
  port        = local.app_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  # / returns {"message": "Portfolio Management API is running"} → 200
  health_check {
    path                = "/"
    matcher             = "200"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    interval            = 30
    timeout             = 5
  }
}

resource "aws_lb_listener" "http" {
  # checkov:skip=CKV_AWS_2: HTTP listener used for redirect or non-TLS non-prod.
  # checkov:skip=CKV_AWS_103: HTTP listener does not use TLS.
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  # Forward directly in non-TLS environments; redirect to HTTPS when cert present
  dynamic "default_action" {
    for_each = local.has_alb_certificate ? [] : [1]
    content {
      type             = "forward"
      target_group_arn = aws_lb_target_group.app.arn
    }
  }

  dynamic "default_action" {
    for_each = local.has_alb_certificate ? [1] : []
    content {
      type = "redirect"
      redirect {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  }
}

resource "aws_lb_listener" "https" {
  count             = local.has_alb_certificate ? 1 : 0
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.alb_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# ─── ECR REPOSITORY ───
resource "aws_ecr_repository" "api" {
  # checkov:skip=CKV_AWS_51: Mutable tags required for CI/CD rolling deploys.
  # checkov:skip=CKV_AWS_136: AWS-managed encryption is sufficient.
  name                 = "kiwi-${var.environment}-api"
  image_tag_mutability = "MUTABLE"
  force_delete         = var.environment != "production"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "api" {
  repository = aws_ecr_repository.api.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images beyond the most recent 3"
        selection = {
          tagStatus   = "untagged"
          countType   = "imageCountMoreThan"
          countNumber = 3
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Keep at most 30 images total"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 30
        }
        action = { type = "expire" }
      }
    ]
  })
}

# ─── ECS CLUSTER ───
resource "aws_ecs_cluster" "main" {
  # checkov:skip=CKV_AWS_65: Container Insights cost extra; not required for this tier.
  name = "kiwi-${var.environment}-cluster"
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = local.fargate_on_demand_weight
    capacity_provider = "FARGATE"
  }

  default_capacity_provider_strategy {
    weight            = local.fargate_spot_weight
    capacity_provider = "FARGATE_SPOT"
  }
}

# ─── IAM ROLES ───
resource "aws_iam_role" "ecs_task_role" {
  name = "kiwi-${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "kiwi-${var.environment}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_task_execution_secrets" {
  count = length(local.ecs_execution_secret_policy_statements) > 0 ? 1 : 0
  name  = "kiwi-${var.environment}-ecs-execution-secrets"
  role  = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = local.ecs_execution_secret_policy_statements
  })
}

# ─── CLOUDWATCH LOG GROUP ───
resource "aws_cloudwatch_log_group" "ecs" {
  # checkov:skip=CKV_AWS_158: KMS encryption not strictly required.
  # checkov:skip=CKV_AWS_338: 1-year retention not required.
  name              = "/ecs/kiwi-${var.environment}-api"
  retention_in_days = local.ecs_log_retention_days
}

# ─── ECS TASK DEFINITION & SERVICE ───
resource "aws_ecs_task_definition" "app" {
  family                   = "kiwi-${var.environment}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  # Bootstrap HTTP server — replaced by the real Flask image on first CI/CD deploy.
  # Responds 200 on GET / so the ALB health check passes while waiting for first deploy.
  container_definitions = jsonencode([{
    name      = local.container_name
    image     = "public.ecr.aws/docker/library/node:20-alpine"
    command   = ["sh", "-c", "node -e \"require('http').createServer((req,res)=>res.end('bootstrap')).listen(${local.app_port},'0.0.0.0')\""]
    essential = true
    portMappings = [{
      containerPort = local.app_port
      hostPort      = local.app_port
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
        "awslogs-region"        = data.aws_region.current.name
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

resource "aws_ecs_service" "app" {
  name            = "kiwi-${var.environment}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1

  # Don't wait for stability — the bootstrap image may not pass health checks
  # until the first real deploy. GitHub Actions updates it immediately.
  wait_for_steady_state = false

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    base              = 1
    weight            = local.fargate_on_demand_weight
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = local.fargate_spot_weight
  }

  network_configuration {
    security_groups  = [aws_security_group.ecs.id]
    subnets          = var.private_subnet_ids
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = local.container_name
    container_port   = local.app_port
  }

  # GitHub Actions manages image updates and desired_count; ignore Terraform drift
  lifecycle {
    ignore_changes = [task_definition, desired_count]
  }
}

# ─── OUTPUTS ───
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Hosted zone ID of the ALB (for Route 53 alias records)"
  value       = aws_lb.main.zone_id
}

output "ecs_security_group_id" {
  description = "ECS Fargate tasks SG ID (passed to database module for MySQL ingress)"
  value       = aws_security_group.ecs.id
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.app.name
}

output "ecs_task_family" {
  description = "ECS task definition family (used by CI/CD to download the current definition)"
  value       = aws_ecs_task_definition.app.family
}

output "ecr_repository_url" {
  description = "ECR repository URL for Docker image pushes"
  value       = aws_ecr_repository.api.repository_url
}

output "ecr_repository_arn" {
  description = "ECR repository ARN (used by IAM-OIDC module)"
  value       = aws_ecr_repository.api.arn
}

output "ecs_service_arn" {
  description = "ECS service ARN (used by IAM-OIDC module)"
  value       = aws_ecs_service.app.id
}

output "ecs_task_execution_role_arn" {
  description = "ECS task execution role ARN"
  value       = aws_iam_role.ecs_task_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "ECS task role ARN"
  value       = aws_iam_role.ecs_task_role.arn
}
