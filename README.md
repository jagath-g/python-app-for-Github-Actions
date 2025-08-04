# Secure Python Web App CI/CD with Multi-Architecture Docker & Cloud Integration

<img src="https://github.com/bhuvan-raj/python-app-for-Github-Actions/blob/main//cicd.png" alt="Banner" />

## Project Overview

Welcome to the Secure Python Web App CI/CD Project\! This repository provides you with a basic Python Flask web application and challenges you to build a robust, industry-level Continuous Integration/Continuous Delivery (CI/CD) pipeline using GitHub Actions.

This pipeline incorporates essential DevSecOps practices, including multi-architecture Docker image builds, automated security scanning, secure secrets management with AWS Secrets Manager, and comprehensive notifications.

## Project Objectives

By completing this project, you will learn to:

  * **Design Multi-Stage Dockerfiles:** Create efficient and secure Docker images for Python applications.
  * **Implement Multi-Architecture Builds:** Build Docker images compatible with different CPU architectures (e.g., AMD64, ARM64).
  * **Integrate Automated Testing:** Run unit tests as part of your CI pipeline and generate comprehensive test reports.
  * **Perform Container Security Scanning:** Use Trivy to identify vulnerabilities in your Docker images and integrate findings into GitHub Security.
  * **Manage Secrets Securely:** Leverage AWS Secrets Manager and GitHub OIDC for robust credential management, eliminating hardcoded secrets.
  * **Orchestrate CI/CD with GitHub Actions:** Build a multi-stage pipeline with conditional job execution and environment management.
  * **Automate Deployments:** Understand and simulate deployments to staging and production environments, including manual approval gates.
  * **Implement Comprehensive Notifications:** Get real-time feedback on your pipeline status via AWS SES emails and (optionally) Slack.
  * **Understand DevSecOps Principles:** Apply "shift-left" security, automation, and continuous feedback loops throughout the SDLC.

## Provided Files

This repository contains the following core application files:

  * `app.py`: A simple Flask web application with basic routes.
  * `test_app.py`: Unit tests for `app.py` using `pytest`.
  * `requirements.txt`: Defines the production dependencies for `app.py`.
  * `requirements-dev.txt`: Defines development and testing dependencies (including `pytest`).

**Your primary task is to create the `Dockerfile` and the GitHub Actions workflow (`.github/workflows/main.yml`) that utilizes these files.**

## Pipeline Stages Overview

Your completed CI/CD pipeline will consist of the following jobs, executed sequentially or in parallel based on dependencies:

1.  **`code-quality`**:
      * Lints and formats Python code (`flake8`, `black`, `isort`).
      * Scans for hardcoded secrets (`trufflesecurity/trufflehog`).
2.  **`build-and-scan-images`**:
      * Builds multi-architecture Docker images for the Python app.
      * Pushes individual architecture images to Docker Hub and AWS ECR.
      * Scans these images for vulnerabilities using Trivy, failing the pipeline on critical issues.
3.  **`run-unit-tests-and-report`**:
      * Runs `pytest` unit tests on the application.
      * Generates a JUnit XML test report.
      * Uploads the test report as a GitHub Actions Artifact.
4.  **`create-multi-arch-manifests`**:
      * Creates and pushes multi-architecture manifest lists (`latest`, `SHA`) to Docker Hub and AWS ECR.
5.  **`deploy-to-staging`**:
      * Simulates deployment to a `staging` environment.
      * Runs simulated integration tests against the staging environment.
6.  **`deploy-to-production`**:
      * Requires **manual approval** to deploy to the `production` environment.
      * Simulates deployment to production.
      * Performs a post-deployment health check.

**Notifications:** Each major job will send an email notification via AWS SES on its completion status. Slack notifications are optional but highly encouraged for a more "industry-like" feel.

## Setup Guide

Before you can run the CI/CD pipeline, you need to configure your AWS account and GitHub repository.

### 1\. AWS Account Setup

Ensure you have an AWS account with necessary permissions.

#### 1.1. IAM Role for GitHub Actions (OIDC)

This is the **most secure way** to grant GitHub Actions access to your AWS resources. You'll create an IAM role that GitHub Actions can "assume" using OpenID Connect (OIDC), without needing long-lived AWS credentials stored directly in GitHub.

1.  **Create an IAM OIDC Provider:**
      * In the IAM console, navigate to **Identity Providers** -\> **Add provider**.
      * Select **OpenID Connect**.
      * **Provider URL:** `https://token.actions.githubusercontent.com`
      * **Audience:** `sts.amazonaws.com`
      * Click "Add provider".
