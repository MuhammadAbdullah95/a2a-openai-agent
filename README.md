# 🤖 TellTimeAgent - A2A Agent Using OpenAI Agents SDK

## 🌐 What is A2A (Agent-to-Agent) Protocol?

The **Agent2Agent (A2A) Protocol** is an **open protocol** that enables communication and interoperability between AI agents built on different frameworks by different companies. It was initiated by **Google** and is now maintained as an open-source project under the **Linux Foundation**.

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

### 📚 Official Resources

| Resource | Link |
|----------|------|
| 🌐 Official Documentation | [a2a-protocol.org](https://a2a-protocol.org) |
| 📝 Protocol Specification | [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/) |
| 🐙 GitHub Repository | [github.com/a2aproject/A2A](https://github.com/a2aproject/A2A) |
| 🐍 Python SDK | [a2a-python](https://github.com/a2aproject/a2a-python) - `pip install a2a-sdk` |
| 🎬 Official Samples | [a2a-samples](https://github.com/a2aproject/a2a-samples) |

---

## 📦 Project Structure

```bash
a2a_openai_agent/
├── .env                       # API key goes here (not committed)
├── pyproject.toml            # Dependency config (used with uv or pip)
├── README.md                 # You're reading it!
├── app/
│   └── cmd/
│       └── cmd.py            # Command-line app to talk to the agent
├── my_agents/
│   └── openai_sdk/
│       ├── __main__.py       # Starts the agent + A2A server
│       ├── agent.py          # OpenAI agent definition using Agents SDK
│       └── task_manager.py   # Handles task lifecycle
├── server/
│   ├── server.py             # A2A server logic (routes, JSON-RPC)
│   └── task_manager.py       # In-memory task storage + interface
├── client/
│   └── client.py             # A2A client for sending requests
└── models/
    ├── agent.py              # AgentCard, AgentSkill, AgentCapabilities
    ├── json_rpc.py           # JSON-RPC request/response formats
    ├── request.py            # SendTaskRequest, A2ARequest union
    └── task.py               # Task structure, messages, status
```

---

## 🚀 Features

✅ OpenAI-powered A2A agent using Agents SDK  
✅ Follows JSON-RPC 2.0 specification  
✅ Supports session handling  
✅ Custom A2A server implementation (non-streaming)  
✅ CLI to interact with agent  
✅ Function tools support  
✅ Fully commented and beginner-friendly

---

## 💠 Setup

### 1. Clone and navigate to the repo

```bash
git clone https://github.com/MuhammadAbdullah95/a2a-openai-agent.git
cd a2a_openai_agent
```

### 2. Setup with `uv` (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager. Install it first:

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then create a virtual environment and install dependencies:

```bash
# Create virtual environment
uv venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### Alternative: Setup with `pip`

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -e .
```

---

## 🔑 API Key Setup

Create a `.env` file in the root directory:

```bash
touch .env
```

And add your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```

---

## ▶️ Running the Agent

In one terminal window:

```bash
python -m my_agents.openai_sdk
```

You should see:

```
Uvicorn running on http://localhost:10002
```

---

## 🧑‍💻 Running the Client

Open a **second terminal window**:

```bash
python -m app.cmd.cmd --agent http://localhost:10002
```

You can now type messages like:

```bash
what time is it?
```

And get an OpenAI-powered response!

---

## 🔍 Agent Workflow (A2A Lifecycle)

1. The client queries the agent using a CLI (`cmd.py`)
2. The A2A client sends a task using JSON-RPC to the A2A server
3. The server parses the request, invokes the task manager
4. The task manager calls the OpenAI-powered `TellTimeAgent`
5. The agent uses the `get_current_time` tool to get the system time
6. The server wraps the response and sends it back to the client

---

## 🛠️ Tech Stack

- **OpenAI Agents SDK** - Agent orchestration and tool calling
- **Starlette** - Lightweight ASGI web framework
- **Uvicorn** - ASGI web server
- **httpx** - Async HTTP client
- **Pydantic** - Data validation

---

## 🙌 Acknowledgements

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [OpenAI API](https://platform.openai.com/)
- [Starlette](https://www.starlette.io/)
- [Uvicorn](https://www.uvicorn.org/)

---

## 🌐 Connect with Me

- [Linkedin: Muhammad Abdullah](https://www.linkedin.com/in/muhammad-abdullah-3a8550255/)
- Facebook: [Muhammad Abdullah](https://www.facebook.com/muhammad.abdullah.332635)
- GitHub: [Muhammad Abdullah](https://github.com/MuhammadAbdullah95)

---