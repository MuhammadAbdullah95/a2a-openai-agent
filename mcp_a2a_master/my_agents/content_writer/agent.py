from collections.abc import AsyncIterable
import asyncio
import json
import os
from typing import TypedDict, Annotated
from contextlib import AsyncExitStack

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

from utilities.common.file_loader import load_instructions_file

from rich import print as rprint

from dotenv import load_dotenv
load_dotenv()


class ContentWriterState(TypedDict):
    messages: list
    query: str
    final_content: str
    should_save: bool
    save_filename: str
    save_result: str


class ContentWriterAgent:
    """
    Content writing agent using LangGraph + GPT-4o.
    Can generate content and save it to the filesystem via MCP.
    """

    def __init__(self):
        self.system_instruction = load_instructions_file("my_agents/content_writer/instructions.txt")
        self._llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        self._mcp_session: ClientSession | None = None
        self._exit_stack = AsyncExitStack()
        self._graph = None
        self._sessions: dict[str, list] = {}

    async def create(self):
        await self._connect_filesystem_mcp()
        self._graph = self._build_graph()

    async def _connect_filesystem_mcp(self):
        """Connect to the filesystem MCP server via stdio."""
        try:
            # Determine the path to the filesystem server
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            server_dir = os.path.join(base_dir, "mcp", "servers", "filesystem_server")

            server_params = StdioServerParameters(
                command="uv",
                args=["--directory", server_dir, "run", "filesystem_server.py"]
            )

            transport = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read_stream, write_stream = transport[0], transport[1]
            self._mcp_session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            await asyncio.wait_for(self._mcp_session.initialize(), timeout=10.0)
            rprint("[bold green]Content Writer connected to filesystem MCP server[/bold green]")
        except Exception as e:
            rprint(f"[bold yellow]Warning: Could not connect to filesystem MCP server: {e}[/bold yellow]")
            self._mcp_session = None

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        graph = StateGraph(ContentWriterState)

        graph.add_node("generate_content", self._generate_content)
        graph.add_node("save_content", self._save_content)

        graph.set_entry_point("generate_content")
        graph.add_conditional_edges(
            "generate_content",
            self._should_save_content,
            {
                "save": "save_content",
                "end": END,
            }
        )
        graph.add_edge("save_content", END)

        return graph.compile()

    async def _generate_content(self, state: ContentWriterState) -> dict:
        """Generate content using GPT-4o."""
        messages = [
            SystemMessage(content=self.system_instruction),
            HumanMessage(content=state["query"]),
        ]

        response = await self._llm.ainvoke(messages)
        content = response.content

        # Detect if user wants to save
        query_lower = state["query"].lower()
        should_save = any(
            keyword in query_lower
            for keyword in ["save", "write to file", "store", "save to", "save as"]
        )

        # Generate a filename if saving
        save_filename = ""
        if should_save:
            # Try to extract a filename or generate one
            save_filename = self._extract_filename(state["query"])

        return {
            "final_content": content,
            "should_save": should_save,
            "save_filename": save_filename,
        }

    def _should_save_content(self, state: ContentWriterState) -> str:
        """Determine if content should be saved to a file."""
        if state.get("should_save") and self._mcp_session is not None:
            return "save"
        return "end"

    async def _save_content(self, state: ContentWriterState) -> dict:
        """Save the generated content to a file via MCP."""
        if not self._mcp_session:
            return {"save_result": "Filesystem MCP server not available."}

        filename = state.get("save_filename", "content.md")
        content = state.get("final_content", "")

        try:
            result = await self._mcp_session.call_tool(
                "write_file",
                arguments={"filepath": filename, "content": content}
            )
            save_msg = ""
            if result.content:
                for item in result.content:
                    if hasattr(item, "text"):
                        save_msg = item.text
                        break
            return {"save_result": save_msg or "File saved successfully."}
        except Exception as e:
            return {"save_result": f"Error saving file: {str(e)}"}

    def _extract_filename(self, query: str) -> str:
        """Extract or generate a filename from the user query."""
        # Simple heuristic: look for common patterns
        query_lower = query.lower()
        for marker in ["save as ", "save to ", "write to "]:
            if marker in query_lower:
                idx = query_lower.index(marker) + len(marker)
                candidate = query[idx:].strip().split()[0] if idx < len(query) else ""
                if candidate:
                    # Ensure it has an extension
                    if "." not in candidate:
                        candidate += ".md"
                    return candidate

        # Default filename based on content type keywords
        if "blog" in query_lower:
            return "blog_post.md"
        elif "article" in query_lower:
            return "article.md"
        elif "email" in query_lower:
            return "email.md"
        return "content.md"

    async def invoke(self, query: str, session_id: str) -> AsyncIterable[dict]:
        """
        Invoke the content writer agent.

        Yields:
            dict with 'is_task_complete' (bool), 'updates' or 'content' (str)
        """
        yield {
            'is_task_complete': False,
            'updates': "Generating content..."
        }

        try:
            input_state: ContentWriterState = {
                "messages": [],
                "query": query,
                "final_content": "",
                "should_save": False,
                "save_filename": "",
                "save_result": "",
            }

            result = await self._graph.ainvoke(input_state)

            final_content = result.get("final_content", "No content generated.")
            save_result = result.get("save_result", "")

            if save_result:
                final_content += f"\n\n---\n{save_result}"

            rprint(f"[bold green]Content Writer output:[/bold green] {final_content[:200]}...")

            yield {
                'is_task_complete': True,
                'content': final_content,
            }
        except Exception as e:
            error_msg = f"Error in content writer: {str(e)}"
            rprint(f"[bold red]{error_msg}[/bold red]")
            yield {
                'is_task_complete': True,
                'content': error_msg,
            }
