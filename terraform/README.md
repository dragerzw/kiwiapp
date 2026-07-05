# KiwiApp — Terraform Infrastructure

Provisions the full AWS stack for kiwiapp:

- **Networking** — VPC, public/private subnets, Internet Gateway, route tables
- **NAT** — fck-nat t4g.nano (~$3/mo) for private subnet outbound traffic
- **Compute** — ECS Fargate (Flask/Gunicorn), ALB, ECR, CloudWatch Logs
- **Database** — RDS MySQL 8.0 (private subnet, SSL enforced)
- **Frontend** — S3 + CloudFront with OAC for React SPA
- **DNS** — ACM certificate + Route 53 alias records for `kiwiapp.thedrageradvantage.com` / `api.kiwiapp.thedrageradvantage.com`
- **IAM-OIDC** — GitHub Actions deploy role (keyless auth, no long-lived credentials)

---

## Prerequisites

| Tool | Version |
| :--- | :--- |
| Terraform | ≥ 1.5.0 |
| AWS CLI | ≥ 2.x |
| Valid AWS credentials | `aws sso login` or `aws configure` |

---

## Step 1 — Bootstrap (run once per AWS account)

Creates the S3 state bucket and DynamoDB lock table.

```bash
cd terraform/bootstrap
terraform init
terraform apply -var="project_name=kiwiapp"

# Note the outputs — you'll need them in Step 2
# state_bucket_name = "kiwiapp-terraform-state-<ACCOUNT_ID>"
# dynamodb_table_name = "kiwiapp-terraform-locks"
```

---

## Step 2 — Provision Production Infrastructure

### 2a. Create a backend config file (never committed)

Create `terraform/environments/production/backend.conf`:

```hcl
bucket         = "kiwiapp-terraform-state-<YOUR_ACCOUNT_ID>"
key            = "production/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "kiwiapp-terraform-locks"
encrypt        = true
```

### 2b. Create a tfvars file (never committed)

Create `terraform/environments/production/production.tfvars`:

```hcl
db_password = "<STRONG_RANDOM_PASSWORD_MIN_8_CHARS>"
```

> **Tip:** Generate with `openssl rand -base64 24`

### 2c. Init + Plan + Apply

```bash
cd terraform/environments/production

terraform init -backend-config=backend.conf

terraform plan -var-file=production.tfvars

terraform apply -var-file=production.tfvars
```

The apply takes ~15 minutes (mostly RDS and CloudFront).

### 2d. Capture outputs

```bash
terraform output -json
```

Copy each output value into the matching GitHub Secret for the `production` environment.

---

## Step 3 — Populate SSM Parameter Store

After RDS is created, store the actual secret values in SSM:

```bash
REGION="us-east-1"

# Build the DATABASE_URL from the RDS address in the Terraform output
# terraform output -raw rds_connection_url_template  → substitute the password
aws ssm put-parameter \
  --region "$REGION" \
  --name "/kiwiapp/production/DATABASE_URL" \
  --type "SecureString" \
  --value "mysql+pymysql://kiwi_admin:<YOUR_DB_PASSWORD>@<RDS_ENDPOINT>:3306/kiwiappproduction"

aws ssm put-parameter \
  --region "$REGION" \
  --name "/kiwiapp/production/ALPHA_VANTAGE_API_KEY" \
  --type "SecureString" \
  --value "<YOUR_KEY>"

aws ssm put-parameter \
  --region "$REGION" \
  --name "/kiwiapp/production/COGNITO_USER_POOL_ID" \
  --type "SecureString" \
  --value "<YOUR_USER_POOL_ID>"

aws ssm put-parameter \
  --region "$REGION" \
  --name "/kiwiapp/production/COGNITO_APP_CLIENT_ID" \
  --type "SecureString" \
  --value "<YOUR_CLIENT_ID>"
```

---

## Step 4 — Configure GitHub Secrets

In the `production` environment on GitHub (`Settings → Environments → production → Secrets`):