2.  **Create an IAM Role (`github-actions-oidc-role`)**:
      * In the IAM console, navigate to **Roles** -\> **Create role**.

      * Choose **Custom trust policy**.

      * Paste the following JSON, replacing `YOUR_AWS_ACCOUNT_ID`, `YOUR_GITHUB_USERNAME`, and `YOUR_REPO_NAME`:

        ```json
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Federated": "arn:aws:iam::YOUR_AWS_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
              },
              "Action": "sts:AssumeRoleWithWebIdentity",
              "Condition": {
                "StringEquals": {
                  "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                  "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/YOUR_REPO_NAME:*"
                }
              }
            }
          ]
        }
        ```

      * Click "Next".

      * **Attach Permissions Policies:** You'll need to create and attach policies for the services your pipeline interacts with.

          * **Secrets Manager Policy:**
            ```json
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "secretsmanager:GetSecretValue",
                        "Resource": "arn:aws:secretsmanager:YOUR_AWS_REGION:YOUR_AWS_ACCOUNT_ID:secret:YOUR_AWS_SECRETS_MANAGER_SECRET_NAME-*"
                    }
                ]
            }
            ```
          * **SES Policy:**
            ```json
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "ses:SendEmail",
                            "ses:SendRawEmail"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            ```
          * **ECR Policy:**
            ```json
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "ecr:GetDownloadUrlForLayer",
                            "ecr:BatchGetImage",
                            "ecr:BatchCheckLayerAvailability",
                            "ecr:PutImage",
                            "ecr:InitiateLayerUpload",
                            "ecr:UploadLayerPart",
                            "ecr:CompleteLayerUpload",
                            "ecr:GetAuthorizationToken"
                        ],
                        "Resource": "arn:aws:ecr:YOUR_AWS_REGION:YOUR_AWS_ACCOUNT_ID:repository/YOUR_ECR_REPO_NAME"
                    }
                ]
            }
            ```
            (You might need to adjust `Resource` to `*` for simplicity in some cases, but specify repository is best practice).

      * Name your role (e.g., `github-actions-oidc-role`) and create it. **Copy its ARN.**

#### 1.2. AWS Secrets Manager Setup

1.  **Create a Secret:**
      * In the Secrets Manager console, click **Store a new secret**.
      * Choose **Other type of secret**.
      * Enter your Docker Hub username and Personal Access Token (PAT) as key-value pairs.
      * Example (raw JSON):
        ```json
        {
          "DOCKERHUB_USERNAME": "your-dockerhub-username",
          "DOCKERHUB_TOKEN": "your-dockerhub-pat"
        }
        ```
      * Name your secret (e.g., `docker-credentials`). **Copy this secret name.**
      * **Note:** For ECR, you usually get a temporary token (`aws ecr get-login-password`). Your workflow will dynamically generate this, so you don't store ECR password here, just ensure your IAM role has `ecr:GetAuthorizationToken` permission.

#### 1.3. AWS ECR Repository

1.  **Create a Repository:**
      * In the ECR console, navigate to **Repositories** -\> **Create repository**.
      * Set the **Visibility settings** to `Private`.
      * Give it a name (e.g., `my-python-app`).

#### 1.4. AWS SES (Simple Email Service) Setup

1.  **Verify Sender Email Addresses:**
      * In the SES console, navigate to **Verified identities** -\> **Create identity**.
      * Choose `Email address` and enter the email address you will use as the sender (`SES_SENDER_EMAIL`).
      * Follow the instructions to verify the email (click the link in the verification email).
      * **Crucial:** Ensure the region for SES matches your `AWS_REGION`. If you are in a non-default SES region, you might need to request production access to send emails to unverified recipients.

### 2\. GitHub Repository Setup

Go to your GitHub repository -\> **Settings** -\> **Secrets and variables** -\> **Actions**.

#### 2.1. Repository Secrets

Add the following repository secrets:

  * `AWS_REGION`: Your AWS region (e.g., `ap-south-1`).
  * `AWS_ROLE_ARN`: The ARN of the IAM role you created (e.g., `arn:aws:iam::123456789012:role/github-actions-oidc-role`).
  * `AWS_PROD_ROLE_ARN`: (Optional, but recommended for production) ARN of a separate, more restricted IAM role for production deployments. If not using, use `AWS_ROLE_ARN`.
  * `AWS_SECRETS_MANAGER_SECRET_NAME`: The name of the secret you created in Secrets Manager (e.g., `docker-credentials`).
  * `SES_SENDER_EMAIL`: The verified email address in SES that will send notifications.
  * `SES_RECIPIENT_EMAIL`: The email address(es) that will receive notifications (comma-separated for multiple).
  * `SLACK_WEBHOOK_URL`: (Optional) Your Slack incoming webhook URL for notifications.

#### 2.2. GitHub Environments

Configure environments to formalize your deployment stages and add approval gates.

1.  Navigate to **Settings** -\> **Environments**.
2.  Click **New environment**.
3.  **Create `staging` environment:**
      * Name: `staging`
      * (Optional) Add environment variables or secrets specific to staging.
      * (Optional) Add a deployment protection rule for "Wait timer" (e.g., 5 seconds).
4.  **Create `production` environment:**
      * Name: `production`
      * **Add "Required reviewers":** Select yourself or a team that must approve deployments to production. This is a critical security gate.
      * (Optional) Add "Wait timer" or other deployment protection rules.

## Your Development Tasks

