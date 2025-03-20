#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Stopping all services...${NC}"
docker-compose down

echo -e "${BLUE}Starting services with updated configuration...${NC}"
docker-compose up -d

echo -e "${GREEN}Services restarted. Wait a few minutes for the model to load, then run:${NC}"
echo -e "${BLUE}  ./test_api.sh${NC}"
