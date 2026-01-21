# Single Agent A2A Demo - TellTimeAgent

A single-agent implementation demonstrating the **Agent2Agent (A2A) Protocol** using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/).

This agent responds to time-related queries by using a `get_current_time` tool.

---

## Project Structure

```bash
a2a_single_agent/
├── .env                       # API key goes here (not committed)
├── pyproject.toml             # Dependency config (used with uv or pip)
├── README.md                  # You're reading it!
├── app/
│   └── cmd/
│       └── cmd.py             # Command-line app to talk to the agent
├── my_agents/
│   └── openai_sdk/
│       ├── __main__.py        # Starts the agent + A2A server
│       ├── agent.py           # OpenAI agent definition using Agents SDK
│       └── task_manager.py    # Handles task lifecycle
├── server/
│   ├── server.py              # A2A server logic (routes, JSON-RPC)
│   └── task_manager.py        # In-memory task storage + interface
├── client/
│   └── client.py              # A2A client for sending requests
└── models/
    ├── agent.py               # AgentCard, AgentSkill, AgentCapabilities
    ├── json_rpc.py            # JSON-RPC request/response formats
    ├── request.py             # SendTaskRequest, A2ARequest union
    └── task.py                # Task structure, messages, status
```

---

## Features

- OpenAI-powered A2A agent using Agents SDK
- Follows JSON-RPC 2.0 specification
- Supports session handling
- Custom A2A server implementation (non-streaming)
- CLI to interact with agent
- Function tools support
- Fully commented and beginner-friendly

---

## Setup

### 1. Navigate to this directory

```bash
cd a2a_single_agent
```

### 2. Create and activate a virtual environment

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using standard Python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

### 4. Set your API key

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

---

## Running the Agent

**Terminal 1 - Start the agent server:**

```bash
python -m my_agents.openai_sdk
```

You should see:

```
Uvicorn running on http://localhost:10002
```

**Terminal 2 - Start the client:**

```bash
python -m app.cmd.cmd --agent http://localhost:10002
```

---

## Try It Out

```bash
> what time is it?
Agent says: The current time is 2025-05-05 14:23:10
```

---

## Agent Workflow (A2A Lifecycle)

1. The client queries the agent using a CLI (`cmd.py`)
2. The A2A client sends a task using JSON-RPC to the A2A server
3. The server parses the request, invokes the task manager
4. The task manager calls the OpenAI-powered `TellTimeAgent`
5. The agent uses the `get_current_time` tool to get the system time
6. The server wraps the response and sends it back to the client

---

## Tech Stack

- **OpenAI Agents SDK** - Agent orchestration and tool calling
- **Starlette** - Lightweight ASGI web framework
- **Uvicorn** - ASGI web server
- **httpx** - Async HTTP client
- **Pydantic** - Data validation

---

## Connect with Me

- LinkedIn: [Muhammad Abdullah](https://www.linkedin.com/in/muhammad-abdullah-3a8550255/)
- Facebook: [Muhammad Abdullah](https://www.facebook.com/muhammad.abdullah.332635)
- GitHub: [Muhammad Abdullah](https://github.com/MuhammadAbdullah95)

---