| Secret | Source |
| :--- | :--- |
| `AWS_ROLE_ARN` | `terraform output github_actions_role_arn` |
| `AWS_REGION` | `us-east-1` |
| `ECS_CLUSTER_NAME` | `terraform output ecs_cluster_name` |
| `ECS_SERVICE_NAME` | `terraform output ecs_service_name` |
| `ECS_TASK_DEFINITION` | `terraform output ecs_task_family` |
| `ECR_REPOSITORY_URL` | `terraform output ecr_repository_url` |
| `S3_BUCKET_NAME` | `terraform output s3_bucket_name` |
| `CLOUDFRONT_DISTRIBUTION_ID` | `terraform output cloudfront_distribution_id` |
| `SERVICE_URL` | `https://api.kiwiapp.thedrageradvantage.com` |
| `DATABASE_URL_VALUEFROM` | `/kiwiapp/production/DATABASE_URL` |
| `ALPHA_VANTAGE_API_KEY_VALUEFROM` | `/kiwiapp/production/ALPHA_VANTAGE_API_KEY` |
| `COGNITO_USER_POOL_ID_VALUEFROM` | `/kiwiapp/production/COGNITO_USER_POOL_ID` |
| `COGNITO_APP_CLIENT_ID_VALUEFROM` | `/kiwiapp/production/COGNITO_APP_CLIENT_ID` |
| `VITE_API_BASE_URL` | `https://api.kiwiapp.thedrageradvantage.com` |
| `VITE_COGNITO_AUTHORITY` | `https://cognito-idp.us-east-1.amazonaws.com/<POOL_ID>` |
| `VITE_COGNITO_CLIENT_ID` | `<YOUR_CLIENT_ID>` |
| `VITE_COGNITO_REDIRECT_URI` | `https://kiwiapp.thedrageradvantage.com/` |
| `VITE_COGNITO_POST_LOGOUT_REDIRECT_URI` | `https://kiwiapp.thedrageradvantage.com/signed-out` |
| `VITE_COGNITO_DOMAIN` | `https://<YOUR_COGNITO_DOMAIN>.auth.us-east-1.amazoncognito.com` |

---

## Step 5 — Update Cognito App Client

In the AWS Cognito console, add the new URLs to your App Client:

- **Allowed callback URLs:** `https://kiwiapp.thedrageradvantage.com/`
- **Allowed sign-out URLs:** `https://kiwiapp.thedrageradvantage.com/signed-out`

---

## Step 6 — First Schema Migration

On the very first deploy, set `AUTO_CREATE_SCHEMA=true` by temporarily editing the `environment-variables` block in `ecs-deploy.yml`, or run the schema migration manually via an ECS task override:

```bash
aws ecs run-task \
  --cluster kiwi-production-cluster \
  --task-definition kiwi-production-api \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<PRIVATE_SUBNET_ID>],securityGroups=[<ECS_SG_ID>],assignPublicIp=DISABLED}" \
  --overrides '{"containerOverrides":[{"name":"kiwi-api","environment":[{"name":"AUTO_CREATE_SCHEMA","value":"true"}]}]}'
```

Then set `AUTO_CREATE_SCHEMA=false` before the next regular deploy.

---

## Module Graph

```
networking
    │
    ├── nat-instance (depends_on networking)
    │
    ├── dns (reads cloudfront + alb outputs — Terraform resolves ordering)
    │
    ├── compute (uses dns cert ARN for ALB HTTPS, depends_on nat)
    │
    ├── database (uses ECS SG ID from compute)
    │
    ├── frontend (uses dns cert ARN for CloudFront)
    │
    └── iam-oidc (uses outputs from compute + frontend)
```

---

## Cost Estimate (us-east-1, production)

| Resource | Cost |
| :--- | :--- |
| ECS Fargate (0.25 vCPU, 0.5 GB, SPOT mix) | ~$5–10/mo |
| RDS MySQL t4g.micro, 20 GB gp3 | ~$15/mo |
| NAT Instance t4g.nano | ~$3/mo |
| ALB | ~$16/mo |
| CloudFront (first 1 TB free tier) | ~$0–3/mo |
| S3 (< 1 GB) | ~$0.02/mo |
| **Total estimated** | **~$40–50/mo** |

> Compare to: AWS Managed NAT Gateway alone costs $32/mo — the fck-nat swap saves ~$29/mo.
