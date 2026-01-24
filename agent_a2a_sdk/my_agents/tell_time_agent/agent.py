# =============================================================================
# agents/tell_time_agent/agent.py
# =============================================================================
# Purpose:
# This file defines the TellTimeAgent.
# - It uses OpenAI Agents SDK with GPT-4o-mini
# - It supports streaming responses
# - It defines a simple tool: get_time_now()
# - It handles structured responses with support for multi-turn logic
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from datetime import datetime                      # To get the current system time
from typing import Any, AsyncIterable              # Type annotations for cleaner, safer code

from agents import Agent, Runner, function_tool, ItemHelpers  # OpenAI Agents SDK components

# -----------------------------------------------------------------------------
# Tool Definition: get_time_now()
# -----------------------------------------------------------------------------
@function_tool
def get_time_now() -> dict[str, str]:
    """Returns the current system time in HH:MM:SS format."""
    return {"current_time": datetime.now().strftime("%H:%M:%S")}

# -----------------------------------------------------------------------------
# TellTimeAgent Class Definition
# -----------------------------------------------------------------------------
class TellTimeAgent:
    """
    OpenAI Agents SDK agent that answers time-related queries.
    - Uses the get_time_now tool
    - Responds with streaming updates
    - Powered by GPT-4o-mini model
    """

    # Instruction given to the agent LLM
    SYSTEM_INSTRUCTION = (
        "You are a specialized assistant for time-related queries. "
        "Use the 'get_time_now' tool when users ask for the current time to get the time in HH:MM:SS format. "
        "Convert this time to the requested format by the user on your own. You are allowed to do that. "
        "Always provide a helpful, concise response."
    )

    # Declares formats this agent can handle for input/output
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        # Initialize the OpenAI Agent with GPT-4o-mini (fast, cost-effective)
        self.agent = Agent(
            name="TellTime Agent",
            instructions=self.SYSTEM_INSTRUCTION,
            model="gpt-4o-mini",
            tools=[get_time_now],
        )

    # -----------------------------------------------------------------------------
    # The `stream` method streams partial updates from the agent in real-time.
    # It returns responses step-by-step as the agent works, instead of waiting for everything at once.
    # -----------------------------------------------------------------------------

    async def stream(self, query: str, session_id: str) -> AsyncIterable[dict[str, Any]]:
        """
        This function is used when a user sends a message to the agent.
        Instead of waiting for a single response, it gives us updates as they happen.

        - 'query' is the user's question or command (e.g., "What time is it?")
        - 'session_id' is a unique ID for this user's interaction (to maintain context)
        - It yields updates such as "Looking up time...", "Processing...", and the final result.
        """

        # --------------------------------------------------------------
        # Start streaming the agent's response using Runner.run_streamed()
        # This returns a RunResultStreaming object that we can iterate over
        # --------------------------------------------------------------
        result = Runner.run_streamed(self.agent, input=query)

        # Track whether we've seen any events
        final_output = None

        # --------------------------------------------------------------
        # Process each streaming event as it arrives
        # Events include: tool calls, tool outputs, and final messages
        # --------------------------------------------------------------
        async for event in result.stream_events():
            # Skip raw response events (token-by-token), focus on higher-level events
            if event.type == "raw_response_event":
                continue

            # Handle run item stream events (tool calls, outputs, messages)
            if event.type == "run_item_stream_event":
                item = event.item

                # ----------------------------------------------------------
                # Tool call event: Agent is about to call the get_time_now tool
                # ----------------------------------------------------------
                if item.type == "tool_call_item":
                    yield {
                        "is_task_complete": False,
                        "require_user_input": False,
                        "content": "Looking up the current time...",
                    }

                # ----------------------------------------------------------
                # Tool output event: Agent received the result from the tool
                # ----------------------------------------------------------
                elif item.type == "tool_call_output_item":
                    yield {
                        "is_task_complete": False,
                        "require_user_input": False,
                        "content": "Processing the time result...",
                    }

                # ----------------------------------------------------------
                # Message output event: Agent has generated a final response
                # ----------------------------------------------------------
                elif item.type == "message_output_item":
                    text = ItemHelpers.text_message_output(item)
                    if text:
                        final_output = text

        # --------------------------------------------------------------
        # Yield the final response after all streaming events are processed
        # --------------------------------------------------------------
        if final_output:
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": final_output,
            }
        else:
            # Fallback if no output was captured
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": "Unable to process your request at the moment. Please try again.",
            }
