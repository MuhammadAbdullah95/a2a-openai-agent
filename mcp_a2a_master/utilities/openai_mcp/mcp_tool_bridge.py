import asyncio
import json
from typing import Any
from contextlib import AsyncExitStack

import httpx

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client

from agents import FunctionTool
from agents.run_context import RunContextWrapper

from utilities.mcp.mcp_discovery import MCPDiscovery
from rich import print as rprint


class MCPToolBridge:
    """
    Bridges MCP server tools to OpenAI Agents SDK FunctionTool objects.

    Connects to MCP servers (stdio or streamable-http), enumerates their tools,
    and creates FunctionTool instances that the OpenAI Agents SDK can use.
    """

    def __init__(self, config_file: str = None):
        self.discovery = MCPDiscovery(config_file=config_file)
        self._exit_stack = AsyncExitStack()
        self._sessions: list[ClientSession] = []
        self._tools: list[FunctionTool] = []

    async def get_tools(self) -> list[FunctionTool]:
        """
        Connect to all configured MCP servers and return their tools
        as OpenAI Agents SDK FunctionTool objects.
        """
        servers = self.discovery.list_servers()

        for name, server_config in servers.items():
            try:
                session = await self._connect_server(name, server_config)
                if session:
                    self._sessions.append(session)
                    tools = await self._create_tools_from_session(name, session)
                    self._tools.extend(tools)
            except Exception as e:
                rprint(f"[bold red]Error loading tools from MCP server '{name}': {e} (skipping)[/bold red]")

        return self._tools.copy()

    async def _check_http_reachable(self, url: str) -> bool:
        """Quick check if an HTTP URL is reachable."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                await client.get(url)
            return True
        except Exception:
            return False

    async def _connect_server(self, name: str, config: dict) -> ClientSession | None:
        """
        Connect to a single MCP server and return its ClientSession.
        """
        if config.get("command") == "streamable_http":
            url = config["args"][0]

            # Pre-check HTTP reachability to avoid anyio cancel scope pollution
            if not await self._check_http_reachable(url):
                rprint(f"[bold yellow]MCP server '{name}' at {url} is not reachable (skipping)[/bold yellow]")
                return None

            transport = await self._exit_stack.enter_async_context(
                streamablehttp_client(url=url)
            )
        else:
            server_params = StdioServerParameters(
                command=config["command"],
                args=config.get("args", [])
            )
            transport = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )

        read_stream, write_stream = transport[0], transport[1]
        session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await session.initialize()

        rprint(f"[bold green]Connected to MCP server '[cyan]{name}[/cyan]'[/bold green]")
        return session

    async def _create_tools_from_session(
        self, server_name: str, session: ClientSession
    ) -> list[FunctionTool]:
        """
        Enumerate tools from an MCP session and create FunctionTool objects.
        """
        tools_result = await session.list_tools()
        function_tools = []

        for tool_def in tools_result.tools:
            tool_name = tool_def.name
            tool_description = tool_def.description or f"MCP tool: {tool_name}"
            input_schema = tool_def.inputSchema or {"type": "object", "properties": {}}

            # Ensure schema is strict-compatible for OpenAI
            schema = self._make_strict_schema(input_schema)

            fn_tool = self._make_function_tool(
                tool_name=tool_name,
                tool_description=tool_description,
                schema=schema,
                session=session,
            )
            function_tools.append(fn_tool)

        tool_names = [t.name for t in function_tools]
        if tool_names:
            rprint(
                f"[bold green]Loaded tools from '[cyan]{server_name}[/cyan]': "
                f"{', '.join(tool_names)}[/bold green]"
            )

        return function_tools

    def _make_function_tool(
        self,
        tool_name: str,
        tool_description: str,
        schema: dict,
        session: ClientSession,
    ) -> FunctionTool:
        """
        Create a single FunctionTool that invokes the MCP tool via the session.
        """

        async def on_invoke_tool(ctx: RunContextWrapper[Any], args_json: str) -> str:
            try:
                args = json.loads(args_json) if args_json else {}
            except json.JSONDecodeError:
                args = {}

            try:
                result = await session.call_tool(tool_name, arguments=args)

                # Extract text content from the MCP result
                if result.content:
                    text_parts = []
                    for content_item in result.content:
                        if hasattr(content_item, "text"):
                            text_parts.append(content_item.text)
                    return "\n".join(text_parts) if text_parts else "Tool executed successfully (no text output)"
                return "Tool executed successfully (no output)"
            except Exception as e:
                return f"Error calling MCP tool '{tool_name}': {str(e)}"

        return FunctionTool(
            name=tool_name,
            description=tool_description,
            params_json_schema=schema,
            on_invoke_tool=on_invoke_tool,
        )

    def _make_strict_schema(self, input_schema: dict) -> dict:
        """
        Ensure the JSON schema has additionalProperties: false for OpenAI strict mode.
        """
        schema = dict(input_schema)
        if "additionalProperties" not in schema:
            schema["additionalProperties"] = False

        # Ensure all required properties are declared
        if "properties" in schema and "required" not in schema:
            schema["required"] = list(schema["properties"].keys())

        return schema

    async def cleanup(self):
        """
        Close all MCP connections.
        """
        try:
            await self._exit_stack.aclose()
        except Exception:
            pass
