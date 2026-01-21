# =============================================================================
# agents/greeting_agent/agent.py
# =============================================================================
# 🎯 Purpose:
#   A composite "orchestrator" agent that:
#     1) Discovers all registered A2A agents via DiscoveryClient
#     2) Invokes the TellTimeAgent to fetch the current time
#     3) Generates a 2–3 line poetic greeting referencing that time
# =============================================================================

import logging                              # Built-in module to log info, warnings, errors
from typing import Dict, Any, List
from dotenv import load_dotenv              # For loading environment variables from a .env file

load_dotenv()  # Read .env in project root so that OPENAI_API_KEY is set

# OpenAI Agents SDK imports
from agents import Agent, Runner, function_tool

# Utilities we wrote for agent discovery and HTTP connection:
from utilities.discovery import DiscoveryClient
from a2a_agents.host_agent.agent_connect import AgentConnector

# Create a module-level logger using this file's name
logger = logging.getLogger(__name__)

# Global references for tools (will be initialized in GreetingAgent)
_discovery_client: DiscoveryClient = None
_connectors: Dict[str, AgentConnector] = {}


# -----------------------------------------------------------------------------
# 🛠️ Tool Functions (defined at module level for @function_tool decorator)
# -----------------------------------------------------------------------------

@function_tool
async def list_agents() -> list[dict]:
    """
    Fetch all AgentCard metadata from the registry.
    Returns a list of agent information dictionaries.
    """
    global _discovery_client
    if _discovery_client is None:
        _discovery_client = DiscoveryClient()
    
    cards = await _discovery_client.list_agent_cards()
    return [card.model_dump(exclude_none=True) for card in cards]


@function_tool
async def call_agent(agent_name: str, message: str) -> str:
    """
    Call a specific agent with a message and get its response.
    
    Args:
        agent_name: The name of the agent to call (e.g., 'TellTimeAgent')
        message: The message to send to the agent
        
    Returns:
        The agent's response text
    """
    global _discovery_client, _connectors
    
    if _discovery_client is None:
        _discovery_client = DiscoveryClient()
    
    # Re-fetch registry to catch new agents dynamically
    cards = await _discovery_client.list_agent_cards()
    
    # Try to match exactly by name (case-insensitive)
    matched = next(
        (c for c in cards
         if c.name.lower() == agent_name.lower()
         or getattr(c, "id", "").lower() == agent_name.lower()),
        None
    )

    # Fallback: substring match if no exact found
    if not matched:
        matched = next(
            (c for c in cards if agent_name.lower() in c.name.lower()),
            None
        )

    # If still nothing, error out
    if not matched:
        raise ValueError(f"Agent '{agent_name}' not found.")

    # Use Pydantic model's name field as key
    key = matched.name
    
    # If we haven't built a connector yet, create and cache one
    if key not in _connectors:
        _connectors[key] = AgentConnector(
            name=matched.name,
            base_url=matched.url
        )
    connector = _connectors[key]

    # Use a static session for simplicity
    session_id = "greeting_session"

    # Delegate the task and wait for the full Task object
    task = await connector.send_task(message, session_id=session_id)

    # Pull the final agent reply out of the history
    if task.history and task.history[-1].parts:
        return task.history[-1].parts[0].text

    return ""


class GreetingAgent:
    """
    🧠 Orchestrator "meta-agent" that:
      - Provides two LLM tools: list_agents() and call_agent(...)
      - On a "greet me" request:
          1) Calls list_agents() to see which agents are up
          2) Calls call_agent("TellTimeAgent", "What is the current time?")
          3) Crafts a 2–3 line poetic greeting referencing that time
    """

    # Declare which content types this agent accepts by default
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """
        🏗️ Constructor: build the internal orchestrator agent.
        """
        # Initialize global discovery client
        global _discovery_client
        _discovery_client = DiscoveryClient()
        
        # Build the agent with its tools and system instruction
        self._agent = self._build_agent()

        # A fixed user_id to group all greeting calls into one session
        self.user_id = "greeting_user"
        
        # 🗂️ In-memory session history storage: session_id -> list of messages
        self._sessions: Dict[str, List[Dict[str, Any]]] = {}

    def _build_agent(self) -> Agent:
        """
        🔧 Internal: define the agent, its system instruction, and tools.
        """
        system_instr = (
            "You are a poetic greeting agent. You have two tools:\n"
            "1) list_agents() → returns metadata for all available agents.\n"
            "2) call_agent(agent_name: str, message: str) → fetches a reply from that agent.\n\n"
            "When asked to greet, first call list_agents() to discover available agents, then "
            "call_agent('TellTimeAgent', 'What is the current time?') to get the current time, "
            "then craft a 2–3 line poetic greeting referencing that time.\n\n"
            "Be creative and poetic in your greetings!"
        )

        return Agent(
            model="gpt-4o-mini",
            name="greeting_orchestrator",
            instructions=system_instr,
            tools=[list_agents, call_agent],
        )

    async def invoke(self, query: str, session_id: str) -> str:
        """
        🔄 Public: send a user query through the orchestrator agent pipeline,
        ensuring session reuse or creation, and return the final text reply.
        """
        # 🔄 Get or create session history for this session_id
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        session_history = self._sessions[session_id]
        
        # 📥 Build input: previous history + new user message
        if session_history:
            input_messages = session_history + [{"role": "user", "content": query}]
        else:
            input_messages = query
        
        # 🚀 Run the agent
        result = await Runner.run(self._agent, input_messages)
        
        # 💾 Update session history with the new conversation
        self._sessions[session_id] = result.to_input_list()
        
        # 📤 Return the final output
        return result.final_output if result.final_output else ""
