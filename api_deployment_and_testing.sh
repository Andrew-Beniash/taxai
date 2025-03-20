#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Default variables
API_URL=${1:-"http://localhost:8000"}
DEPLOYMENT_TYPE=${2:-"local"}  # Options: local, kubernetes
SKIP_TESTS=${3:-"false"}
RUN_LOAD_TEST=${4:-"false"}

# Function to display script header
print_header() {
    echo -e "\n${BLUE}======================================${NC}"
    echo -e "${BLUE}  Tax AI API Deployment and Testing  ${NC}"
    echo -e "${BLUE}======================================${NC}\n"
    echo -e "${BLUE}API URL: ${YELLOW}$API_URL${NC}"
    echo -e "${BLUE}Deployment Type: ${YELLOW}$DEPLOYMENT_TYPE${NC}"
    echo -e "${BLUE}Skip Tests: ${YELLOW}$SKIP_TESTS${NC}"
    echo -e "${BLUE}Run Load Test: ${YELLOW}$RUN_LOAD_TEST${NC}\n"
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    local missing_tools=()
    
    # Check for curl
    if ! command -v curl &> /dev/null; then
        missing_tools+=("curl")
    fi
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    # For Kubernetes deployments, check for kubectl
    if [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
        if ! command -v kubectl &> /dev/null; then
            missing_tools+=("kubectl")
        fi
        
        # Check if Kubernetes cluster is running
        if ! kubectl cluster-info &> /dev/null; then
            echo -e "${RED}Error: Kubernetes cluster is not running.${NC}"
            echo -e "${YELLOW}Please start your Kubernetes cluster (minikube, k3s, etc.)${NC}"
            exit 1
        fi
    fi
    
    # For load tests, check for locust
    if [[ "$RUN_LOAD_TEST" == "true" ]]; then
        if ! command -v locust &> /dev/null; then
            missing_tools+=("locust (can be installed via 'pip install locust')")
        fi
    fi
    
    # If any tools are missing, report and exit
    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo -e "${RED}Missing required tools:${NC}"
        for tool in "${missing_tools[@]}"; do
            echo -e "${RED}- $tool${NC}"
        done
        echo -e "${YELLOW}Please install the missing tools and try again.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ All prerequisites are installed.${NC}"
}

# Function to test API with curl
test_api_with_curl() {
    echo -e "\n${BLUE}Testing API with curl...${NC}"
    
    # Check if API is reachable
    echo -e "${BLUE}Checking if API is reachable...${NC}"
    if curl -s --head --request GET "$API_URL/health" | grep "200 OK" > /dev/null; then
        echo -e "${GREEN}✓ API is reachable${NC}"
    else
        echo -e "${RED}✗ API is not reachable at $API_URL${NC}"
        echo -e "${YELLOW}Starting local API server...${NC}"
        
        # Start API server in background if using local deployment
        if [[ "$DEPLOYMENT_TYPE" == "local" ]]; then
            echo -e "${BLUE}Starting local API server...${NC}"
            cd "$(dirname "$0")" && uvicorn main:app --host 0.0.0.0 --port 8000 &
            API_PID=$!
            
            # Wait for API to become available
            echo -e "${BLUE}Waiting for API to start...${NC}"
            for i in {1..30}; do
                if curl -s --head --request GET "$API_URL/health" | grep "200 OK" > /dev/null; then
                    echo -e "${GREEN}✓ API has started successfully${NC}"
                    break
                fi
                
                if [[ $i -eq 30 ]]; then
                    echo -e "${RED}✗ Failed to start API after 30 seconds${NC}"
                    if [[ -n "$API_PID" ]]; then
                        kill $API_PID
                    fi
                    exit 1
                fi
                
                echo -n "."
                sleep 1
            done
            echo ""
        else
            echo -e "${RED}✗ Cannot continue without a working API endpoint${NC}"
            exit 1
        fi
    fi
    
    # Health check test
    echo -e "\n${BLUE}Testing health check endpoint...${NC}"
    HEALTH_RESPONSE=$(curl -s -X GET "$API_URL/health")
    if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
        echo -e "${GREEN}✓ Health check passed: $HEALTH_RESPONSE${NC}"
    else
        echo -e "${RED}✗ Health check failed: $HEALTH_RESPONSE${NC}"
        if [[ -n "$API_PID" ]]; then
            kill $API_PID
        fi
        exit 1
    fi
    
    # Wait for model to load (modified to be faster for testing purposes)
    echo -e "\n${BLUE}Checking if AI model is loaded...${NC}"
    MODEL_LOADED=false
    MAX_ATTEMPTS=5  # Reduced for testing
    ATTEMPT=1
    
    while [ "$MODEL_LOADED" = false ] && [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
        echo -e "${BLUE}Checking if model is loaded (attempt $ATTEMPT/$MAX_ATTEMPTS)...${NC}"
        HEALTH_RESPONSE=$(curl -s -X GET "$API_URL/health")
        if [[ $HEALTH_RESPONSE == *"model_loaded\":true"* ]]; then
            MODEL_LOADED=true
            echo -e "${GREEN}✓ Model loaded successfully!${NC}"
        else
            echo -e "${BLUE}Model is still loading, waiting 5 seconds...${NC}"
            sleep 5
            ATTEMPT=$((ATTEMPT+1))
        fi
    done
    
    if [ "$MODEL_LOADED" = false ]; then
        echo -e "${YELLOW}⚠ Model is not loaded yet, tests may fail.${NC}"
        echo -e "${YELLOW}Continuing with tests anyway...${NC}"
    fi
    
    # Test tax query endpoint - positive case
    echo -e "\n${BLUE}Testing tax query endpoint (positive case)...${NC}"
    QUERY_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/query" \
        -H "Content-Type: application/json" \
        -d '{"query": "What are the tax deductions for a small business?"}')
    
    if [[ $QUERY_RESPONSE == *"response"* && $QUERY_RESPONSE == *"citations"* ]]; then
        echo -e "${GREEN}✓ Tax query endpoint responded successfully${NC}"
        # Extract and display a portion of the response
        RESPONSE_PREVIEW=$(echo $QUERY_RESPONSE | grep -o '"response":"[^"]*"' | cut -d'"' -f4 | cut -c1-150)
        echo -e "${BLUE}Response preview:${NC}"
        echo -e "${YELLOW}$RESPONSE_PREVIEW...${NC}"
    else
        echo -e "${RED}✗ Tax query endpoint failed: $QUERY_RESPONSE${NC}"
    fi
    
    # Test tax query endpoint - empty query (should be rejected)
    echo -e "\n${BLUE}Testing tax query endpoint (validation case)...${NC}"
    EMPTY_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/query" \
        -H "Content-Type: application/json" \
        -d '{"query": ""}')
    
    if [[ $EMPTY_RESPONSE == *"detail"* ]]; then
        echo -e "${GREEN}✓ Validation correctly rejects empty queries${NC}"
    else
        echo -e "${RED}✗ Validation test failed: $EMPTY_RESPONSE${NC}"
    fi
    
    echo -e "\n${GREEN}Basic API testing completed successfully!${NC}"
}

# Function to deploy using Docker + Kubernetes
deploy_to_kubernetes() {
    echo -e "\n${BLUE}Deploying API to Kubernetes...${NC}"
    
    # Build Docker image
    echo -e "${BLUE}Building Docker image...${NC}"
    docker build -t taxai-api:latest .
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to build Docker image${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
    
    # If using minikube, load the image
    if command -v minikube &> /dev/null; then
        echo -e "${BLUE}Loading image into minikube...${NC}"
        minikube image load taxai-api:latest
    fi
    
    # Deploy to Kubernetes
    echo -e "${BLUE}Deploying to Kubernetes...${NC}"
    
    # Create namespace if it doesn't exist
    kubectl create namespace taxai 2>/dev/null || true
    
    # Set context to the namespace
    kubectl config set-context --current --namespace=taxai
    
    # Apply Kubernetes resources in the correct order
    echo -e "${BLUE}Applying ConfigMap and Secret...${NC}"
    kubectl apply -f kubernetes/configmap.yaml
    kubectl apply -f kubernetes/secret.yaml
    
    echo -e "${BLUE}Applying PersistentVolumeClaims...${NC}"
    kubectl apply -f kubernetes/postgres-pvc.yaml
    kubectl apply -f kubernetes/chroma-pvc.yaml
    kubectl apply -f kubernetes/rabbitmq-pvc.yaml
    
    echo -e "${BLUE}Deploying backend services...${NC}"
    kubectl apply -f kubernetes/postgres-deployment.yaml
    kubectl apply -f kubernetes/postgres-service.yaml
    kubectl apply -f kubernetes/chroma-deployment.yaml
    kubectl apply -f kubernetes/chroma-service.yaml
    kubectl apply -f kubernetes/rabbitmq-deployment.yaml
    kubectl apply -f kubernetes/rabbitmq-service.yaml
    
    echo -e "${BLUE}Waiting for backend services to be ready...${NC}"
    kubectl wait --for=condition=available --timeout=120s deployment/taxai-postgres
    kubectl wait --for=condition=available --timeout=120s deployment/taxai-chroma
    kubectl wait --for=condition=available --timeout=120s deployment/taxai-rabbitmq
    
    echo -e "${BLUE}Deploying API service...${NC}"
    kubectl apply -f kubernetes/api-deployment.yaml
    kubectl apply -f kubernetes/api-service.yaml
    kubectl apply -f kubernetes/api-hpa.yaml
    
    # Apply Ingress last
    echo -e "${BLUE}Applying Ingress...${NC}"
    kubectl apply -f kubernetes/ingress.yaml
    
    # Check deployment status
    echo -e "${BLUE}Checking deployment status...${NC}"
    kubectl get pods
    
    # Wait for API pods to be ready
    echo -e "${BLUE}Waiting for API pods to be ready...${NC}"
    kubectl wait --for=condition=available --timeout=300s deployment/taxai-api
    
    echo -e "${GREEN}✓ Kubernetes deployment completed!${NC}"
    
    # Get the API URL
    if command -v minikube &> /dev/null; then
        MINIKUBE_IP=$(minikube ip)
        echo -e "${GREEN}✓ API is deployed at: http://$MINIKUBE_IP:30000${NC}"
        echo -e "${YELLOW}Note: You may need to use port-forwarding to access the API:${NC}"
        echo -e "${YELLOW}kubectl port-forward svc/taxai-api 8000:8000${NC}"
    else
        echo -e "${GREEN}✓ API is deployed. Use kubectl port-forward to access:${NC}"
        echo -e "${YELLOW}kubectl port-forward svc/taxai-api 8000:8000${NC}"
    fi
}

# Function to run load tests
run_load_test() {
    echo -e "\n${BLUE}Running load tests with Locust...${NC}"
    
    # Check if Locust is installed
    if ! command -v locust &> /dev/null; then
        echo -e "${RED}Locust is not installed. Installing now...${NC}"
        pip install locust
    fi
    
    # Check if load test script exists
    if [ ! -f "load_test.py" ]; then
        echo -e "${RED}Error: load_test.py not found${NC}"
        exit 1
    fi
    
    # Run load test in headless mode with 10 users
    echo -e "${BLUE}Starting load test with 10 concurrent users for 30 seconds...${NC}"
    locust -f load_test.py --host=$API_URL --headless -u 10 -r 2 --run-time 30s
    
    echo -e "\n${GREEN}Load testing completed!${NC}"
    echo -e "${YELLOW}For more detailed load testing, run:${NC}"
    echo -e "${YELLOW}locust -f load_test.py --host=$API_URL${NC}"
    echo -e "${YELLOW}And open http://localhost:8089 in your browser${NC}"
}

# Main script execution
print_header
check_prerequisites

# Deploy if needed
if [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
    deploy_to_kubernetes
fi

# Run tests if not skipped
if [[ "$SKIP_TESTS" != "true" ]]; then
    test_api_with_curl
fi

# Run load tests if requested
if [[ "$RUN_LOAD_TEST" == "true" ]]; then
    run_load_test
fi

# Cleanup
if [[ -n "$API_PID" ]]; then
    echo -e "\n${BLUE}Stopping local API server...${NC}"
    kill $API_PID
fi

echo -e "\n${GREEN}All tasks completed successfully!${NC}"
echo -e "${BLUE}===============================${NC}"
