# A2A SDK Agent - TellTimeAgent with Streaming

A single-agent implementation using the **official [a2a-sdk](https://github.com/a2aproject/a2a-python)** Python package with the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/). Demonstrates streaming responses, multi-turn conversations, and the AgentExecutor pattern.

---

## What Makes This Different?

Unlike the basic examples that implement A2A from scratch, this project uses the **official `a2a-sdk` package** which provides:
- Built-in A2A server with `A2AStarletteApplication`
- `DefaultRequestHandler` for request routing
- `InMemoryTaskStore` for task state management
- `InMemoryPushNotifier` for push notifications
- Streaming via Server-Sent Events (SSE)

---

## Project Structure

```bash
agent_a2a_sdk/
├── .env                          # OPENAI_API_KEY (not committed)
├── pyproject.toml                # Dependencies (a2a-sdk, openai-agents, etc.)
├── main.py                       # Optional runner stub
├── my_agents/
│   └── tell_time_agent/
│       ├── __main__.py           # Agent server entry point (port 10000)
│       ├── agent.py              # TellTimeAgent with OpenAI Agents SDK
│       └── agent_executor.py     # Bridge between agent and A2A runtime
└── client/
    └── client.py                 # Async A2A SDK client with streaming
```

---

## Agent Details

| Property | Value |
|----------|-------|
| **Name** | TellTime Agent |
| **Model** | GPT-4o-mini |
| **Framework** | OpenAI Agents SDK |
| **Port** | 10000 |
| **Capabilities** | Streaming, Push Notifications |
| **Tool** | `get_time_now()` - returns current time (HH:MM:SS) |

---

## Features

- Official `a2a-sdk` (v0.2.4) integration
- OpenAI Agents SDK with GPT-4o-mini
- Real-time streaming responses via SSE
- Multi-turn conversation support
- AgentExecutor pattern (bridge between agent logic and A2A runtime)
- Push notification support
- Agent discovery via `/.well-known/agent.json`

---

## Setup

### 1. Navigate to this directory

```bash
cd agent_a2a_sdk
```

### 2. Create and activate a virtual environment

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
uv pip install -e .
```

### 4. Set your API key

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

---

## Running the Demo

**Terminal 1 - Start the Agent Server:**

```bash
uv run python -m my_agents.tell_time_agent
```

Server starts at `http://localhost:10000`

**Terminal 2 - Run the Client:**

```bash
uv run python client/client.py
```

---

## Try It Out

```
[>] Your query: What time is it?
=== Streaming Update ===
Looking up the current time...
=== Streaming Update ===
Processing the time result...
=== Streaming Update ===
The current time is 14:32:45
```

---

## How It Works

```
User Query
    ↓
[A2A Client] → sends SendStreamingMessageRequest
    ↓
[A2AStarletteApplication] → routes via DefaultRequestHandler
    ↓
[TellTimeAgentExecutor] → bridges A2A to agent
    ↓
[TellTimeAgent] → OpenAI Agents SDK (GPT-4o-mini)
    ├─ Detects tool need → calls get_time_now()
    ├─ Yields: "Looking up time..." (working)
    ├─ Yields: "Processing result..." (working)
    └─ Yields: Final answer (completed)
    ↓
[EventQueue] → streams TaskStatusUpdateEvents via SSE
    ↓
[A2A Client] → displays real-time updates
```

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **a2a-sdk** | Official Python SDK providing server, request handling, and task management |
| **AgentExecutor** | Bridge pattern connecting your agent logic to the A2A runtime |
| **Streaming** | Real-time updates via SSE as the agent processes |
| **Multi-turn** | Tasks maintain context for follow-up conversations |
| **Agent Card** | Published at `/.well-known/agent.json` for discovery |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `a2a-sdk==0.2.4` | Official A2A Protocol SDK |
| `openai-agents>=0.6.0` | OpenAI Agents SDK |
| `httpx>=0.28.1` | Async HTTP client |
| `click>=8.2.1` | CLI framework |
| `python-dotenv>=1.1.0` | Environment variable loader |
| `rich>=14.0.0` | Rich terminal output |
| `uvicorn>=0.34.2` | ASGI server |

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
