from database import (
    create_conversation,
    get_conversation,
    get_all_conversations,
    delete_conversation,
    update_title,
    add_message,
    get_recent_messages,
    conversation_exists
)


# =====================================================
# Create Conversation
# =====================================================

def create_chat(title="New Chat"):
    return create_conversation(title)


# =====================================================
# List Conversations
# =====================================================

def list_conversations():

    conversations = get_all_conversations()

    return [
        {
            "id": str(conv["_id"]),
            "title": conv.get("title", "New Chat"),
            "messages": len(conv.get("messages", []))
        }

        for conv in conversations
    ]


# =====================================================
# Get Single Conversation
# =====================================================

def get_single_conversation(conversation_id):

    conversation = get_conversation(conversation_id)

    if conversation is None:

        return {
            "error": "Conversation not found."
        }

    conversation["_id"] = str(conversation["_id"])

    return conversation


# =====================================================
# Delete Conversation
# =====================================================

def remove_conversation(conversation_id):

    delete_conversation(conversation_id)

    return {
        "success": True
    }


# =====================================================
# Rename Conversation
# =====================================================

def rename_chat(conversation_id, title):
    update_title(conversation_id, title)


# =====================================================
# Save Message
# =====================================================

def save_message(conversation_id, role, content):
    add_message(conversation_id, role, content)


# =====================================================
# Recent Messages
# =====================================================

def recent_messages(conversation_id, limit=8):
    return get_recent_messages(conversation_id, limit)


# =====================================================
# Conversation Exists
# =====================================================

def chat_exists(conversation_id):
    return conversation_exists(conversation_id)