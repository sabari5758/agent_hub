# AgentHub - IT Sector Intelligence Crew

**AgentHub** is an intelligent multi-agent system exposed via a REST API. It uses autonomous AI agents to research technology trends and provide career analysis for the IT sector.

## 🔄 How it Works (API Flow)

When you call an endpoint (e.g., `/research`), the following process occurs:

1.  **Request**: You send a POST request with a JSON payload (e.g., `{"topic": "AI Agents"}`) to the API.
2.  **Orchestration (`api.py`)**:
    *   The FastAPI application receives the request and validates it against the `TrendRequest` schema.
    *   Instead of running a massive crew with all agents, the API dynamically selects only the specific **Agent** (e.g., `tech_scout`) and **Task** (e.g., `research_task`) needed for this specific endpoint.
    *   It assembles a temporary, isolated `Crew` instance.
3.  **Execution (`crew.py`)**:
    *   The `Crew` kicks off the task using the **Groq LLM** (Llama 3.3).
    *   The Agent utilizes its assigned tools (like `google_search` or `website_scraper`) to gather real-time information from the web.
4.  **Response**:
    *   The Agent parses the raw findings into a structured Pydantic model (`TrendResult` or `JobResult`).
    *   The API converts this into a clean JSON response and sends it back to you.

## 📂 Project Logic & Key Files

The core intelligence and behavior of this project are defined in these specific files:

### 1. `src/agent_hub/api.py` (The Interface)
*   **Role**: The API Controller.
*   **Logic**: This file defines the FastAPI endpoints. It acts as the bridge between the outside world and your AI agents. It handles input validation, triggers the specific agentic workflow, and ensures the output is formatted correctly before returning it to the client.

### 2. `src/agent_hub/crew.py` (The Brain)
*   **Role**: The CrewAI Configuration.
*   **Logic**: This file defines the `AgentHub` class. It configures:
    *   **Agents**: Who they are (Tech Scout, Career Analyst) and what LLM they use.
    *   **Tasks**: What they need to do (Research, Analysis) and the expected output format.
    *   **Tools**: The capabilities given to agents (e.g., Google Search).

### 3. `src/agent_hub/config/*.yaml` (The Persona)
*   **Logic**: These YAML files (`agents.yaml`, `tasks.yaml`) contain the natural language prompts that define the personality, goals, and specific instructions for your agents.

## 🚀 Quick Start

### Prerequisites
- Python >=3.10
- UV (recommended)
- API Keys in `.env`: `GROQ_API_KEY`, `SERPER_API_KEY`

### Installation

```bash
pip install uv
crewai install
```

### Running the API

```bash
python src/agent_hub/api.py
```

The server will start at `http://0.0.0.0:8000`.

*   **Research Endpoint**: `POST /research`
*   **Career Endpoint**: `POST /career-advice`
