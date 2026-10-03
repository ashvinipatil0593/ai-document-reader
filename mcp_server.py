from fastmcp import FastMCP

from services.conversation_service import (
    list_conversations,
    get_single_conversation,
    remove_conversation,
)

mcp = FastMCP("BookRAG MCP Server")


@mcp.tool
def ping():
    """Health check"""
    return "pong"


@mcp.tool
def get_conversations():
    """Return all conversations"""
    return list_conversations()


@mcp.tool
def get_conversation(conversation_id: str):
    """Return one conversation"""
    return get_single_conversation(conversation_id)


@mcp.tool
def delete_conversation(conversation_id: str):
    """Delete one conversation"""
    return remove_conversation(conversation_id)


if __name__ == "__main__":
    mcp.run()