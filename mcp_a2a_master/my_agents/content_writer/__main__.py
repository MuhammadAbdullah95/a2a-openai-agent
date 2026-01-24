import asyncio
import uvicorn

from a2a.types import AgentSkill, AgentCard, AgentCapabilities
import asyncclick as click
from a2a.server.request_handlers import DefaultRequestHandler

from my_agents.content_writer.agent_executor import ContentWriterAgentExecutor
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication


@click.command()
@click.option('--host', default='localhost', help='Host for the agent server')
@click.option('--port', default=10002, help='Port for the agent server')
async def main(host: str, port: int):
    """
    Main function to create and run the content writer agent.
    """
    skill = AgentSkill(
        id="content_writer_skill",
        name="content_writer_skill",
        description="A content writing agent that generates blog posts, articles, "
                    "marketing copy, and other written content. Can save content to files.",
        tags=["content", "writer", "blog", "article", "copywriting"],
        examples=[
            "Write a blog post about Python async programming.",
            "Create a marketing email for a new product launch.",
            "Write an article about machine learning and save it to a file.",
        ]
    )

    agent_card = AgentCard(
        name="content_writer",
        description="A content writing agent that generates blog posts, articles, "
                    "marketing copy, and other written content using GPT-4o. "
                    "Can save generated content to files via filesystem MCP server.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        capabilities=AgentCapabilities(streaming=True),
    )

    agent_executor = ContentWriterAgentExecutor()
    await agent_executor.create()

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore()
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    config = uvicorn.Config(server.build(), host=host, port=port)
    server_instance = uvicorn.Server(config)

    await server_instance.serve()


if __name__ == "__main__":
    asyncio.run(main())
