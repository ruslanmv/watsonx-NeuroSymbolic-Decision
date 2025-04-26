# Installation and Setup (Running Components Locally)

This guide explains how to set up and run the backend and frontend components of the application directly on your local Linux machine, while keeping the IBM ODM server running in a Docker container as defined in the `docker-compose.yml`.

## Prerequisites

Before you begin, ensure you have the following installed on your Linux system:

* **Docker and Docker Compose:** Required to run the ODM container.
* **Python 3 and pip:** Necessary for the backend application (`rule-agent`).
* **Node.js and npm or yarn:** Required for the frontend application (`chatbot-frontend`).
* **Source Code:** The complete project source code, including the `docker-compose.yml`, `rule-agent`, `chatbot-frontend`, and the `llm.env` file, structured as expected by the compose file.

## Setup Procedure

Follow these steps in order:

### Step 1: Start the IBM ODM Server (Using Docker)

Running IBM ODM directly outside of Docker is complex. The easiest approach is to use the Docker container defined in your `docker-compose.yml` for the ODM service.

1.  Open your terminal and navigate to the root directory of your project (the directory containing `docker-compose.yml`).
    ```bash
    cd /path/to/your/project
    ```
2.  Start only the `odm` service in detached mode (`-d`):
    ```bash
    docker compose up -d odm
    ```
    This command will pull the `ibmcom/odm` image (if not already present) and start the container.
3.  Wait for the ODM container to become healthy. You can check its status using:
    ```bash
    docker compose ps
    ```
    Look for `(healthy)` next to the `odm` container status. This might take several minutes as ODM starts up. You can also view the logs for the `odm` container to see its progress:
    ```bash
    docker compose logs odm
    ```
    The ODM server will be accessible on your local machine at `http://localhost:9060`.




You need to set the `ODM_SERVER_URL` environment variable in the same terminal session *before* you run `bash serverStart.sh`. Since you are running the ODM server via Docker Compose and it's mapped to `9060` on your host (as confirmed by `docker compose ps`), the URL from your local machine should be `http://localhost:9060`.

1.  Open your terminal and navigate to your project root directory.
2.  Set the environment variable:
    ```bash
    export ODM_SERVER_URL="http://localhost:9060"
    ```


### Step 2: Run the Backend (rule-agent) Locally

The backend code is located in the `./rule-agent` directory.

1.  Navigate into the backend source directory:
    ```bash
    cd rule-agent
    ```
2.  **Set Environment Variables:** You need to replicate the environment variables defined in `docker-compose.yml` and your `llm.env` file. Use `export` to set these variables in your current terminal session.

    ```bash
    # Variables from docker-compose.yml
    export ODM_SERVER_URL="http://localhost:9060" # Connect to the Dockerized ODM running on your host
    export ODM_USERNAME="odmAdmin"
    export ODM_PASSWORD="odmAdmin"
    export PYTHONUNBUFFERED="1"
    export DATADIR="./data" # This path is relative to the current directory (rule-agent)

    # Variables from llm.env
    # You need to manually export each variable found in your llm.env file.
    # Example (replace with actual variables from your llm.env):
    export LLM_API_KEY="your_api_key_here"
    export ANOTHER_LLM_VARIABLE="another_value"

    # Alternatively, if llm.env contains simple KEY=VALUE pairs, you might be able to source it:
    # source ../llm.env # Assuming llm.env is in the parent directory
    ```
    Ensure the `./data` directory exists inside the `rule-agent` directory:
    ```bash
    mkdir -p ./data
    ```

3.  **Install Python Dependencies:** Look for a `requirements.txt` file in the `rule-agent` directory and install the necessary libraries.
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Backend Application:** The exact command to start the backend depends on its implementation. Look for a main script (e.g., `main.py`) or instructions within the `rule-agent` directory.
    ```bash
    # Example command (might vary based on your project structure)
    python main.py
    # Or it might be a command specific to a framework, e.g.:
    # flask run --port 9000
    ```
    The backend should start and listen on port 9000. Keep this terminal window open to see logs.

### Step 3: Run the Frontend (chatbot-frontend) Locally

The frontend code is located in the `./chatbot-frontend` directory.

1.  Navigate back to the project root and then into the frontend source directory:
    ```bash
    cd ../chatbot-frontend
    ```
2.  **Install Node.js Dependencies:** Look for a `package.json` file and install the project's dependencies using npm or yarn.
    ```bash
    npm install
    # Or if using yarn:
    # yarn install
    ```
3.  **Configure Backend API URL:** The frontend needs to know the address of the running backend API (`http://localhost:9000`). How this is configured depends on the frontend framework. It's often done via an environment variable set before starting the development server. Consult your frontend's documentation or code.
    ```bash
    # Example using a common pattern for frontend frameworks (variable name may differ)
    export REACT_APP_API_URL="http://localhost:9000"
    # Or if your frontend uses a proxy setting, you might configure that instead.
    ```
4.  **Run the Frontend Application:** Start the frontend development server. Look for a script like `start` in the `scripts` section of `package.json`.
    ```bash
    npm start
    # Or if using yarn:
    # yarn start
    ```
    The frontend development server should start, likely opening the application in your web browser at `http://localhost:8080`. Keep this terminal window open.

## Accessing the Application

Once all three components (ODM Docker, Local Backend, Local Frontend) are running:

* The IBM ODM console should be accessible at `http://localhost:9060`.
* The Backend API should be running locally on port 9000.
* The Frontend Chatbot application should be accessible in your web browser at `http://localhost:8080`.

## Stopping the Application

* To stop the local backend and frontend, press `Ctrl+C` in their respective terminal windows.
* To stop the ODM Docker container, navigate back to your project root directory and run:
    ```bash
    docker compose down odm
    ```