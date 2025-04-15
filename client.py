import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    # Define the server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],  # Replace with your server script name
        env=None
    )

    # Establish the stdio connection
    async with stdio_client(server_params) as (read, write):
        # Initialize the client session
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Example: List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools:
                print(f"- {tool.name}")

            # Example: Call a specific tool
            # Replace 'tool_name' and arguments with your tool's details
            # result = await session.call_tool("tool_name", {"arg1": "value1"})
            # print("Tool result:", result)

if __name__ == "__main__":
    asyncio.run(run())
