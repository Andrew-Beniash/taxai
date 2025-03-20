# API Testing and Deployment Guide

This document explains how to deploy and test the Tax AI API using both local and Kubernetes environments, and how to conduct load testing to ensure the system can handle concurrent requests efficiently.

## Prerequisites

Before getting started, make sure you have the following tools installed:

- **Docker**: For containerizing the application
- **curl**: For testing API endpoints
- **kubectl**: For Kubernetes deployment (only needed for Kubernetes deployment)
- **locust**: For load testing (`pip install locust`)

## Deployment Options

The system can be deployed in two ways:

1. **Local Deployment**: Using Docker Compose for a local development environment
2. **Kubernetes Deployment**: For production-like environments with auto-scaling capabilities

## Quick Start

### 1. Deploy and Test API (Local)

To deploy the API locally and run tests:

```bash
# Make the script executable
chmod +x api_deployment_and_testing.sh

# Run local deployment with API tests
./api_deployment_and_testing.sh "http://localhost:8000" "local" "false" "false"
```

### 2. Deploy to Kubernetes and Test

To deploy to Kubernetes and run tests:

```bash
# Make the script executable
chmod +x api_deployment_and_testing.sh

# Deploy to Kubernetes and run API tests
./api_deployment_and_testing.sh "http://localhost:8000" "kubernetes" "false" "false"

# If needed, set up port forwarding to access the API
kubectl port-forward svc/taxai-api 8000:8000
```

### 3. Run Load Tests

To run load tests against a deployed API:

```bash
# Deploy and run load tests
./api_deployment_and_testing.sh "http://localhost:8000" "local" "false" "true"
```

## Script Parameters

The `api_deployment_and_testing.sh` script accepts the following parameters:

1. **API_URL** (default: "http://localhost:8000"): The URL where the API is accessible
2. **DEPLOYMENT_TYPE** (default: "local"): The deployment type, either "local" or "kubernetes"
3. **SKIP_TESTS** (default: "false"): Whether to skip the API tests
4. **RUN_LOAD_TEST** (default: "false"): Whether to run load tests with Locust

## Manual Testing

### Testing with curl

You can manually test the API using curl commands:

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Query the AI
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the tax deductions for a small business?"}'
```

### Advanced Load Testing

For more detailed load testing, you can use Locust's web interface:

```bash
locust -f load_test.py --host=http://localhost:8000
```

Then open http://localhost:8089 in your browser to configure and start the test.

## Kubernetes Configuration

The Kubernetes deployment includes:

- **Horizontal Pod Autoscaler (HPA)**: Automatically scales the API pods based on CPU utilization
- **Resource Limits**: Ensures pods have appropriate resources allocated
- **Health Probes**: Monitors the API health and restarts pods if necessary
- **Persistent Storage**: For databases and vector stores

To view the status of the Kubernetes deployment:

```bash
kubectl get pods -n taxai
kubectl get deployments -n taxai
kubectl get hpa -n taxai
```

## Postman Testing

For more user-friendly testing, we've provided a Postman collection:

1. Run the script to save the Postman collection:
   ```bash
   chmod +x save-postman-collection.sh
   ./save-postman-collection.sh
   ```

2. Import the collection into Postman:
   - Open Postman
   - Click "Import" button in the top-left corner
   - Select "File" and choose `tests/postman/taxai-postman-collection.json`

3. Set up an environment in Postman:
   - Click "Environments" in the sidebar
   - Create a new environment
   - Add a variable named `base_url` with value `http://localhost:8000`

4. Run the collection:
   - Open the "Tax AI API" collection
   - Click the "Run" button
   - Select the requests you want to run
   - Click "Run Tax AI API"

The collection includes tests for:
- Health checks
- Basic tax queries
- Context-based queries
- Complex tax scenarios
- Error handling (empty queries, non-tax queries)

## Troubleshooting

### Common Issues

1. **API not reachable**: 
   - Check if the API is running: `docker ps` or `kubectl get pods`
   - Verify port forwarding: `kubectl port-forward svc/taxai-api 8000:8000`

2. **Model loading timeout**:
   - The AI model may take time to load, especially on first startup
   - Increase the timeout value in the script if needed

3. **Kubernetes pods failing**:
   - Check pod logs: `kubectl logs -n taxai <pod-name>`
   - Describe the pod: `kubectl describe pod -n taxai <pod-name>`

4. **Docker image issues**:
   - Ensure Docker daemon is running
   - Check Docker image build logs
   - Verify Dockerfile has correct dependencies

## Performance Tuning

To optimize performance based on load testing results:

1. Adjust the HPA settings in `kubernetes/api-hpa.yaml`
2. Modify resource requests and limits in `kubernetes/api-deployment.yaml`
3. Increase the number of replicas for higher traffic scenarios
4. Optimize the model configuration in `config.py`

## Best Practices

1. Always run tests before deploying to production
2. Use load testing to determine appropriate scaling parameters
3. Monitor API performance over time to detect degradation
4. Implement CI/CD pipelines to automate testing and deployment
5. Regularly update dependencies and security patches

## Next Steps

After completing the basic testing and deployment:

1. Integrate these tests into your CI/CD pipeline
2. Set up monitoring and alerting for production deployments
3. Implement more comprehensive test coverage
4. Consider A/B testing for different model configurations

For more information on specific topics, see:
- `docs/LOAD_TESTING_GUIDE.md` for detailed load testing instructions
- `docs/POSTMAN_GUIDE.md` for advanced Postman usage
