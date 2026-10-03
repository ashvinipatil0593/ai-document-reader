from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import sys

# -----------------------------
# MongoDB Connection
# -----------------------------
collection = None

try:
    client = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=5000
    )

    client.admin.command("ping")

    # IMPORTANT:
    # Never print to stdout in MCP.
    print("MongoDB Connected", file=sys.stderr)

    db = client["docreader_ai"]
    collection = db["conversations"]

except Exception as e:
    print(f"MongoDB Connection Failed: {e}", file=sys.stderr)


# -----------------------------
# Create New Conversation
# -----------------------------
def create_conversation(title="New Chat"):

    if collection is None:
        return None

    conversation = {
        "title": title,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "messages": []
    }

    result = collection.insert_one(conversation)

    return str(result.inserted_id)


# -----------------------------
# Add Message
# -----------------------------
def add_message(conversation_id, role, content):

    if collection is None:
        return

    collection.update_one(
        {"_id": ObjectId(conversation_id)},
        {
            "$push": {
                "messages": {
                    "role": role,
                    "content": content,
                    "time": datetime.now()
                }
            },
            "$set": {
                "updated_at": datetime.now()
            }
        }
    )


# -----------------------------
# Get One Conversation
# -----------------------------
def get_conversation(conversation_id):

    if collection is None:
        return None

    return collection.find_one(
        {"_id": ObjectId(conversation_id)}
    )


# -----------------------------
# Get All Conversations
# -----------------------------
def get_all_conversations():

    if collection is None:
        return []

    return list(
        collection.find().sort("updated_at", -1)
    )


# -----------------------------
# Recent Messages
# -----------------------------
def get_recent_messages(conversation_id, limit=8):

    conversation = get_conversation(conversation_id)

    if conversation is None:
        return []

    return conversation.get("messages", [])[-limit:]


# -----------------------------
# Update Title
# -----------------------------
def update_title(conversation_id, title):

    if collection is None:
        return

    collection.update_one(
        {"_id": ObjectId(conversation_id)},
        {
            "$set": {
                "title": title,
                "updated_at": datetime.now()
            }
        }
    )


# -----------------------------
# Delete Conversation
# -----------------------------
def delete_conversation(conversation_id):

    if collection is None:
        return

    collection.delete_one(
        {"_id": ObjectId(conversation_id)}
    )


# -----------------------------
# Conversation Exists
# -----------------------------
def conversation_exists(conversation_id):

    if collection is None:
        return False

    return (
        collection.count_documents(
            {"_id": ObjectId(conversation_id)}
        ) > 0
    )