# A2A Protocol - From Basics to Advanced Multi-Agent Systems

A progressive collection of **Agent2Agent (A2A) Protocol** implementations — from a single agent to a full multi-framework orchestration system with MCP integration. Each folder builds on the previous, providing a complete learning path for building interoperable AI agents.

---

## What is A2A (Agent-to-Agent) Protocol?

The **Agent2Agent (A2A) Protocol** is an open protocol that enables communication and interoperability between AI agents built on different frameworks by different companies. It was initiated by **Google** and is now maintained as an open-source project under the **Linux Foundation**.

### Why A2A?

As AI agents become more prevalent, their ability to interoperate is crucial for building complex, multi-functional applications. A2A aims to:

- **Break Down Silos** - Connect agents across different ecosystems
- **Enable Complex Collaboration** - Allow specialized agents to work together on tasks that a single agent cannot handle alone
- **Promote Open Standards** - Foster a community-driven approach to agent communication
- **Preserve Opacity** - Allow agents to collaborate without sharing internal memory, proprietary logic, or specific tool implementations

### Key Features of the Protocol

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
│
├── a2a_single_agent/         # 1. Single agent (A2A from scratch)
│   ├── my_agents/openai_sdk/ #    TellTimeAgent
│   ├── server/               #    Custom A2A server
│   ├── client/               #    A2A client
│   └── models/               #    JSON-RPC models
│
├── a2a_multi_agent/          # 2. Multi-agent (A2A from scratch)
│   ├── a2a_agents/           #    TellTime + Greeting + Orchestrator
│   ├── server/               #    Custom A2A server
│   ├── client/               #    A2A client
│   └── utilities/            #    Agent discovery
│
├── agent_a2a_sdk/            # 3. Official a2a-sdk integration
│   ├── my_agents/            #    TellTimeAgent with streaming
│   └── client/               #    SDK-based async client
│
└── mcp_a2a_master/           # 4. MCP + A2A multi-framework
    ├── my_agents/            #    Host + Content Writer + Website Builder
    ├── mcp/servers/          #    Terminal, Filesystem, HTTP servers
    └── utilities/            #    A2A + MCP discovery & bridging
```

---

## Examples Overview (Progressive Difficulty)

### 1. Single Agent - `a2a_single_agent/`

> **Difficulty:** Beginner | **Framework:** OpenAI Agents SDK

A minimal A2A implementation built from scratch — no SDK, just raw JSON-RPC 2.0 communication.

| Component | Description |
|-----------|-------------|
| **TellTimeAgent** | Responds to time queries using `get_current_time` tool |

**You'll learn:** Agent Cards, JSON-RPC, task lifecycle, A2A server basics.

[View README](a2a_single_agent/README.md)

---

### 2. Multi-Agent - `a2a_multi_agent/`

> **Difficulty:** Intermediate | **Framework:** OpenAI Agents SDK

Three agents collaborating with discovery and delegation — still from scratch.

| Agent | Port | Description |
|-------|------|-------------|
| **TellTimeAgent** | 10000 | Returns current time |
| **GreetingAgent** | 10001 | Generates poetic greetings (calls TellTimeAgent) |
| **OrchestratorAgent** | 10002 | LLM-powered request routing |

**You'll learn:** Agent discovery, delegation, orchestration patterns.

[View README](a2a_multi_agent/README.md)

---

### 3. A2A SDK Agent - `agent_a2a_sdk/`

> **Difficulty:** Intermediate | **Framework:** OpenAI Agents SDK + Official a2a-sdk

Uses the **official `a2a-sdk`** Python package instead of custom implementation.

| Component | Description |
|-----------|-------------|
| **TellTimeAgent** | Streaming agent with SSE + push notifications |
| **A2A Client** | SDK-based async client with multi-turn support |

**You'll learn:** Official SDK usage, AgentExecutor pattern, streaming, SSE.

[View README](agent_a2a_sdk/README.md)

---

### 4. MCP + A2A Master - `mcp_a2a_master/`

> **Difficulty:** Advanced | **Frameworks:** OpenAI Agents SDK + Google ADK + LangGraph

Production-grade multi-agent system combining MCP and A2A with three different agent frameworks.

| Agent | Framework | Model | Port |
|-------|-----------|-------|------|
| **Host Agent** | OpenAI Agents SDK | GPT-4o | 10001 |
| **Website Builder** | Google ADK | Gemini-2.5-Flash | 10000 |
| **Content Writer** | LangGraph | GPT-4o | 10002 |

**MCP Servers:** Terminal, Filesystem, Arithmetic (stdio + streamable-http)

**You'll learn:** Multi-framework orchestration, MCP-to-A2A bridging, tool discovery, state graphs.

[View README](mcp_a2a_master/README.md)

---

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended)
- API keys: OpenAI (all examples), Google (mcp_a2a_master)

### Clone the Repository

```bash
git clone https://github.com/MuhammadAbdullah95/a2a-openai-agent.git
cd a2a-openai-agent
```

### Run Any Example

Each folder is self-contained with its own `pyproject.toml`:

```bash
cd <example_folder>
uv venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
echo "OPENAI_API_KEY=your_key" > .env
```

Then follow the specific README for running agents and clients.

---

## Tech Stack

| Technology | Used In | Purpose |
|-----------|---------|---------|
| **OpenAI Agents SDK** | All examples | Agent orchestration and tool calling |
| **a2a-sdk** | agent_a2a_sdk, mcp_a2a_master | Official A2A Protocol SDK |
| **Google ADK** | mcp_a2a_master | Website builder agent |
| **LangGraph** | mcp_a2a_master | Content writer state machine |
| **MCP** | mcp_a2a_master | Tool discovery and execution |
| **Starlette** | All examples | ASGI web framework |
| **Uvicorn** | All examples | ASGI web server |
| **httpx** | All examples | Async HTTP client |
| **Pydantic** | All examples | Data validation |

---

## Learning Path

```
Start Here
    │
    ▼
┌─────────────────────┐
│  1. a2a_single_agent │  ← Understand A2A basics
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. a2a_multi_agent  │  ← Learn agent collaboration
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. agent_a2a_sdk    │  ← Use official SDK + streaming
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. mcp_a2a_master   │  ← Multi-framework + MCP integration
└─────────────────────┘
```

---

## A2A Protocol Resources

| Resource | Link |
|----------|------|
| Official Documentation | [a2a-protocol.org](https://a2a-protocol.org) |
| Protocol Specification | [A2A Specification](https://a2a-protocol.org/latest/specification/) |
| GitHub Repository | [github.com/a2aproject/A2A](https://github.com/a2aproject/A2A) |
| Python SDK | [a2a-python](https://github.com/a2aproject/a2a-python) |
| Official Samples | [a2a-samples](https://github.com/a2aproject/a2a-samples) |

---

## Acknowledgements

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [A2A Protocol](https://a2a-protocol.org)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

---

## Connect with Me

- LinkedIn: [Muhammad Abdullah](https://www.linkedin.com/in/muhammad-abdullah-3a8550255/)
- Facebook: [Muhammad Abdullah](https://www.facebook.com/muhammad.abdullah.332635)
- GitHub: [Muhammad Abdullah](https://github.com/MuhammadAbdullah95)

---

## License

This project is open source and available for educational purposes.

---
