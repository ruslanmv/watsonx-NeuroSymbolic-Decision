#!/bin/bash

# Define colors for a better look
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Welcome Banner ---
echo -e "${BLUE}"
echo "-----------------------------------------------------"
echo "  Watsonx NeuroSymbolic Decision Framework Stopper   "
echo "-----------------------------------------------------"
echo -e "${NC}"
echo "This script will stop the Docker containers defined"
echo "in your docker-compose.yml."
echo ""

# --- Stop Logic ---
echo -e "${YELLOW}Stopping Docker Compose services...${NC}"

# Check if docker compose is available
if ! command -v docker compose &> /dev/null
then
    echo -e "${RED}Error:${NC} 'docker compose' command not found. Please ensure Docker and Docker Compose are installed and in your PATH."
    exit 1
fi

# Run the docker compose down command
# Using -v to remove named volumes might be desired for a clean slate, but
# a simple 'down' is usually sufficient to stop containers and remove the default network.
docker compose down
exit_status=$?

# --- Report Status ---
if [ $exit_status -eq 0 ]; then
    echo -e "${GREEN}Docker Compose services stopped successfully!${NC}"
else
    echo -e "${RED}Error:${NC} Failed to stop Docker Compose services. Please check the output above."
    echo "Common issues: No containers were running, permissions problems."
    exit $exit_status
fi

echo ""
echo -e "${BLUE}-----------------------------------------------------${NC}"
echo -e "${GREEN}Stop process complete.${NC}"
echo -e "${BLUE}-----------------------------------------------------${NC}"

exit 0