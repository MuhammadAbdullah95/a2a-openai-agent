# =============================================================================
# agents/host_agent/orchestrator.py
# =============================================================================
# 🎯 Purpose:
# Defines the OrchestratorAgent that uses an OpenAI Agent to interpret user
# queries and delegate them to any child A2A agent discovered at startup.
# Also defines OrchestratorTaskManager to expose this logic via JSON-RPC.
# =============================================================================

import uuid                         # For generating unique identifiers (e.g., session IDs)
import logging                      # Standard library for configurable logging
from typing import Dict, Any, List
from dotenv import load_dotenv      # Utility to load environment variables from a .env file

# Load the .env file so that environment variables like OPENAI_API_KEY
# are available to the agent
load_dotenv()

# -----------------------------------------------------------------------------
# OpenAI Agents SDK imports
# -----------------------------------------------------------------------------
from agents import Agent, Runner, function_tool

# -----------------------------------------------------------------------------
# A2A server-side infrastructure
# -----------------------------------------------------------------------------
from server.task_manager import InMemoryTaskManager
# InMemoryTaskManager: base class providing in-memory task storage and locking

from models.request import SendTaskRequest, SendTaskResponse
# Data models for incoming task requests and outgoing responses

from models.task import Message, TaskStatus, TaskState, TextPart
# Message: encapsulates role+parts; TaskStatus/State: status enums; TextPart: text payload

# -----------------------------------------------------------------------------
# Connector to child A2A agents
# -----------------------------------------------------------------------------
from a2a_agents.host_agent.agent_connect import AgentConnector
# AgentConnector: lightweight wrapper around A2AClient to call other agents

from models.agent import AgentCard
# AgentCard: metadata structure for agent discovery results

# Set up module-level logger for debug/info messages
logger = logging.getLogger(__name__)

# Global references for tools (will be initialized in OrchestratorAgent)
_connectors: Dict[str, AgentConnector] = {}


# -----------------------------------------------------------------------------
# 🛠️ Tool Functions (defined at module level for @function_tool decorator)
# -----------------------------------------------------------------------------

@function_tool
def list_agents() -> list[str]:
    """
    List all available child agent names.
    Returns a list of agent names that can be used with delegate_task.
    """
    global _connectors
    return list(_connectors.keys())


@function_tool
async def delegate_task(agent_name: str, message: str) -> str:
    """
    Delegate a task to a specific child agent.
    
    Args:
        agent_name: The name of the agent to delegate to
        message: The message/task to send to the agent
        
    Returns:
        The agent's response text
    """
    global _connectors
    
    if agent_name not in _connectors:
        raise ValueError(f"Unknown agent: {agent_name}")
    
    connector = _connectors[agent_name]
    session_id = str(uuid.uuid4())
    
    # Delegate task asynchronously and await Task result
    child_task = await connector.send_task(message, session_id)
    
    # Extract text from the last history entry if available
    if child_task.history and len(child_task.history) > 1:
        return child_task.history[-1].parts[0].text
    return ""


class OrchestratorAgent:
    """
    🤖 Uses an OpenAI Agent to route incoming user queries,
    calling out to any discovered child A2A agents via tools.
    """

    # Define supported MIME types for input/output
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, agent_cards: list[AgentCard]):
        """
        Initialize the OrchestratorAgent with discovered child agents.
        
        Args:
            agent_cards: List of AgentCard objects from discovery
        """
        global _connectors
        
        # Build one AgentConnector per discovered AgentCard
        _connectors.clear()
        for card in agent_cards:
            _connectors[card.name] = AgentConnector(card.name, card.url)

        # Build the internal agent with our custom tools and instructions
        self._agent = self._build_agent()

        # Static user ID for session tracking across calls
        self._user_id = "orchestrator_user"
        
        # 🗂️ In-memory session history storage: session_id -> list of messages
        self._sessions: Dict[str, List[Dict[str, Any]]] = {}

    def _build_agent(self) -> Agent:
        """
        Construct the OpenAI Agent with:
        - Model name
        - Agent name/description
        - System instruction
        - Available tool functions
        """
        # Build a bullet-list of agent names for the instruction
        agent_list = "\n".join(f"- {name}" for name in _connectors)
        
        instruction = (
            "You are an orchestrator agent with two tools:\n"
            "1) list_agents() -> list available child agents\n"
            "2) delegate_task(agent_name, message) -> call that agent\n\n"
            "Use these tools to satisfy the user's request. Do not hallucinate.\n\n"
            "Available agents:\n" + agent_list
        )
        
        return Agent(
            model="gpt-4o-mini",
            name="orchestrator_agent",
            instructions=instruction,
            tools=[list_agents, delegate_task],
        )

    async def invoke(self, query: str, session_id: str) -> str:
        """
        Main entry: receives a user query + session_id,
        runs the agent with tools enabled, and returns the final text.
        Maintains conversation history across calls.
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


class OrchestratorTaskManager(InMemoryTaskManager):
    """
    🪄 TaskManager wrapper: exposes OrchestratorAgent.invoke() over the
    A2A JSON-RPC `tasks/send` endpoint, handling in-memory storage and
    response formatting.
    """
    def __init__(self, agent: OrchestratorAgent):
        super().__init__()       # Initialize base in-memory storage
        self.agent = agent       # Store our orchestrator logic

    def _get_user_text(self, request: SendTaskRequest) -> str:
        """
        Helper: extract the user's raw input text from the request object.
        """
        return request.params.message.parts[0].text

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        Called by the A2A server when a new task arrives:
        1. Store the incoming user message
        2. Invoke the OrchestratorAgent to get a response
        3. Append response to history, mark completed
        4. Return a SendTaskResponse with the full Task
        """
        logger.info(f"OrchestratorTaskManager received task {request.params.id}")

        # Step 1: save the initial message
        task = await self.upsert_task(request.params)

        # Step 2: run orchestration logic
        user_text = self._get_user_text(request)
        response_text = await self.agent.invoke(user_text, request.params.sessionId)

        # Step 3: wrap the agent output into a Message
        reply = Message(role="agent", parts=[TextPart(text=response_text)])
        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(reply)

        # Step 4: return structured response
        return SendTaskResponse(id=request.id, result=task)
