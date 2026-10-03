import os

import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq

from database import (
    get_recent_messages,
    add_message
)

from prompts import qa_prompt

from mcp_client import (
    get_conversations,
    get_conversation,
    delete_conversation
)

load_dotenv()


# =========================================================
# EMBEDDING MODEL
# =========================================================

_embedding_model = None


def load_embedding_model():

    global _embedding_model

    if _embedding_model is None:

        _embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    return _embedding_model


# =========================================================
# GROQ CLIENT
# =========================================================

def load_groq_client():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:

        raise ValueError(
            "GROQ_API_KEY not found."
        )

    return Groq(api_key=api_key)


# =========================================================
# BUILD VECTOR STORE
# =========================================================

def build_vectorstore(chunks):

    if not chunks:

        raise ValueError(
            "No chunks found."
        )

    embedding_model = load_embedding_model()

    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True,
        show_progress_bar=False
    ).astype("float32")

    dimension = embeddings.shape[1]

    faiss_index = faiss.IndexFlatL2(
        dimension
    )

    faiss_index.add(embeddings)

    return (
        faiss_index,
        embedding_model,
        embeddings
    )


# =========================================================
# CHAT HISTORY
# =========================================================

def prepare_chat_history(messages):

    history = []

    for message in messages:

        role = message.get("role")

        content = message.get(
            "content",
            ""
        )

        if role == "user":

            history.append(
                (
                    "human",
                    content
                )
            )

        elif role == "assistant":

            history.append(
                (
                    "ai",
                    content
                )
            )

    return history
# =========================================================
# CREATE RAG CHAIN
# =========================================================

def create_rag_chain(
    chunks,
    faiss_index,
    embedding_model,
    top_k=5
):

    client = load_groq_client()

    # =====================================================
    # MCP TOOLS
    # =====================================================

    tools = [

        {
            "type": "function",
            "function": {
                "name": "get_conversations",
                "description": "Return all conversations.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },

        {
            "type": "function",
            "function": {
                "name": "get_conversation",
                "description": "Return a single conversation by conversation id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "conversation_id"
                    ]
                }
            }
        },

        {
            "type": "function",
            "function": {
                "name": "delete_conversation",
                "description": "Delete a conversation using conversation id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "conversation_id"
                    ]
                }
            }
        }

    ]

    # =====================================================
    # MAIN RAG FUNCTION
    # =====================================================

    def rag_chain(
        question,
        conversation_id
    ):

        previous_messages = get_recent_messages(
            conversation_id,
            limit=8
        )

        chat_history = prepare_chat_history(
            previous_messages
        )
        # =====================================================
        # MCP ROUTING
        # =====================================================

        question_lower = question.lower()

        # -----------------------------------------
        # Show all conversations
        # -----------------------------------------

        if question_lower.startswith(
            (
                "show my conversations",
                "show conversations",
                "list conversations",
                "my conversations",
                "my chats"
            )
        ):

            result = get_conversations()

            return {
                "answer": str(result),
                "context": ""
            }

        # -----------------------------------------
        # Show single conversation
        # -----------------------------------------

        if question_lower.startswith(
            "show conversation"
        ):

            conversation_id = question.split()[-1]

            result = get_conversation(
                conversation_id
            )

            return {
                "answer": str(result),
                "context": ""
            }

        # -----------------------------------------
        # Delete conversation
        # -----------------------------------------

        if question_lower.startswith(
            "delete conversation"
        ):

            conversation_id = question.split()[-1]

            result = delete_conversation(
                conversation_id
            )

            return {
                "answer": str(result),
                "context": ""
            }

        # =====================================================
        # QUESTION EMBEDDING
        # =====================================================

        question_embedding = embedding_model.encode(
            [question],
            convert_to_numpy=True,
            show_progress_bar=False
        ).astype("float32")

        # =====================================================
        # FAISS SEARCH
        # =====================================================

        distances, indices = faiss_index.search(
            question_embedding,
            top_k
        )

        relevant_chunks = []

        for index in indices[0]:

            if 0 <= index < len(chunks):

                relevant_chunks.append(
                    chunks[index]
                )

        context = "\n\n".join(
            relevant_chunks
        )

        # =====================================================
        # NO CONTEXT
        # =====================================================

        if not context.strip():

            answer = (
                "This information is not available "
                "in the uploaded document."
            )

            add_message(
                conversation_id,
                "user",
                question
            )

            add_message(
                conversation_id,
                "assistant",
                answer
            )

            return {
                "answer": answer,
                "context": ""
            }

        # =====================================================
        # PROMPT
        # =====================================================

        messages = qa_prompt.format_messages(
            chat_history=chat_history,
            context=context,
            input=question
        )

        groq_messages = []

        for message in messages:

            if message.type == "system":

                groq_messages.append({
                    "role": "system",
                    "content": message.content
                })

            elif message.type == "human":

                groq_messages.append({
                    "role": "user",
                    "content": message.content
                })

            elif message.type == "ai":

                groq_messages.append({
                    "role": "assistant",
                    "content": message.content
                })
        # =====================================================
        # CALL GROQ
        # =====================================================

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=groq_messages,
            temperature=0.0,
            max_tokens=1024
        )

        answer = response.choices[0].message.content

        if answer is None:

            answer = ""

        answer = answer.strip()

        # =====================================================
        # SAFETY FALLBACK
        # =====================================================

        if not answer:

            answer = (
                "This information is not available "
                "in the uploaded document."
            )

        # =====================================================
        # SAVE USER MESSAGE
        # =====================================================

        add_message(
            conversation_id,
            "user",
            question
        )

        # =====================================================
        # SAVE ASSISTANT MESSAGE
        # =====================================================

        add_message(
            conversation_id,
            "assistant",
            answer
        )

        # =====================================================
        # RETURN RESPONSE
        # =====================================================

        return {
            "answer": answer,
            "context": context
        }

    return rag_chain

