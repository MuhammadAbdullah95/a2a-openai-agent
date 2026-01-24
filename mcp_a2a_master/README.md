# MCP + A2A Master - Multi-Framework Agent Orchestration

An advanced multi-agent system combining **MCP (Model Context Protocol)** and **A2A (Agent-to-Agent Protocol)** with three different agent frameworks: **OpenAI Agents SDK**, **Google ADK**, and **LangGraph**. Demonstrates real-world patterns for agent orchestration, tool discovery, and task delegation.

---

## Architecture Overview

```
                         ┌─────────────────────────┐
                         │      User (CLI)          │
                         └────────────┬────────────-┘
                                      │
                         ┌────────────▼─────────────┐
                         │    Host Agent (GPT-4o)    │
                         │    OpenAI Agents SDK      │
                         │    Port: 10001            │
                         └──┬────────────────────┬──┘
                            │                    │
              ┌─────────────▼──────┐    ┌───────▼──────────────┐
              │  A2A Delegation    │    │   MCP Tools           │
              └──┬──────────┬──────┘    │  (Terminal, FS, Math) │
                 │          │           └───────────────────────┘
    ┌────────────▼───┐  ┌──▼─────────────────┐
    │ Website Builder │  │  Content Writer     │
    │ Google ADK      │  │  LangGraph          │
    │ Gemini-2.5-Flash│  │  GPT-4o             │
    │ Port: 10000     │  │  Port: 10002        │
    └─────────────────┘  └────────────────────-┘
```

---

## Agents

| Agent | Framework | Model | Port | Description |
|-------|-----------|-------|------|-------------|
| **Host Agent** | OpenAI Agents SDK | GPT-4o | 10001 | Central orchestrator - routes tasks to agents or MCP tools |
| **Website Builder** | Google ADK | Gemini-2.5-Flash | 10000 | Generates complete single-file HTML pages with CSS/JS |
| **Content Writer** | LangGraph | GPT-4o | 10002 | Creates blog posts, articles, marketing copy and saves to files |

---

## MCP Servers

| Server | Transport | Tool | Description |
|--------|-----------|------|-------------|
| **Terminal Server** | stdio | `terminal_server` | Execute shell commands |
| **Filesystem Server** | stdio | `write_file`, `read_file`, `list_files` | File I/O operations |
| **Arithmetic Server** | streamable-http | `add_numbers` | Math operations (port 3000) |

---

## Project Structure

```bash
mcp_a2a_master/
├── .env                              # API keys (OPENAI_API_KEY, GOOGLE_API_KEY)
├── pyproject.toml                    # Dependencies
├── main.py                           # Entry point
├── my_agents/
│   ├── host_agent/                   # Central orchestrator
│   │   ├── __main__.py               # Server entry (port 10001)
│   │   ├── agent.py                  # GPT-4o agent with tools
│   │   ├── agent_executor.py         # A2A executor bridge
│   │   └── instructions.txt          # System prompt
│   ├── content_writer/               # Content generation agent
│   │   ├── __main__.py               # Server entry (port 10002)
│   │   ├── agent.py                  # LangGraph state machine
│   │   ├── agent_executor.py         # A2A executor bridge
│   │   └── instructions.txt          # System prompt
│   └── website_builder_simple/       # Website generation agent
│       ├── __main__.py               # Server entry (port 10000)
│       ├── agent.py                  # Google ADK LlmAgent
│       ├── agent_executor.py         # A2A executor bridge
│       └── instructions.txt          # System prompt
├── mcp/
│   └── servers/
│       ├── terminal_server/          # Shell command execution
│       │   └── terminal_server.py
│       ├── filesystem_server/        # File read/write/list
│       │   └── filesystem_server.py
│       └── streamable_http_server.py # HTTP-based arithmetic server
├── utilities/
│   ├── a2a/
│   │   ├── agent_discovery.py        # Fetches AgentCards from registry
│   │   ├── agent_connect.py          # Sends tasks to remote agents
│   │   └── agent_registry.json       # Agent URLs list
│   ├── mcp/
│   │   ├── mcp_discovery.py          # Discovers MCP servers from config
│   │   ├── mcp_connect.py            # Connects to MCP servers (stdio/http)
│   │   └── mcp_config.json           # MCP server definitions
│   ├── openai_mcp/
│   │   └── mcp_tool_bridge.py        # Converts MCP tools → OpenAI FunctionTools
│   └── common/
│       └── file_loader.py            # Loads instruction files
└── app/
    └── cmd/
        └── cmd.py                    # Interactive CLI client
```

