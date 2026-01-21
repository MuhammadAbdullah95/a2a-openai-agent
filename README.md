# A2A Protocol Examples with OpenAI Agents SDK

A comprehensive collection of **Agent2Agent (A2A) Protocol** implementations using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/). This repository demonstrates how to build interoperable AI agents that communicate via the A2A standard.

---

## What is A2A (Agent-to-Agent) Protocol?

The **Agent2Agent (A2A) Protocol** is an open protocol that enables communication and interoperability between AI agents built on different frameworks by different companies. It was initiated by **Google** and is now maintained as an open-source project under the **Linux Foundation**.

### Why A2A?

As AI agents become more prevalent, their ability to interoperate is crucial for building complex, multi-functional applications. A2A aims to:

- **Break Down Silos** - Connect agents across different ecosystems
- **Enable Complex Collaboration** - Allow specialized agents to work together on tasks that a single agent cannot handle alone
- **Promote Open Standards** - Foster a community-driven approach to agent communication
- **Preserve Opacity** - Allow agents to collaborate without sharing internal memory, proprietary logic, or specific tool implementations

### Key Features

| Feature | Description |
|---------|-------------|
| **Standardized Communication** | JSON-RPC 2.0 over HTTP(S) |
| **Agent Discovery** | Via "Agent Cards" detailing capabilities and connection info |
| **Flexible Interaction** | Supports synchronous request/response, streaming (SSE), and async push notifications |
| **Rich Data Exchange** | Handles text, files, and structured JSON data |
| **Enterprise-Ready** | Designed with security, authentication, and observability in mind |

---

## Repository Structure

```
a2a-openai-agent/
├── README.md                 # This file
├── a2a_single_agent/         # Single agent example
│   ├── README.md             # Single agent documentation
│   ├── pyproject.toml        # Dependencies
│   ├── app/cmd/              # CLI client
│   ├── my_agents/openai_sdk/ # TellTimeAgent implementation
│   ├── server/               # A2A server
│   ├── client/               # A2A client
│   └── models/               # Data models
│
└── a2a_multi_agent/          # Multi-agent example
    ├── README.md             # Multi-agent documentation
    ├── pyproject.toml        # Dependencies
    ├── app/cmd/              # CLI client
    ├── a2a_agents/           # Three collaborating agents
    │   ├── tell_time_agent/  # Returns current time
    │   ├── greeting_agent/   # Generates poetic greetings
    │   └── host_agent/       # Orchestrator that routes requests
    ├── server/               # A2A server
    ├── client/               # A2A client
    ├── models/               # Data models
    └── utilities/            # Agent discovery utilities
```

---

## Examples Overview

### 1. Single Agent (`a2a_single_agent/`)

A minimal A2A implementation with one agent:

| Component | Description |
|-----------|-------------|
| **TellTimeAgent** | Responds to time-related queries using the `get_current_time` tool |

**Use Case**: Learn the basics of A2A protocol, agent cards, JSON-RPC communication, and task lifecycle.

[View Single Agent README](a2a_single_agent/README.md)

---

### 2. Multi-Agent (`a2a_multi_agent/`)

A more advanced implementation with three collaborating agents:

| Agent | Port | Description |
|-------|------|-------------|
| **TellTimeAgent** | 10000 | Returns the current system time |
| **GreetingAgent** | 10001 | Fetches time and generates poetic greetings |
| **OrchestratorAgent** | 10002 | Routes requests to the appropriate child agent |

**Use Case**: Learn agent discovery, delegation, orchestration, and multi-agent collaboration.

[View Multi-Agent README](a2a_multi_agent/README.md)

---

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Clone the Repository

```bash
git clone https://github.com/MuhammadAbdullah95/a2a-openai-agent.git
cd a2a-openai-agent
```

### Run the Single Agent Example

```bash
cd a2a_single_agent

# Setup environment
uv venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# Add your API key
echo "OPENAI_API_KEY=your_key_here" > .env

# Terminal 1: Start the agent
python -m my_agents.openai_sdk

# Terminal 2: Run the client
python -m app.cmd.cmd --agent http://localhost:10002
```

### Run the Multi-Agent Example

```bash
cd a2a_multi_agent

# Setup environment
uv venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# Add your API key
echo "OPENAI_API_KEY=your_key_here" > .env

# Terminal 1: TellTimeAgent
python -m a2a_agents.tell_time_agent --host localhost --port 10000

# Terminal 2: GreetingAgent
python -m a2a_agents.greeting_agent --host localhost --port 10001

# Terminal 3: OrchestratorAgent
python -m a2a_agents.host_agent.entry --host localhost --port 10002

# Terminal 4: Client
python -m app.cmd.cmd --agent http://localhost:10002
```

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
| Python SDK | [a2a-python](https://github.com/a2aproject/a2a-python) - `pip install a2a-sdk` |
| Official Samples | [a2a-samples](https://github.com/a2aproject/a2a-samples) |

---

## Acknowledgements

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [OpenAI API](https://platform.openai.com/)
- [A2A Protocol](https://a2a-protocol.org)
- [Starlette](https://www.starlette.io/)
- [Uvicorn](https://www.uvicorn.org/)

---

## Connect with Me

- LinkedIn: [Muhammad Abdullah](https://www.linkedin.com/in/muhammad-abdullah-3a8550255/)
- Facebook: [Muhammad Abdullah](https://www.facebook.com/muhammad.abdullah.332635)
- GitHub: [Muhammad Abdullah](https://github.com/MuhammadAbdullah95)

---

## License

This project is open source and available for educational purposes.

---
