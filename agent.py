import asyncio
from fastmcp.client import Client, PythonStdioTransport


async def main():

    transport = PythonStdioTransport(
        script_path="mcp_server.py"
    )

    async with Client(transport) as client:

        print("✅ Connected to MCP Server")

        # Show all available tools
        tools = await client.list_tools()

        print("\nAvailable Tools:\n")

        for tool in tools:
            print(f"- {tool.name}")

        while True:

            print("\n--------------------------------")
            tool = input("Enter tool name (or exit): ").strip()

            if tool.lower() == "exit":
                print("👋 Goodbye!")
                break

            try:

                # -----------------------------
                # get_conversation
                # -----------------------------
                if tool == "get_conversation":

                    conversation_id = input(
                        "Conversation ID: "
                    ).strip()

                    result = await client.call_tool(
                        "get_conversation",
                        {
                            "conversation_id": conversation_id
                        }
                    )

                # -----------------------------
                # delete_conversation
                # -----------------------------
                elif tool == "delete_conversation":

                    conversation_id = input(
                        "Conversation ID: "
                    ).strip()

                    result = await client.call_tool(
                        "delete_conversation",
                        {
                            "conversation_id": conversation_id
                        }
                    )

                # -----------------------------
                # ping
                # get_conversations
                # -----------------------------
                else:

                    result = await client.call_tool(tool)

                print("\n========== RESULT ==========\n")
                print(result)
                print("\n============================")

            except Exception as e:

                print("\n❌ ERROR")
                print(e)


if __name__ == "__main__":
    asyncio.run(main())