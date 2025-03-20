#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL
API_URL=${1:-"http://localhost:8000"}

echo -e "${BLUE}Testing Tax AI API at $API_URL${NC}"

# Health check test
echo -e "\n${BLUE}Testing health check endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s -X GET "$API_URL/health")
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo -e "${GREEN}✓ Health check passed: $HEALTH_RESPONSE${NC}"
else
    echo -e "${RED}✗ Health check failed: $HEALTH_RESPONSE${NC}"
    exit 1
fi

# Wait for model to load
echo -e "\n${BLUE}Waiting for AI model to load (this may take a few minutes)...${NC}"
MODEL_LOADED=false
MAX_ATTEMPTS=30  # Try for about 5 minutes
ATTEMPT=1

while [ "$MODEL_LOADED" = false ] && [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo -e "${BLUE}Checking if model is loaded (attempt $ATTEMPT/$MAX_ATTEMPTS)...${NC}"
    HEALTH_RESPONSE=$(curl -s -X GET "$API_URL/health")
    if [[ $HEALTH_RESPONSE == *"model_loaded\":true"* ]]; then
        MODEL_LOADED=true
        echo -e "${GREEN}✓ Model loaded successfully!${NC}"
    else
        echo -e "${BLUE}Model is still loading, waiting 10 seconds...${NC}"
        sleep 10
        ATTEMPT=$((ATTEMPT+1))
    fi
done

if [ "$MODEL_LOADED" = false ]; then
    echo -e "${RED}✗ Model failed to load after multiple attempts. Check logs for details.${NC}"
    echo -e "${RED}Continuing with tests, but they might fail...${NC}"
fi

# Test tax query endpoint - positive case
echo -e "\n${BLUE}Testing tax query endpoint (positive case)...${NC}"
QUERY_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What are the tax deductions for a small business?"}')

if [[ $QUERY_RESPONSE == *"response"* && $QUERY_RESPONSE == *"citations"* ]]; then
    echo -e "${GREEN}✓ Tax query endpoint responded successfully${NC}"
    # Pretty print the response summary
    echo -e "${BLUE}Response preview:${NC}"
    echo $QUERY_RESPONSE | grep -o '"response":"[^"]*"' | head -50
else
    echo -e "${RED}✗ Tax query endpoint failed: $QUERY_RESPONSE${NC}"
fi

# Test tax query endpoint - empty query (should be rejected)
echo -e "\n${BLUE}Testing tax query endpoint (validation case)...${NC}"
EMPTY_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/query" \
    -H "Content-Type: application/json" \
    -d '{"query": ""}')

if [[ $EMPTY_RESPONSE == *"detail"* && $EMPTY_RESPONSE == *"empty"* ]]; then
    echo -e "${GREEN}✓ Validation correctly rejects empty queries${NC}"
else
    echo -e "${RED}✗ Validation test failed: $EMPTY_RESPONSE${NC}"
fi

echo -e "\n${BLUE}API testing completed${NC}"
