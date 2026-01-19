# =============================================================================
# agents/google_adk/agent.py
# =============================================================================
# 🎯 Purpose:
# This file defines a simple AI agent called TellTimeAgent.
# It uses OpenAI's Agents SDK to respond with the current time.
# 
# MIGRATED FROM: Google ADK + Gemini
# MIGRATED TO: OpenAI Agents SDK
# =============================================================================


# -----------------------------------------------------------------------------
# 📦 Built-in & External Library Imports
# -----------------------------------------------------------------------------

from datetime import datetime
import traceback

# 🧠 OpenAI Agents SDK - Agent and Runner
from agents import Agent, Runner, function_tool

# 🔐 Load environment variables (like API keys) from a `.env` file
from dotenv import load_dotenv
load_dotenv()  # Load variables like OPENAI_API_KEY into the system


# -----------------------------------------------------------------------------
# 🕒 TellTimeAgent: Your AI agent that tells the time
# -----------------------------------------------------------------------------


@function_tool
def get_current_time():
    """Returns the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class TellTimeAgent:
    # This agent only supports plain text input/output
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """
        👷 Initialize the TellTimeAgent:
        - Creates the Agent using OpenAI Agents SDK
        """
        self._agent = self._build_agent()

    def _build_agent(self) -> Agent:
        """
        ⚙️ Creates and returns an OpenAI Agent.

        Returns:
            Agent: An agent object from OpenAI Agents SDK
        """
        return Agent(
            name="tell_time_agent",
            instructions="You are a helpful assistant that tells the current time. Reply with the current time in the format YYYY-MM-DD HH:MM:SS when asked about time.",
            model="gpt-4o-mini",  # Using OpenAI's efficient model
            tools=[get_current_time]
        )

    async def invoke(self, query: str, session_id: str) -> str:
        """
        📥 Handle a user query and return a response string.

        Args:
            query (str): What the user said (e.g., "what time is it?")
            session_id (str): Session identifier (not used in basic OpenAI SDK)

        Returns:
            str: Agent's reply (usually the current time)
        """
        try:
            # 🚀 Run the agent using OpenAI's Runner
            result = await Runner.run(
                self._agent,
                query
            )

            # 📤 Return the final output from the agent
            return result.final_output if result.final_output else ""

        except Exception as e:
            # Print a user-friendly error message
            print(f"🔥🔥🔥 An error occurred in TellTimeAgent.invoke: {e}")

            # Print the full, detailed stack trace to the console
            traceback.print_exc()

            # Return a helpful error message to the user/client
            return "Sorry, I encountered an internal error and couldn't process your request."

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
