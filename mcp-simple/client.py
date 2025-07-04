from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent


server_params = StdioServerParameters(command="uv", args=["run", "server.py"])


async def main(query: str):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # tools = await session.list_tools()
            # print(tools)
            langchain_tools = await load_mcp_tools(session)

            agent = create_react_agent("openai:gpt-4.1", langchain_tools, debug=True)
            agent_response = await agent.ainvoke({"messages": query})

            with open("agent_response.md", "w") as f:
                f.write(agent_response["messages"][-1].content)


if __name__ == "__main__":
    import asyncio
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", type=str, required=True)
    args = parser.parse_args()

    asyncio.run(main(args.query))
