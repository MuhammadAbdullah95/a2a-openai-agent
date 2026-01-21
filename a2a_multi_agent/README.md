# Multi-Agent A2A Demo with OpenAI Agents SDK

A multi-agent implementation demonstrating the **Agent2Agent (A2A) Protocol** with three collaborating agents using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/).

## Agents Overview

| Agent | Port | Description |
|-------|------|-------------|
| **TellTimeAgent** | 10000 | Returns the current system time |
| **GreetingAgent** | 10001 | Fetches time from TellTimeAgent and generates a poetic greeting |
| **OrchestratorAgent** | 10002 | Routes requests to the appropriate child agent |

---

## Project Structure

```bash
a2a_multi_agent/
├── .env                         # Your OPENAI_API_KEY (not committed)
├── pyproject.toml               # Dependency config
├── README.md                    # You are reading it!
├── app/
│   └── cmd/
│       └── cmd.py               # CLI to interact with the OrchestratorAgent
├── a2a_agents/                  # Agent implementations
│   ├── tell_time_agent/
│   │   ├── __main__.py          # Starts TellTimeAgent server
│   │   ├── agent.py             # OpenAI Agents SDK-based time agent
│   │   └── task_manager.py      # In-memory task handler for TellTimeAgent
│   ├── greeting_agent/
│   │   ├── __main__.py          # Starts GreetingAgent server
│   │   ├── agent.py             # Orchestrator that calls TellTimeAgent + LLM greeting
│   │   └── task_manager.py      # Task handler for GreetingAgent
│   └── host_agent/
│       ├── entry.py             # CLI to start OrchestratorAgent server
│       ├── orchestrator.py      # LLM router + TaskManager for OrchestratorAgent
│       └── agent_connect.py     # Helper to call child A2A agents
├── server/
│   ├── server.py                # A2A JSON-RPC server implementation
│   └── task_manager.py          # Base in-memory task manager interface
├── client/
│   └── client.py                # A2A client for sending requests
├── models/
│   ├── agent.py                 # AgentCard, AgentSkill, AgentCapabilities
│   ├── json_rpc.py              # JSON-RPC request/response formats
│   ├── request.py               # SendTaskRequest, A2ARequest union
│   └── task.py                  # Task structure, messages, status
└── utilities/
    ├── discovery.py             # Finds agents via agent_registry.json
    └── agent_registry.json      # List of child-agent URLs
```

---

## Setup

### 1. Navigate to this directory

```bash
cd a2a_multi_agent
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

```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

---

## Running the Demo

Open **four terminal windows** and run each command in order:

**Terminal 1 - Start TellTimeAgent:**
```bash
python -m a2a_agents.tell_time_agent --host localhost --port 10000
```

**Terminal 2 - Start GreetingAgent:**
```bash
python -m a2a_agents.greeting_agent --host localhost --port 10001
```

**Terminal 3 - Start OrchestratorAgent:**
```bash
python -m a2a_agents.host_agent.entry --host localhost --port 10002
```

**Terminal 4 - Launch the CLI:**
```bash
python -m app.cmd.cmd --agent http://localhost:10002
```

---

## Try It Out

```bash
> What time is it?
Agent says: The current time is: 2025-05-05 14:23:10

> Greet me
Agent says: Good afternoon, friend! The golden sun dips low...
```

---

## How It Works

1. **Discovery**: OrchestratorAgent reads `utilities/agent_registry.json` and fetches each agent's `/.well-known/agent.json`
2. **Routing**: Based on intent, the Orchestrator's LLM calls its tools:
   - `list_agents()` - lists child-agent names
   - `delegate_task(agent_name, message)` - forwards tasks
3. **Child Agents**:
   - TellTimeAgent returns the current time
   - GreetingAgent calls TellTimeAgent then crafts a poetic greeting
4. **JSON-RPC**: All communication uses A2A JSON-RPC 2.0 over HTTP

---

## Tech Stack

- **OpenAI Agents SDK** - Agent orchestration and tool calling
- **Starlette** - Lightweight ASGI web framework
- **Uvicorn** - ASGI web server
- **httpx** - Async HTTP client
- **Pydantic** - Data validation

---

## A2A Protocol Resources

| Resource | Link |
|----------|------|
| Official Documentation | [a2a-protocol.org](https://a2a-protocol.org) |
| Protocol Specification | [A2A Specification](https://a2a-protocol.org/latest/specification/) |
| GitHub Repository | [github.com/a2aproject/A2A](https://github.com/a2aproject/A2A) |
| Python SDK | [a2a-python](https://github.com/a2aproject/a2a-python) |

---

## Connect with Me

- LinkedIn: [Muhammad Abdullah](https://www.linkedin.com/in/muhammad-abdullah-3a8550255/)
- Facebook: [Muhammad Abdullah](https://www.facebook.com/muhammad.abdullah.332635)
- GitHub: [Muhammad Abdullah](https://github.com/MuhammadAbdullah95)

---
