from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio


async def get_mcp_agent_tools():
    client = MultiServerMCPClient(
        {
            "mcp_tools": {  # type: ignore
                "command": "uv",
                "args": ["run", "./app/mcp_server.py"],
                "transport": "stdio",
            }
        }
    )
    tools = await client.get_tools()
    return tools


agent_tools = asyncio.run(get_mcp_agent_tools())
