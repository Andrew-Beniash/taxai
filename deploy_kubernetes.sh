#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check for required tools
check_requirements() {
    echo -e "${BLUE}Checking requirements...${NC}"
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}kubectl is not installed. Please install it first.${NC}"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}docker is not installed. Please install it first.${NC}"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}Kubernetes is not running. Please start a Kubernetes cluster (minikube, k3s, etc.).${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}All requirements satisfied.${NC}"
}

# Function to build the Docker image
build_docker_image() {
    echo -e "${BLUE}Building Docker image...${NC}"
    
    docker build -t taxai-api:latest .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Docker image built successfully.${NC}"
    else
        echo -e "${RED}Failed to build Docker image.${NC}"
        exit 1
    fi
    
    # If using minikube, load the image into minikube
    if command -v minikube &> /dev/null; then
        echo -e "${BLUE}Loading image into minikube...${NC}"
        minikube image load taxai-api:latest
    fi
}

# Function to deploy to Kubernetes
deploy_to_kubernetes() {
    echo -e "${BLUE}Deploying to Kubernetes...${NC}"
    
    # Create namespace if it doesn't exist
    kubectl create namespace taxai 2>/dev/null || true
    kubectl config set-context --current --namespace=taxai
    
    # Apply Kubernetes configurations
    echo -e "${BLUE}Applying persistent volume claims...${NC}"
    kubectl apply -f kubernetes/postgres-pvc.yaml
    kubectl apply -f kubernetes/chroma-pvc.yaml
    kubectl apply -f kubernetes/rabbitmq-pvc.yaml
    
    echo -e "${BLUE}Applying ConfigMap and Secret...${NC}"
    kubectl apply -f kubernetes/configmap.yaml
    kubectl apply -f kubernetes/secret.yaml
    
    echo -e "${BLUE}Deploying database services...${NC}"
    kubectl apply -f kubernetes/postgres-deployment.yaml
    kubectl apply -f kubernetes/postgres-service.yaml
    kubectl apply -f kubernetes/chroma-deployment.yaml
    kubectl apply -f kubernetes/chroma-service.yaml
    kubectl apply -f kubernetes/rabbitmq-deployment.yaml
    kubectl apply -f kubernetes/rabbitmq-service.yaml
    
    echo -e "${BLUE}Waiting for database services to be ready...${NC}"
    kubectl wait --for=condition=available --timeout=300s deployment/taxai-postgres
    kubectl wait --for=condition=available --timeout=300s deployment/taxai-chroma
    kubectl wait --for=condition=available --timeout=300s deployment/taxai-rabbitmq
    
    echo -e "${BLUE}Deploying API service...${NC}"
    kubectl apply -f kubernetes/api-deployment.yaml
    kubectl apply -f kubernetes/api-service.yaml
    kubectl apply -f kubernetes/api-hpa.yaml
    
    echo -e "${BLUE}Setting up ingress...${NC}"
    kubectl apply -f kubernetes/ingress.yaml
    
    echo -e "${GREEN}Deployment completed!${NC}"
}

# Function to check deployment status
check_status() {
    echo -e "${BLUE}Checking deployment status...${NC}"
    
    echo -e "${BLUE}Pods:${NC}"
    kubectl get pods
    
    echo -e "${BLUE}Services:${NC}"
    kubectl get services
    
    echo -e "${BLUE}Deployments:${NC}"
    kubectl get deployments
    
    echo -e "${BLUE}Horizontal Pod Autoscalers:${NC}"
    kubectl get hpa
    
    echo -e "${BLUE}Ingress:${NC}"
    kubectl get ingress
}

# Function to clean up the deployment
cleanup() {
    echo -e "${BLUE}Cleaning up deployment...${NC}"
    
    kubectl delete -f kubernetes/ingress.yaml
    kubectl delete -f kubernetes/api-hpa.yaml
    kubectl delete -f kubernetes/api-service.yaml
    kubectl delete -f kubernetes/api-deployment.yaml
    kubectl delete -f kubernetes/rabbitmq-service.yaml
    kubectl delete -f kubernetes/rabbitmq-deployment.yaml
    kubectl delete -f kubernetes/chroma-service.yaml
    kubectl delete -f kubernetes/chroma-deployment.yaml
    kubectl delete -f kubernetes/postgres-service.yaml
    kubectl delete -f kubernetes/postgres-deployment.yaml
    kubectl delete -f kubernetes/secret.yaml
    kubectl delete -f kubernetes/configmap.yaml
    kubectl delete -f kubernetes/rabbitmq-pvc.yaml
    kubectl delete -f kubernetes/chroma-pvc.yaml
    kubectl delete -f kubernetes/postgres-pvc.yaml
    
    echo -e "${GREEN}Cleanup completed!${NC}"
}

# Function to show help
show_help() {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  build       Build the Docker image"
    echo "  deploy      Deploy to Kubernetes"
    echo "  status      Check deployment status"
    echo "  cleanup     Clean up the deployment"
    echo "  all         Build, deploy, and check status"
    echo "  help        Show this help message"
}

# Main script
case "$1" in
    build)
        check_requirements
        build_docker_image
        ;;
    deploy)
        check_requirements
        deploy_to_kubernetes
        ;;
    status)
        check_status
        ;;
    cleanup)
        cleanup
        ;;
    all)
        check_requirements
        build_docker_image
        deploy_to_kubernetes
        check_status
        ;;
    help|*)
        show_help
        ;;
esac

exit 0
