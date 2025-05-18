#!/bin/bash

# Define colors for a better look
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- Welcome Banner ---
echo -e "${BLUE}"
echo "-----------------------------------------------------"
echo "  Watsonx NeuroSymbolic Decision Framework Launcher  "
echo "-----------------------------------------------------"
echo -e "${NC}"
echo "This script will help you start the application."
echo ""

# --- Ask for Environment ---
ENVIRONMENT=""
while true; do
    echo -e "${YELLOW}Choose your backend environment:${NC}"
    echo "1) Container Environment (Docker Compose)"
    echo "2) Local Development Environment (Python Backend)"
    read -p "Enter choice (1 or 2): " env_choice

    case $env_choice in
        1) ENVIRONMENT="container"; break;;
        2) ENVIRONMENT="local"; break;;
        *) echo -e "${RED}Invalid choice. Please enter 1 or 2.${NC}";;
    esac
    echo "" # Add space for readability
done

echo -e "${GREEN}You selected: $ENVIRONMENT backend environment.${NC}"
echo ""

# --- Ask for AI System ---
AI_SYSTEM=""
while true; do
    echo -e "${YELLOW}Choose your AI System:${NC}"
    echo "1) Watsonx.ai (Online)"
    echo "2) Local Ollama"
    read -p "Enter choice (1 or 2): " ai_choice

    case $ai_choice in
        1) AI_SYSTEM="watsonx"; break;;
        2) AI_SYSTEM="ollama"; break;;
        *) echo -e "${RED}Invalid choice. Please enter 1 or 2.${NC}";;
    esac
    echo "" # Add space for readability
done

echo -e "${GREEN}You selected: $AI_SYSTEM AI system.${NC}"
echo ""

# --- Execution Logic ---

if [ "$ENVIRONMENT" == "container" ]; then
    echo -e "${BLUE}--- Starting Container Environment (Backend & Frontend) ---${NC}"

    echo -e "${YELLOW}INFO:${NC} When using the Container Environment, the frontend container"
    echo "      defined in docker-compose.yml will be started automatically."
    echo -e "${YELLOW}INFO:${NC} Ensure you have copied either 'watsonx.env' or 'ollama.env'"
    echo "      to '.env' in the root directory based on your AI system choice."
    echo ""

    echo -e "${BLUE}Running 'docker compose up -d'...${NC}"
    # Check if docker compose is available
    if ! command -v docker compose &> /dev/null
    then
        echo -e "${RED}Error:${NC} 'docker compose' command not found. Please install Docker and Docker Compose."
        exit 1
    fi

    # Build and start services in detached mode
    docker compose up -d
    exit_status=$?

    if [ $exit_status -eq 0 ]; then
        echo -e "${GREEN}Docker Compose started successfully!${NC}"
        echo -e "${BLUE}Access the Chatbot Frontend at: ${YELLOW}http://localhost:8080${NC}"
        echo -e "${BLUE}You can view logs with: ${YELLOW}docker compose logs${NC}"
        echo -e "${BLUE}To stop the services: ${YELLOW}docker compose down${NC}"
    else
        echo -e "${RED}Error:${NC} Failed to start Docker Compose services. Please check the output above."
        echo "Common issues: Docker not running, incorrect .env file, port conflicts."
        exit $exit_status
    fi