---

## Features

- Multi-framework integration (OpenAI Agents SDK + Google ADK + LangGraph)
- Official `a2a-sdk` for agent communication
- MCP tool discovery and execution (stdio + streamable-http transports)
- MCP-to-OpenAI tool bridge (converts MCP schemas to FunctionTools)
- Dynamic agent discovery via Agent Cards
- LLM-powered routing decisions
- Streaming task updates
- Multi-turn session management
- Content generation with auto-save to filesystem

---

## Setup

### 1. Navigate to this directory

```bash
cd mcp_a2a_master
```

### 2. Create and activate a virtual environment

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
uv pip install -e .
```

### 4. Set your API keys

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
```

---

## Running the Demo

Open **five terminal windows** and start services in order:

**Terminal 1 - Start Arithmetic MCP Server (optional):**
```bash
uv run python -m mcp.servers.streamable_http_server
```

**Terminal 2 - Start Website Builder Agent:**
```bash
uv run python -m my_agents.website_builder_simple
```

**Terminal 3 - Start Content Writer Agent:**
```bash
uv run python -m my_agents.content_writer
```

**Terminal 4 - Start Host Agent:**
```bash
uv run python -m my_agents.host_agent
```

**Terminal 5 - Launch the CLI:**
```bash
uv run python -m app.cmd.cmd
```

---

## Try It Out

```bash
# Website generation (routes to Website Builder)
> Build me a landing page for a coffee shop

# Content writing (routes to Content Writer)
> Write a blog post about Python async programming

# Direct MCP tool usage
> Run the command "ls" in the terminal

# Time-based query
> What files are in the workspace?
```

---

## How It Works

### Task Delegation Flow

1. **User** sends a query via CLI to Host Agent
2. **Host Agent** (GPT-4o) analyzes the query and decides:
   - Call `list_agents()` to see available agents
   - Call `delegate_task(agent_name, message)` to forward to a specialist
   - Use an MCP tool directly (terminal, filesystem, arithmetic)
3. **Specialist Agent** processes the task:
   - Website Builder generates HTML using Gemini
   - Content Writer creates content via LangGraph and optionally saves to file
4. **Response** flows back through A2A protocol to the user

### Discovery Mechanisms

- **A2A Discovery**: Host Agent reads `agent_registry.json` and fetches `/.well-known/agent.json` from each agent
- **MCP Discovery**: Host Agent reads `mcp_config.json` and connects to configured MCP servers
- **Tool Bridge**: `MCPToolBridge` converts MCP tool schemas into OpenAI-compatible `FunctionTool` objects

---

## Key Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| **Agent Orchestration** | Host Agent as central coordinator |
| **Multi-Framework** | OpenAI + Google ADK + LangGraph in one system |
| **Protocol Bridging** | MCP tools exposed as A2A-compatible function tools |
| **Service Discovery** | Registry-based + `.well-known/agent.json` |
| **State Graphs** | LangGraph for complex content generation workflows |
| **Transport Modes** | stdio (local servers) + streamable-http (remote) |
| **Streaming** | Real-time updates via SSE during task execution |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `a2a-sdk>=0.2.15` | A2A Protocol SDK |
| `openai-agents>=0.0.7` | OpenAI Agents SDK (Host Agent) |
| `google-adk>=1.7.0` | Google Agent Development Kit (Website Builder) |
| `mcp[cli]>=1.12.0` | Model Context Protocol |
| `langgraph>=0.2.0` | LangGraph (Content Writer) |
| `langchain-openai>=0.2.0` | LangChain OpenAI integration |
| `asyncclick>=8.1.8` | Async CLI framework |
| `python-dotenv>=1.0.0` | Environment variable loader |

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
