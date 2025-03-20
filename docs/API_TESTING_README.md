# Tax AI API Testing and Deployment

This package provides comprehensive tools for testing and deploying the Tax AI API, allowing you to validate API endpoints, deploy to Docker and Kubernetes, and conduct load testing.

## Files Included

- **`api_deployment_and_testing.sh`**: Main script for testing and deployment
- **`save-postman-collection.sh`**: Helper script that saves a Postman collection for API testing
- **`make_api_testing_scripts_executable.sh`**: Makes all scripts executable
- **Postman Collection**: Pre-configured Postman collection for API testing

## Documentation

- **`docs/API_TESTING_GUIDE.md`**: General guide for API testing and deployment
- **`docs/LOAD_TESTING_GUIDE.md`**: Detailed guide for load testing with Locust
- **`docs/POSTMAN_GUIDE.md`**: Guide for using Postman to test the API

## Getting Started

1. Make the scripts executable:
   ```bash
   ./make_api_testing_scripts_executable.sh
   ```

2. Test the API with curl:
   ```bash
   ./api_deployment_and_testing.sh "http://localhost:8000" "local" "false" "false"
   ```

3. Create the Postman collection:
   ```bash
   ./save-postman-collection.sh
   ```

4. Run load tests:
   ```bash
   ./api_deployment_and_testing.sh "http://localhost:8000" "local" "false" "true"
   ```

5. Deploy to Kubernetes:
   ```bash
   ./api_deployment_and_testing.sh "http://localhost:8000" "kubernetes" "false" "false"
   ```

## Script Options

The `api_deployment_and_testing.sh` script accepts the following parameters:

```bash
./api_deployment_and_testing.sh [API_URL] [DEPLOYMENT_TYPE] [SKIP_TESTS] [RUN_LOAD_TEST]
```

- **API_URL**: URL of the API (default: http://localhost:8000)
- **DEPLOYMENT_TYPE**: "local" or "kubernetes" (default: local)
- **SKIP_TESTS**: "true" or "false" (default: false)
- **RUN_LOAD_TEST**: "true" or "false" (default: false)

## Requirements

- Docker for containerization
- curl for API testing
- kubectl for Kubernetes deployment
- Locust for load testing (`pip install locust`)
- Postman for API testing (optional)

## API Endpoints Tested

- **GET /health**: Health check endpoint
- **POST /api/v1/query**: Main query endpoint for tax law questions
- **GET /**: Root endpoint

## Kubernetes Features

When deploying to Kubernetes, the system includes:

- Horizontal Pod Autoscaler for automatic scaling
- Resource limits and requests
- Health probes
- Multi-service deployment (API, PostgreSQL, ChromaDB, RabbitMQ)

## Continuous Integration

These scripts can be integrated into CI/CD pipelines for automated testing and deployment. Example GitHub Actions workflow:

```yaml
name: API Testing

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install locust
    - name: Run API tests
      run: |
        chmod +x api_deployment_and_testing.sh
        ./api_deployment_and_testing.sh "http://localhost:8000" "local" "false" "false"
    - name: Run load tests
      run: |
        ./api_deployment_and_testing.sh "http://localhost:8000" "local" "false" "true"
```

## Support

For more information, see the documentation files in the `docs/` directory.