1.  **Create `Dockerfile`:**
      * Based on the provided Python files, create your multi-stage `Dockerfile`.
      * Ensure it correctly installs dependencies, and runs `pytest --junitxml=test-results.xml` in the builder stage.
      * Make sure the `production` stage is lean.
2.  **Create GitHub Actions Workflow (`.github/workflows/main.yml`):**
      * Implement all the jobs outlined in the "Pipeline Stages Overview" section above.
      * Pay close attention to job dependencies (`needs:`).
      * Implement the AWS OIDC authentication to retrieve secrets from Secrets Manager.
      * Integrate Docker Hub and ECR login/push.
      * Configure Trivy scanning with SARIF output and failure conditions.
      * Set up the `run-unit-tests-and-report` job to execute `pytest` and upload `test-results.xml` as an artifact.
      * Integrate AWS SES notifications for each job using `if` conditions.
      * Define and use the `staging` and `production` environments correctly.

## How to Run the Pipeline

1.  **Commit your code:** Place your `Dockerfile` and the provided Python files (`app.py`, `test_app.py`, `requirements.txt`, `requirements-dev.txt`) in the root of your repository.
2.  **Push to `main`:** Push your changes to the `main` branch. This will automatically trigger the CI/CD pipeline.
3.  **Create a Pull Request:** Create a Pull Request against the `main` branch to see the `code-quality` job run on the PR.
4.  **Manual Trigger:** You can also manually trigger the `main` workflow from the "Actions" tab in GitHub (select your workflow -\> "Run workflow" -\> choose `main` branch).

## How to Verify Each Component

After your pipeline runs, check the following:

  * **GitHub Actions UI:**
      * Go to the "Actions" tab in your repository.
      * Click on your latest workflow run.
      * Observe each job succeeding or failing.
      * **Test Results:** Look for "Artifacts" in the workflow summary. You should be able to download `pytest-results.xml`.
  * **GitHub Security Tab:**
      * Navigate to your repository's "Security" tab -\> "Code scanning alerts".
      * You should see alerts generated by Trivy (if any vulnerabilities were found).
  * **Docker Hub:**
      * Log in to your Docker Hub account.
      * Navigate to your repository (`your-username/my-python-app`).
      * Verify that both architecture-specific images (e.g., `my-python-app:<SHA>-linux-amd64`) and the multi-architecture manifest list (`my-python-app:latest`, `my-python-app:<SHA>`) are present.
  * **AWS ECR:**
      * In the ECR console, navigate to your repository (`my-python-app`).
      * Verify that both architecture-specific images and the multi-architecture manifest list are present.
  * **Email Inbox:**
      * Check the recipient email address(es) configured in `SES_RECIPIENT_EMAIL`. You should receive email notifications for each job's status.
  * **Slack Channel (if configured):**
      * Check your Slack channel for deployment notifications.
  * **Production Deployment Approval:**
      * When the pipeline reaches the `deploy-to-production` job, it will pause.
      * Go to the workflow run in GitHub Actions, click on the `deploy-to-production` job, and you will see a "Review deployments" banner. Approve it to continue.

## Key Learning Points & Challenges

  * **Secure Credential Handling:** The primary challenge is not hardcoding secrets. You'll master using AWS Secrets Manager with GitHub OIDC for dynamic, secure access.
  * **Docker Multi-Architecture Builds:** Understanding `docker buildx` and `matrix` strategies is key for deploying portable applications.
  * **Integrating Security Early (Shift-Left):** Observe how Trivy failing the pipeline on critical vulnerabilities prevents insecure images from progressing.
  * **Test Reporting:** Getting test results *out* of your Docker build context and into GitHub Actions artifacts is a common practical problem to solve.
  * **Granular Notifications:** Setting up per-job notifications provides immediate feedback on pipeline health.
  * **GitHub Environments:** Learn how to enforce policies like manual approvals for sensitive environments.

## Troubleshooting Tips

  * **"Permission Denied" (AWS):** Double-check your AWS IAM role's Trust Policy (OIDC configuration) and Permissions Policy. Ensure the `Resource` ARNs in your policies are correct.
  * **"Secret Not Found" (Secrets Manager):** Verify the `AWS_SECRETS_MANAGER_SECRET_NAME` secret in GitHub is exactly the name of your secret in AWS Secrets Manager.
  * **Docker Login Issues:** Ensure `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets are correct, and for ECR, ensure your IAM role has `ecr:GetAuthorizationToken` and the `docker/login-action` for ECR is correctly configured.
  * **Trivy Failures:** If Trivy fails the build, examine its output in the logs to understand which vulnerabilities were found. You might need to update dependencies in `requirements.txt`.
  * **Test Results Not Appearing:** Ensure `pytest --junitxml=test-results.xml` actually generates the file at the expected location, and that `actions/upload-artifact` is pointing to the correct path on the runner.
  * **SES Emails Not Arriving:** Check your SES verified identities, ensure the sender is verified, and that you haven't hit any sending limits (especially if you're in the SES sandbox). Also, check your spam folder\!
  * **GitHub Actions Cache:** If builds seem slow, ensure your `cache-from` and `cache-to` for `docker/build-push-action` are configured correctly.