elif [ "$ENVIRONMENT" == "local" ]; then
    echo -e "${BLUE}--- Preparing for Local Development Environment (Backend) ---${NC}"

    echo -e "${YELLOW}INFO:${NC} Local backend development requires Python 3.11+ and a virtual environment."
    echo "      Please ensure you have followed the steps in README_LOCAL.md"
    echo "      to set up the virtual environment and install dependencies ('pip install -r neuro-symbolic-agent/requirements.txt')."
    echo ""

    if [ "$AI_SYSTEM" == "ollama" ]; then
        echo -e "${BLUE}Starting Local Ollama...${NC}"
        # Check if the script exists and is executable
        if [ ! -f "./start-ollama.sh" ]; then
            echo -e "${RED}Error:${NC} 'start-ollama.sh' script not found in the current directory."
            # Don't exit, maybe Ollama is already running
            ollama_status=1
        elif [ ! -x "./start-ollama.sh" ]; then
            echo -e "${YELLOW}Warning:${NC} 'start-ollama.sh' is not executable. Attempting to make it executable."
            chmod +x "./start-ollama.sh"
            if [ $? -ne 0 ]; then
                 echo -e "${RED}Error:${NC} Failed to make 'start-ollama.sh' executable. Please check permissions."
                 # Don't exit
                 ollama_status=1
            else
                 ./start-ollama.sh
                 ollama_status=$?
            fi
        else
            ./start-ollama.sh
            ollama_status=$?
        fi


        if [ $ollama_status -eq 0 ]; then
            echo -e "${GREEN}Local Ollama script executed successfully!${NC}"
        else
            echo -e "${RED}Error:${NC} Failed to execute 'start-ollama.sh' or script not found. Please check its output and requirements (e.g., Ollama installed and running).${NC}"
        fi

    elif [ "$AI_SYSTEM" == "watsonx" ]; then
        echo -e "${YELLOW}INFO:${NC} For Watsonx.ai locally, ensure your '.env' file has"
        echo "      the correct WATSONX_APIKEY, WATSONX_PROJECT_ID, and WATSONX_URL set."
    fi

    echo ""
    echo -e "${BLUE}--- Backend Preparation Steps Completed ---${NC}"
    echo ""

    # --- Ask about Frontend ---
    START_FRONTEND=""
    while true; do
        echo -e "${YELLOW}Do you want to start the frontend?${NC}"
        read -p "Enter choice (yes/no): " start_frontend_choice
        start_frontend_choice=$(echo "$start_frontend_choice" | tr '[:upper:]' '[:lower:]') # Convert to lowercase

        case $start_frontend_choice in
            yes|y) START_FRONTEND="yes"; break;;
            no|n) START_FRONTEND="no"; break;;
            *) echo -e "${RED}Invalid choice. Please enter 'yes' or 'no'.${NC}";;
        esac
        echo "" # Add space
    done

    if [ "$START_FRONTEND" == "yes" ]; then
        FRONTEND_TYPE=""
        while true; do
            echo "" # Add space
            echo -e "${YELLOW}How do you want to run the frontend?${NC}"
            echo "1) Local Node.js (Requires Node 20+ and 'npm install' in chatbot-frontend)"
            echo "2) Container (Requires Docker)"
            read -p "Enter choice (1 or 2): " frontend_type_choice

            case $frontend_type_choice in
                1) FRONTEND_TYPE="local"; break;;
                2) FRONTEND_TYPE="container"; break;;
                *) echo -e "${RED}Invalid choice. Please enter 1 or 2.${NC}";;
            esac
            echo "" # Add space
        done

        if [ "$FRONTEND_TYPE" == "local" ]; then
            echo -e "${BLUE}--- Starting Local Node.js Frontend ---${NC}"

            # Check if Node.js and npm are installed
            if ! command -v node &> /dev/null || ! command -v npm &> /dev/null
            then
                echo -e "${RED}Error:${NC} Node.js and npm are required for the local frontend but not found."
                echo "Please install Node.js (version 20+ recommended)."
                # Don't exit, let the user know other manual steps
            else
                 echo -e "${YELLOW}INFO:${NC} Ensure you have run 'npm install' in 'chatbot-frontend' at least once."
                 echo -e "${BLUE}Navigating to chatbot-frontend and running 'npm run dev'...${NC}"
                 cd chatbot-frontend || { echo -e "${RED}Error:${NC} Could not change directory to chatbot-frontend."; }

                 # Check if in the correct directory before running npm
                 if [ -d "src" ] && [ -f "package.json" ]; then
                    npm run dev
                    npm_status=$?
                     if [ $npm_status -ne 0 ]; then
                         echo -e "${RED}Error:${NC} 'npm run dev' failed. Check output above."
                         echo "Common issues: npm dependencies not installed ('npm install'), port 8080 already in use."
                     else
                         echo -e "${GREEN}Local frontend started!${NC}"
                         echo -e "${BLUE}Access the Chatbot Frontend at: ${YELLOW}http://localhost:8080${NC}"
                         echo -e "${YELLOW}Note:${NC} This command runs in the foreground. Open a new terminal"
                         echo "      to start the local backend if you haven't already."
                     fi
                 else
                     echo -e "${RED}Error:${NC} Not in the chatbot-frontend directory. Cannot run npm commands.${NC}"
                 fi
                 # Change back to the root directory after trying to run
                 cd ..
            fi


        elif [ "$FRONTEND_TYPE" == "container" ]; then
            echo -e "${BLUE}--- Building and Running Frontend Container ---${NC}"
            echo -e "${YELLOW}INFO:${NC} This will build a Docker image for the frontend and run it."
            echo -e "${YELLOW}INFO:${NC} Ensure Docker is running.${NC}"

             # Check if docker is available
            if ! command -v docker &> /dev/null
            then
                echo -e "${RED}Error:${NC} 'docker' command not found. Please install Docker."
                 # Don't exit, let the user know other manual steps
            else
                echo -e "${BLUE}Navigating to chatbot-frontend and building frontend image...${NC}"
                 cd chatbot-frontend || { echo -e "${RED}Error:${NC} Could not change directory to chatbot-frontend."; }

                # Check if in the correct directory before running docker build
                if [ -f "Dockerfile" ]; then
                    # Build image
                    docker build . --build-arg API_URL=http://localhost:9000 -t nginx-app -m 4g
                    build_status=$?

                    if [ $build_status -eq 0 ]; then
                        echo -e "${GREEN}Frontend Docker image built successfully!${NC}"
                        echo -e "${BLUE}Running frontend container on port 8080...${NC}"
                        # Run container (remove any old ones first quietly)
                        docker rm -f nginx-app-instance &> /dev/null
                        docker run -d --name nginx-app-instance -p 8080:80 nginx-app
                         run_status=$?
                         if [ $run_status -eq 0 ]; then
                             echo -e "${GREEN}Frontend container started!${NC}"
                             echo -e "${BLUE}Access the Chatbot Frontend at: ${YELLOW}http://localhost:8080${NC}"
                             echo -e "${CYAN}To stop this specific frontend container: ${YELLOW}docker stop nginx-app-instance${NC}"
                             echo -e "${YELLOW}Note:${NC} The backend is NOT running in a container. You still"
                             echo "      need to start the local backend Python script."
                         else
                             echo -e "${RED}Error:${NC} Failed to run frontend container. Port 8080 might be in use.${NC}"
                         fi
                    else
                         echo -e "${RED}Error:${NC} Failed to build frontend Docker image. Check output above."
                    fi
                else
                     echo -e "${RED}Error:${NC} Dockerfile not found in the chatbot-frontend directory. Cannot build image.${NC}"
                fi
                # Change back to the root directory after trying to run
                 cd ..
            fi
        fi
    fi

    echo ""
    echo -e "${BLUE}--- Important Next Steps for Local Development ---${NC}"
    echo "1) ${YELLOW}Start the Local Backend Python Script:${NC}"
    echo "   Navigate to the neuro-symbolic-agent directory, activate your venv,"
    echo "   and run 'python main.py'."
    echo "   ${CYAN}Example:${NC}"
    echo "   ${GREEN}source .venv/bin/activate${NC}"
    echo "   ${GREEN}cd neuro-symbolic-agent${NC}"
    echo "   ${GREEN}python main.py${NC}"
    echo ""
    if [ "$START_FRONTEND" != "yes" ] || [ "$FRONTEND_TYPE" == "local" ]; then
        echo "2) ${YELLOW}Start the Local Frontend Node.js Script (if not already done):${NC}"
        echo "   Open a ${YELLOW}separate terminal window${NC},"
        echo "   navigate to the ${CYAN}chatbot-frontend${NC} directory, ensure dependencies are"
        echo "   installed (${CYAN}npm install${NC} - one time), and run:"
        echo "   ${GREEN}npm run dev${NC}"
        echo ""
         echo "   Once both backend and frontend are running, access the UI at: ${YELLOW}http://localhost:8080${NC}"

    elif [ "$START_FRONTEND" == "yes" ] && [ "$FRONTEND_TYPE" == "container" ]; then
        echo "2) ${YELLOW}The Frontend Container has been started (if successful).${NC}"
         echo "   Access the UI at: ${YELLOW}http://localhost:8080${NC}"
    fi

fi

# --- Ask to initialize ODM server ---
read -p "Initialize ODM server? [Y/n]: " init_odm_choice
init_odm_choice=${init_odm_choice:-Y}
if [[ "$init_odm_choice" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Initializing ODM server...${NC}"
    if [ -x "./odm/start_odm.sh" ]; then
        ./odm/start_odm.sh
    else
        echo -e "${YELLOW}Warning:${NC} './odm/start_odm.sh' not found or not executable. Skipping ODM initialization."
    fi
fi


echo ""
echo -e "${BLUE}-----------------------------------------------------${NC}"
echo -e "${GREEN}Setup process selection complete.${NC}"
echo -e "${BLUE}-----------------------------------------------------${NC}"

exit 0