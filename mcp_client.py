import asyncio
from fastmcp.client import Client, PythonStdioTransport


# ======================================================
# MCP Transport
# ======================================================

TRANSPORT = PythonStdioTransport(
    script_path="mcp_server.py"
)


# ======================================================
# Internal Tool Caller
# ======================================================

async def _call_tool(tool_name, arguments=None):

    arguments = arguments or {}

    async with Client(TRANSPORT) as client:

        result = await client.call_tool(
            tool_name,
            arguments
        )

        # Return only the actual text content
        if result.content:

            return result.content[0].text

        return None


# ======================================================
# Get All Conversations
# ======================================================

def get_conversations():

    return asyncio.run(
        _call_tool(
            "get_conversations"
        )
    )


# ======================================================
# Get Single Conversation
# ======================================================

def get_conversation(conversation_id):

    return asyncio.run(
        _call_tool(
            "get_conversation",
            {
                "conversation_id": conversation_id
            }
        )
    )


# ======================================================
# Delete Conversation
# ======================================================

def delete_conversation(conversation_id):

    return asyncio.run(
        _call_tool(
            "delete_conversation",
            {
                "conversation_id": conversation_id
            }
        )
    )