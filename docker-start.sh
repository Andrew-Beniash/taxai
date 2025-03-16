#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting AI-Powered Tax Law Application containers...${NC}"

# Build and start containers
docker-compose up -d

# Check if containers started successfully
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Containers started successfully!${NC}"
    echo -e "${GREEN}Services available at:${NC}"
    echo -e "  - API: http://localhost:8000"
    echo -e "  - ChromaDB: http://localhost:8080"
    echo -e "  - RabbitMQ Management: http://localhost:15672 (guest/guest)"
    echo -e "  - PostgreSQL: localhost:5432 (postgres/postgres)"
    echo ""
    echo -e "${YELLOW}Container logs can be viewed with:${NC}"
    echo -e "  docker-compose logs -f"
    echo ""
    echo -e "${YELLOW}To stop containers:${NC}"
    echo -e "  docker-compose down"
else
    echo -e "${RED}Failed to start containers. Check the logs with:${NC}"
    echo -e "  docker-compose logs"
fi
