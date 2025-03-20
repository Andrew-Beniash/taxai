# Tax AI Deployment Guide

This guide provides instructions for deploying and testing the AI-powered tax law application.

## Prerequisites

- Docker
- Kubernetes cluster (Minikube, K3s, or cloud provider)
- kubectl
- Python 3.10+

## Local Development Setup

### 1. Environment Setup

Make sure you have the necessary environment variables set in a `.env` file at the root of your project:

```bash
# API settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Model settings
USE_MISTRAL=true
USE_HUGGINGFACE_API=true
HUGGINGFACE_API_KEY=your_api_key_here

# Database settings
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taxai
```

### 2. Running Locally with Docker Compose

The easiest way to run the entire application stack locally is using Docker Compose:

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Shut down the services
docker-compose down
```

## Testing the API

### Basic API Testing

You can run a basic API test using the provided script:

```bash
# Make the test script executable
chmod +x make_test_api_executable.sh
./make_test_api_executable.sh

# Run the test
./test_api.sh
```

### Comprehensive API Testing

For more thorough testing, use the Python-based test script:

```bash
python test_api_integration.py --url http://localhost:8000
```

### Load Testing

To test the API under load, use the Locust-based load test:

```bash
# Install locust
pip install locust

# Run the load test
locust -f load_test.py --host http://localhost:8000

# Access the Locust web UI at http://localhost:8089
```

## Kubernetes Deployment

### 1. Prepare for Kubernetes Deployment

Before deploying to Kubernetes, make sure to update the secret in `kubernetes/secret.yaml` with your actual Hugging Face API key.

### 2. Deploy with the Script

We provide a deployment script that handles building the Docker image and deploying to Kubernetes:

```bash
# Make the deployment script executable
chmod +x make_deploy_kubernetes_executable.sh
./make_deploy_kubernetes_executable.sh

# Build the Docker image
./deploy_kubernetes.sh build

# Deploy to Kubernetes
./deploy_kubernetes.sh deploy

# Check deployment status
./deploy_kubernetes.sh status

# Do everything (build, deploy, check status)
./deploy_kubernetes.sh all

# Clean up the deployment
./deploy_kubernetes.sh cleanup
```

### 3. Accessing the API

After deployment, you can access the API through the Kubernetes Ingress:

```bash
# If using Minikube, you need to enable the ingress addon
minikube addons enable ingress

# Get the ingress address
kubectl get ingress

# Add an entry to your hosts file
echo "$(minikube ip) taxai.local" | sudo tee -a /etc/hosts

# Access the API at http://taxai.local
```

## Scaling and Monitoring

The deployment includes a Horizontal Pod Autoscaler (HPA) that will automatically scale the API pods based on CPU usage. You can monitor this with:

```bash
kubectl get hpa
```

## Troubleshooting

If you encounter issues with the deployment:

1. Check the pod logs:
   ```bash
   kubectl logs -l app=taxai,component=api
   ```

2. Check the pod status:
   ```bash
   kubectl describe pod -l app=taxai,component=api
   ```

3. Ensure all services are running:
   ```bash
   kubectl get pods,services,deployments
   ```

4. Verify that the ingress is correctly configured:
   ```bash
   kubectl describe ingress taxai-ingress
   ```
