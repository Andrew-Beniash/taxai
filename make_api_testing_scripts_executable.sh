#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Making API testing scripts executable...${NC}"

# Make the API deployment and testing script executable
chmod +x api_deployment_and_testing.sh
echo -e "${GREEN}✓ chmod +x api_deployment_and_testing.sh${NC}"

# Make the Postman collection save script executable
chmod +x save-postman-collection.sh
echo -e "${GREEN}✓ chmod +x save-postman-collection.sh${NC}"

echo -e "${BLUE}Done! You can now run the scripts:${NC}"
echo -e "${GREEN}./api_deployment_and_testing.sh${NC}"
echo -e "${GREEN}./save-postman-collection.sh${NC}"
