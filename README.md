# KiwiApp

KiwiApp is a full-stack portfolio management application built with a Flask API and a Vite + React frontend. 

It is designed with a heavy emphasis on modern **DevOps, Security, and Cloud-Native** practices, running fully automated CI/CD pipelines to deploy containerized services into AWS via Infrastructure as Code (Terraform).

---

## 🏗️ Architecture & Infrastructure

KiwiApp is deployed entirely on AWS using **Terraform**. The infrastructure is designed for low maintenance, high security, and cost efficiency.

- **Frontend:** A React SPA built with Vite, hosted securely on **Amazon S3** and distributed globally via **CloudFront** CDN.
- **Backend:** A containerized Python Flask API running on serverless **AWS ECS Fargate**, situated behind an **Application Load Balancer (ALB)**.
- **Database:** **Amazon RDS (MySQL 8.0)**, isolated in private subnets, accessible only by the ECS tasks.
- **Authentication:** **Amazon Cognito** handles all user identity, authentication, and OIDC flows (JWT validation).
- **Edge Security:** **Arcjet** is integrated directly into the Flask API middleware to provide Application Layer protection (Bot Detection, Rate Limiting, and WAF rules like SQLi/XSS prevention).

---

## 🚀 DevOps & CI/CD Workflow

The project utilizes **GitHub Actions** for an end-to-end automated Continuous Integration and Continuous Deployment (CI/CD) pipeline. It uses **OIDC (OpenID Connect)** to authenticate with AWS securely, meaning there are *no long-lived AWS credentials* stored in GitHub.

### 1. Continuous Integration (`ci.yml`)
Every push or pull request triggers an aggressive validation pipeline:
- **Linting & Formatting:** Python (`ruff`) and React/TypeScript (`eslint`).
- **Secret Scanning:** `TruffleHog` actively blocks commits that contain leaked secrets.
- **SAST (Static Application Security Testing):** `Bandit` scans the Python code for known security flaws.
- **Container Security:** 
  - `Hadolint` enforces Dockerfile best practices (e.g. multi-stage builds, non-root users).
  - `Trivy` scans the built Docker image for vulnerable OS and library packages.
- **IaC Security:** `Checkov` scans the Terraform configurations to ensure AWS resources are provisioned securely.
- **Unit Testing:** `pytest` validates backend logic and API routes.
- **Smoke Testing:** An automated job spins up the Docker container locally and pings the health endpoint to guarantee the application boots successfully before ever touching a live environment.

### 2. Continuous Deployment (`deploy.yml`)
Deployments to production are completely separated and executed on demand (via `workflow_dispatch`):
1. Builds the final multi-stage Docker image and pushes it to **Amazon ECR**.
2. Dynamically pulls secrets from **AWS SSM Parameter Store** and injects them into a new ECS Task Definition.
3. Performs a rolling deployment to the ECS Fargate cluster.
4. Builds the production React SPA and synchronizes the assets to the **S3 bucket**, followed by a CloudFront cache invalidation.

---

## 💻 Developer Setup

### Project Structure
- `app/`: Flask application, models, routes, auth, and services
- `frontend/`: Vite + React client
- `terraform/`: Complete AWS infrastructure definitions
- `tests/`: Backend pytest suite
- `.github/workflows/`: CI/CD pipelines

### Local Backend Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:
```powershell
python -m pip install -r requirements.txt
```
3. Create a root `.env` file from `.env.example` and fill in your values (e.g., `ARCJET_KEY`, `ALPHA_VANTAGE_API_KEY`).
4. Start the API (Defaults to `http://localhost:5000`):
```powershell
python run.py
```

### Local Frontend Setup

1. Change into the frontend directory:
```powershell
Set-Location frontend
```
2. Install dependencies:
```powershell
npm install
```
3. Create `frontend/.env` from `frontend/.env.example`. You will need your Cognito configuration details here.
4. Start the Vite dev server (Defaults to `http://localhost:5173`):
```powershell
npm run dev
```

### Running Tests

**Backend Unit Tests:**
```powershell
python -m pytest
```

**Frontend Lint & Build Verification:**
```powershell
Set-Location frontend
npm run lint
npm run build
```
