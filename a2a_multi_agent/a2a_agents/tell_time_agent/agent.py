# =============================================================================
# agents/tell_time_agent/agent.py
# =============================================================================
# 🎯 Purpose:
# This file defines a simple AI agent called TellTimeAgent.
# It uses the OpenAI Agents SDK to respond with the current time.
# =============================================================================


# -----------------------------------------------------------------------------
# 📦 Built-in & External Library Imports
# -----------------------------------------------------------------------------

from datetime import datetime  # Used to get the current system time
from typing import Dict, Any, List

# 🧠 OpenAI Agents SDK imports
from agents import Agent, Runner, function_tool

# 🔐 Load environment variables (like API keys) from a `.env` file
from dotenv import load_dotenv
load_dotenv()  # Load variables like OPENAI_API_KEY into the system


# -----------------------------------------------------------------------------
# 🕒 TellTimeAgent: Your AI agent that tells the time
# -----------------------------------------------------------------------------

class TellTimeAgent:
    """
    🕒 A simple agent that tells the current time using OpenAI Agents SDK.
    Maintains session history for multi-turn conversations.
    """
    
    # This agent only supports plain text input/output
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """
        👷 Initialize the TellTimeAgent:
        - Creates the OpenAI Agent
        - Sets up session history storage for conversation memory
        """
        self._agent = self._build_agent()
        
        # 🗂️ In-memory session history storage: session_id -> list of messages
        self._sessions: Dict[str, List[Dict[str, Any]]] = {}

    def _build_agent(self) -> Agent:
        """
        ⚙️ Creates and returns an OpenAI Agent with basic settings.

        Returns:
            Agent: An agent object from OpenAI Agents SDK
        """
        return Agent(
            model="gpt-4o-mini",                          # OpenAI model version
            name="tell_time_agent",                       # Name of the agent
            instructions=(
                "You are a time-telling agent. When asked about the time, "
                "reply with the current time in the format YYYY-MM-DD HH:MM:SS. "
                "The current time is provided to you via the get_current_time tool."
            ),
            tools=[get_current_time]                      # Available tools
        )

    async def invoke(self, query: str, session_id: str) -> str:
        """
        📥 Handle a user query and return a response string.
        Manages conversation history for multi-turn sessions.

        Args:
            query (str): What the user said (e.g., "what time is it?")
            session_id (str): Helps group messages into a session

        Returns:
            str: Agent's reply (usually the current time)
        """
        # 🔄 Get or create session history for this session_id
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        session_history = self._sessions[session_id]
        
        # 📥 Build input: previous history + new user message
        if session_history:
            # Append new user message to existing history
            input_messages = session_history + [{"role": "user", "content": query}]
        else:
            # First message in session
            input_messages = query
        
        # 🚀 Run the agent
        result = await Runner.run(self._agent, input_messages)
        
        # 💾 Update session history with the new conversation
        # to_input_list() gives us all messages including tool calls
        self._sessions[session_id] = result.to_input_list()
        
        # 📤 Return the final output
        return result.final_output if result.final_output else ""


    async def stream(self, query: str, session_id: str):
        """
        🌀 Simulates a "streaming" agent that returns a single reply.
        This is here just to demonstrate that streaming is possible.

        Yields:
            dict: Response payload that says the task is complete and gives the time
        """
        yield {
            "is_task_complete": True,
            "content": f"The current time is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }


# -----------------------------------------------------------------------------
# 🛠️ Tool: Get Current Time
# -----------------------------------------------------------------------------

@function_tool
def get_current_time() -> str:
    """
    Get the current system time.
    
    Returns:
        The current time in YYYY-MM-DD HH:MM:SS format.
    """
    return f"The current time is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
