#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Verifying Docker setup...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Docker is installed${NC}"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Docker Compose is installed${NC}"
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Docker daemon is not running. Please start Docker first.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Docker daemon is running${NC}"
fi

# Check if required files exist
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}Dockerfile not found in the current directory.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Dockerfile exists${NC}"
fi

if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}docker-compose.yml not found in the current directory.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ docker-compose.yml exists${NC}"
fi

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}requirements.txt not found in the current directory.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ requirements.txt exists${NC}"
fi

echo -e "${GREEN}All checks passed. You're ready to run the Docker setup with ./docker-start.sh${NC}"
