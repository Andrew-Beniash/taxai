# CI/CD Pipeline Guide

This document explains how to use the Continuous Integration and Continuous Deployment (CI/CD) pipeline set up with GitHub Actions in this project.

## Overview

The CI/CD pipeline automates the following processes:

1. **Code Validation**: Runs linting checks using flake8 to ensure code quality
2. **Testing**: Executes unit tests using pytest with coverage reporting
3. **Docker Image Building**: Creates and pushes Docker images for deployment
4. **Deployment**: Prepares the application for deployment (configured separately for production)

## Pipeline Workflow

The pipeline is triggered on:
- **Push** to `main` or `development` branches
- **Pull requests** targeting the `main` or `development` branches

### Stages

#### 1. Lint and Test
This stage runs on every push and pull request:
- It checks Python code syntax and style using flake8
- Runs all tests with pytest and generates coverage reports
- Uploads coverage reports to Codecov for tracking

#### 2. Build Docker
This stage only runs on pushes to main and development branches:
- Builds a Docker image based on the Dockerfile
- Pushes the image to Docker Hub with appropriate tags:
  - `latest` for the most recent build
  - A tag with the specific commit SHA for version tracking
- Uses caching to speed up future builds

#### 3. Deploy
This stage only runs on pushes to the main branch:
- Currently contains placeholder deployment commands
- Will be configured with actual deployment steps when ready for production

## Setting Up Docker Hub Secrets

For the Docker image publishing to work, you need to add the following secrets to your GitHub repository:

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add the following secrets:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: A Docker Hub access token (not your password)

To create a Docker Hub access token:
1. Log in to Docker Hub
2. Go to Account Settings → Security → New Access Token
3. Provide a description and set permissions
4. Copy the token and add it as a GitHub secret immediately (it won't be shown again)

## Local Testing

Before pushing to GitHub, you can run the same checks locally:

```bash
# Install development dependencies
pip install flake8 pytest pytest-cov

# Run linting checks
flake8 .

# Run tests with coverage
pytest --cov=. --cov-report=term
```

## Extending the Pipeline

To extend the CI/CD pipeline:

1. Edit the `.github/workflows/ci-cd.yml` file
2. Add new jobs or modify existing ones
3. Commit and push changes to the repository

For additional environment-specific deployments (staging, QA, etc.), you can create separate workflow files with different triggers and deployment targets.
