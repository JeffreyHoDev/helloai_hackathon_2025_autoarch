# Multi-Agent Cloud Architecture Platform

## Overview

This project is a multi-agent system designed to assist pre-sales engineers and cloud practitioners. It leverages a natural language chat interface to generate key cloud artifacts, streamlining the architecture design and deployment process. The system is powered by the Google Agent Development Kit (ADK).

Core capabilities include:

*   **Cloud Architecture Diagram Generation:** Automatically create architecture diagrams from text descriptions.
*   **Technical Proposal Creation:** Generate detailed proposal documents for cloud solutions.
*   **Architecture Validation:** Produce reports that validate the architecture against best practices.
*   **Terraform Configuration:** Generate Infrastructure-as-Code (IaC) files using Terraform.

## Available Agents

The platform uses a hierarchical structure of agents, with a main `root_agent` orchestrating tasks among its sub-agents. The agents are organized as follows, based on the project's directory structure:

*   `root_agent`: The primary agent that manages the overall workflow.
    *   `sub_agents`:
        *   `architecture_validator_agent`: Analyzes and validates architectural designs.
            *   `sub_agents`:
                *   `report_creation_agent`: Generates the final validation report.
        *   `cloud_arch_diagram_agent`: Creates cloud architecture diagrams.
        *   `file_proposal_agent`: Manages and generates file-based proposals. Support DOCX and PDF.
        *   `gcp_agent`: Interacts with Google Cloud Platform.
        *   `terraform_agent`: Generates Terraform infrastructure-as-code files.

### Other Top-Level Agents

*   `cloud_arch_proposal_agent`: A standalone agent for creating architecture proposals.
*   `cloud_cost_analysis_agent`: A standalone agent for analyzing cloud service costs.
*   `diagrams_code_builder_agent`: A specialized agent that generates the code for diagrams.

## Architecture & Deployment

A key aspect of this system's design is the communication between agents. Due to a current limitation in the Google Agent Development Kit (ADK) where sub-agents cannot utilize the Google Search tool, the agents that require web access are designed as standalone services.

Specifically, the `cloud_arch_proposal_agent` and `cloud_cost_analysis_agent` must be deployed independently. They communicate with the main `root_agent` using an Agent-to-Agent (A2A) communication protocol to exchange information and fulfill requests.

## Prerequisites

Before you begin, ensure you have the following installed:

*   Python (3.10+ recommended)
*   `pip` (Python package installer)
*   Docker
*   Google Cloud SDK (`gcloud`)

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/autoarch_project.git
    cd autoarch_project
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install all dependencies:**
    This command finds and installs all `requirements.txt` files in the project.
    ```bash
    find . -name "requirements.txt" -exec pip install -r {} +
    ```

4.  **Authenticate with Google Cloud:**
    Run the following `gcloud` command to authenticate your local environment. This allows the application to use your user credentials to access Google Cloud services (Application Default Credentials).
    ```bash
    gcloud auth application-default login
    ```

5.  **Configure Environment Variables:**
    Create a `.env` file in the project's root directory to store credentials and agent-specific configurations.

    ```env
    # Set to 1 to use the Vertex AI backend, or 0 for the Google AI Studio (Generative Language API) backend.
    GOOGLE_GENAI_USE_VERTEXAI=1

    # Your API key from Google Cloud or Google AI Studio.
    GOOGLE_API_KEY="your_api_key_here"

    # --- GCP Agent Configuration ---
    # The following are required for the gcp_agent to interact with your GCP environment.
    GCP_PROJECT_ID="your-gcp-project-id"
    GCP_SERVICE_ACCOUNT="your-service-account@your-project-id.iam.gserviceaccount.com"
    ```
    **Note:** Ensure the `.env` file is added to your `.gitignore` file to prevent committing secrets.

## Usage

### Live Demo

A deployed version of the service is available for demonstration purposes at:

[https://autoarch-agent-service-945869404169.us-central1.run.app/dev-ui](https://autoarch-agent-service-945869404169.us-central1.run.app/dev-ui)

### Local Development

Running the application locally requires starting the main `root_agent` and any standalone agents separately.

1.  **Start the Standalone A2A Agents:**
    Open a separate terminal for each standalone agent and run the following commands from the project root directory. These servers must be running for the `root_agent` to delegate tasks to them.

    *   **Cloud Proposal Agent:**
        ```bash
        uvicorn cloud_arch_proposal_agent.agent:a2a_app --host localhost --port 8001
        ```
    *   **Cloud Cost Analysis Agent:**
        ```bash
        uvicorn cloud_cost_analysis_agent.agent:a2a_app --host localhost --port 8002
        ```

2.  **Start the Main Application:**
    In a new terminal, run the ADK web interface:
    ```bash
    adk web
    ```
    Navigate to the web UI and select `root_agent` from the list to start interacting with the application.

## Contact

For questions, support, or feedback, please reach out to:

*   hokahwai@google.com
*   jeffreyhodev@gmail.com
