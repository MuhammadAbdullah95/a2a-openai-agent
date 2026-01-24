from collections.abc import AsyncIterable
import json
from typing import Any
from uuid import uuid4

from pydantic import BaseModel

from agents import Agent, Runner, FunctionTool
from agents.run_context import RunContextWrapper

from utilities.a2a.agent_connect import AgentConnector
from utilities.a2a.agent_discovery import AgentDiscovery
from utilities.common.file_loader import load_instructions_file
from utilities.openai_mcp.mcp_tool_bridge import MCPToolBridge

from rich import print as rprint

from dotenv import load_dotenv
load_dotenv()


class ListAgentsArgs(BaseModel):
    pass


class DelegateTaskArgs(BaseModel):
    agent_name: str
    message: str


class HostAgent:
    """
    Orchestrator agent using OpenAI Agents SDK (GPT-4o).
    - Discovers A2A agents via agent discovery
    - Discovers MCP servers via MCPToolBridge and loads tools
    - Routes user queries by picking the correct agent/tool
    """

    def __init__(self):
        self.system_instruction = load_instructions_file("my_agents/host_agent/instructions.txt")
        self.description = load_instructions_file("my_agents/host_agent/description.txt")

        self.mcp_bridge = MCPToolBridge()
        self.agent_discovery = AgentDiscovery()

        self._agent = None
        self._sessions: dict[str, list[dict]] = {}

    async def create(self):
        mcp_tools = await self.mcp_bridge.get_tools()

        list_agents_schema = ListAgentsArgs.model_json_schema()
        list_agents_schema["additionalProperties"] = False

        delegate_task_schema = DelegateTaskArgs.model_json_schema()
        delegate_task_schema["additionalProperties"] = False
        delegate_task_schema["required"] = list(delegate_task_schema.get("properties", {}).keys())

        list_agents_tool = FunctionTool(
            name="list_agents",
            description="List all available A2A agents and their capabilities. "
                        "Call this to discover which agents are available for delegation.",
            params_json_schema=list_agents_schema,
            on_invoke_tool=self._on_list_agents,
        )

        delegate_task_tool = FunctionTool(
            name="delegate_task",
            description="Delegate a task to a specific A2A agent by name. "
                        "Use list_agents first to find available agents.",
            params_json_schema=delegate_task_schema,
            on_invoke_tool=self._on_delegate_task,
        )

        self._agent = Agent(
            name="host_agent",
            model="gpt-4o",
            instructions=self.system_instruction,
            tools=[list_agents_tool, delegate_task_tool, *mcp_tools],
        )

    async def _on_list_agents(self, ctx: RunContextWrapper[Any], args_json: str) -> str:
        cards = await self.agent_discovery.list_agent_cards()
        result = []
        for card in cards:
            result.append({
                "name": card.name,
                "description": card.description,
                "url": card.url,
                "skills": [
                    {"name": s.name, "description": s.description}
                    for s in (card.skills or [])
                ],
            })
        return json.dumps(result, indent=2)

    async def _on_delegate_task(self, ctx: RunContextWrapper[Any], args_json: str) -> str:
        parsed = DelegateTaskArgs.model_validate_json(args_json)
        cards = await self.agent_discovery.list_agent_cards()

        matched_card = None
        for card in cards:
            if card.name.lower() == parsed.agent_name.lower():
                matched_card = card
                break
            elif getattr(card, "id", "").lower() == parsed.agent_name.lower():
                matched_card = card
                break

        if matched_card is None:
            return f"Agent '{parsed.agent_name}' not found. Use list_agents to see available agents."

        connector = AgentConnector(agent_card=matched_card)
        return await connector.send_task(message=parsed.message, session_id=str(uuid4()))

    async def invoke(self, query: str, session_id: str) -> AsyncIterable[dict]:
        """
        Invoke the agent and yield status updates.

        Yields:
            dict with 'is_task_complete' (bool), 'updates' or 'content' (str)
        """
        # Maintain session history
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        self._sessions[session_id].append({
            "role": "user",
            "content": query,
        })

        yield {
            'is_task_complete': False,
            'updates': "Agent is processing your request..."
        }

        try:
            result = await Runner.run(
                self._agent,
                input=self._sessions[session_id],
            )

            final_output = result.final_output or "No response generated."

            # Store assistant response in session
            self._sessions[session_id].append({
                "role": "assistant",
                "content": final_output,
            })

            rprint(f"[bold green]Host Agent final output:[/bold green] {final_output[:200]}")

            yield {
                'is_task_complete': True,
                'content': final_output,
            }
        except Exception as e:
            error_msg = f"Error running host agent: {str(e)}"
            rprint(f"[bold red]{error_msg}[/bold red]")
            yield {
                'is_task_complete': True,
                'content': error_msg,
            }
