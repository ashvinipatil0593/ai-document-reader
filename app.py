import streamlit as st
import os
import re

from document_store import save_document
from dotenv import load_dotenv
from pypdf import PdfReader

from services.rag_service import (
    build_vectorstore,
    create_rag_chain,
    load_embedding_model,
)

from database import (
    create_conversation,
    add_message,
    get_all_conversations,
    get_conversation,
    update_title,
    delete_conversation
)

from auth import (
    signup_user,
    login_user,
    create_reset_token,
    reset_password,
    logout_user
)

from redis_client import (
    test_redis_connection,
    create_login_session,
    check_login_session,
    delete_login_session,
    save_reset_token,
    get_reset_token_email,
    delete_reset_token
)

load_dotenv()


# ----------------------------------------------------
# Page Config
# ----------------------------------------------------

st.set_page_config(
    page_title="AI Document Reader",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Document Reader")
st.caption("Conversational RAG with Memory")


# ----------------------------------------------------
# Session State
# ----------------------------------------------------

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
    
if "conversation_initialized" not in st.session_state:
    st.session_state.conversation_initialized = False

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "embedding_model" not in st.session_state:
    st.session_state.embedding_model = None

if "chunks" not in st.session_state:
    st.session_state.chunks = None

if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None

if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None
    
if "num_pages" not in st.session_state:
    st.session_state.num_pages = 0

if "extracted_characters" not in st.session_state:
    st.session_state.extracted_characters = 0

if "embedding_shape" not in st.session_state:
    st.session_state.embedding_shape = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "user" not in st.session_state:
    st.session_state.user = None

if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False
    

    
# ----------------------------------------------------
# Redis Connection
# ----------------------------------------------------

if not test_redis_connection():

    st.error(
        "❌ Redis is not connected. "
        "Please start your Redis server."
    )

    st.stop()
    
    
# ----------------------------------------------------
# Restore Login Session from Redis
# ----------------------------------------------------

if (
    not st.session_state.logged_in
    and st.session_state.user is not None
):

    user_email = st.session_state.user.get(
        "email"
    )

    if user_email:

        if check_login_session(user_email):

            st.session_state.logged_in = True

# ====================================================
# AUTHENTICATION SCREEN
# ====================================================

if not st.session_state.logged_in:

    st.title("🔐 Welcome to AI Document Reader")

    st.caption(
        "Please login or create an account to continue."
    )

    login_tab, signup_tab = st.tabs(
        ["🔑 Login", "📝 Sign Up"]
    )

    # =================================================
    # LOGIN
    # =================================================

    with login_tab:

        st.subheader("🔑 Login")

        login_email = st.text_input(
            "Email",
            autocomplete="username",
            key="login_email"
        )

        login_password = st.text_input(
        "Password",
        type="password",
        autocomplete="current-password",
        key="login_password"
        )
        if st.button(
            "🔐 Login",
            use_container_width=True,
            key="login_button"
        ):

            if not login_email or not login_password:

                st.warning(
                    "Please enter your email and password."
                )

            else:

                success, message, user = login_user(
                    login_email,
                    login_password
                )

                if success:

                    st.session_state.logged_in = True

                    st.session_state.user = user

                    st.session_state.show_forgot_password = False

                    # -----------------------------------------------
                    # Create Redis Login Session
                    # -----------------------------------------------

                    create_login_session(
                        login_email
                    )

                    st.success(
                        "✅ Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        f"❌ {message}"
                    )

        st.divider()

        if st.button(
            "🔄 Forgot Password?",
            key="forgot_password_button"
        ):

            st.session_state.show_forgot_password = True

    # =================================================
    # SIGN UP
    # =================================================

    with signup_tab:

        st.subheader("📝 Create Account")

        signup_name = st.text_input(
            "Full Name",
            key="signup_name"
        )

        signup_email = st.text_input(
            "Email",
            autocomplete="username",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            autocomplete="new-password",
            key="signup_password"
        )

        signup_confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            autocomplete="new-password",
            key="signup_confirm_password"
        )

        st.caption(
            "Password must contain at least 8 characters, "
            "one uppercase letter, one lowercase letter, "
            "and one number."
        )

        if st.button(
            "📝 Create Account",
            use_container_width=True,
            key="signup_button"
        ):

            if (
                not signup_name
                or not signup_email
                or not signup_password
                or not signup_confirm_password
            ):

                st.warning(
                    "Please fill in all fields."
                )

            elif signup_password != signup_confirm_password:
                st.error(
                    "❌ Passwords do not match."
                )

            else:

                success, message = signup_user(
                    signup_name,
                    signup_email,
                    signup_password
                )

                if success:

                    st.success(
                        "✅ Account created successfully!"
                    )

                    st.info(
                        "You can now login using your email and password."
                    )

                else:

                    st.error(
                        f"❌ {message}"
                    )


# ====================================================
# FORGOT PASSWORD
# ====================================================

if (
    not st.session_state.logged_in
    and st.session_state.show_forgot_password
):

    st.divider()

    st.subheader(
        "🔄 Forgot Password"
    )

    reset_email = st.text_input(
        "Enter your registered email",
        key="reset_email"
    )

    if st.button(
        "Generate Reset Token",
        key="generate_reset_token"
    ):

        if not reset_email:

            st.warning(
                "Please enter your email address."
            )

        else:

            success, message, token = (
                create_reset_token(
                    reset_email
                )
            )

            if success:

                

                # -----------------------------------------------
                # Store Reset Token in Redis
                # -----------------------------------------------

                save_reset_token(
                    token,
                    reset_email
                )

                st.success(
                    "✅ Reset token generated."
                )

                st.info(
                    "For development/testing, "
                    "your reset token is shown below."
                )

                st.code(
                    token
                )

                st.session_state.reset_token = token
            else:

                st.error(
                    f"❌ {message}"
                )

    # -----------------------------------------------
# Reset Password
# -----------------------------------------------

if "reset_token" in st.session_state:

    st.divider()

    st.subheader(
        "🔑 Set New Password"
    )

    new_password = st.text_input(
        "New Password",
        type="password",
        key="new_password"
    )

    confirm_new_password = st.text_input(
        "Confirm New Password",
        type="password",
        key="confirm_new_password"
    )

    if st.button(
        "Reset Password",
        key="reset_password_button"
    ):

        if not new_password or not confirm_new_password:

            st.warning(
                "Please fill in both password fields."
            )

        elif new_password != confirm_new_password:

            st.error(
                "❌ Passwords do not match."
            )

        else:

            reset_token = st.session_state.reset_token

            # Check token in Redis
            token_email = get_reset_token_email(
                reset_token
            )

            if token_email is None:

                st.error(
                    "❌ Reset token has expired. "
                    "Please generate a new token."
                )

            else:

                success, message = reset_password(
                    reset_token,
                    new_password
                )

                if success:

                    # Delete token from Redis
                    delete_reset_token(
                        reset_token
                    )

                    st.success(
                        "✅ Password reset successfully!"
                    )

                    st.session_state.pop(
                        "reset_token",
                        None
                    )

                    st.session_state.show_forgot_password = False

                    st.info(
                        "Please login using your new password."
                    )

                else:

                    st.error(
                        f"❌ {message}"
                    )

    # -----------------------------------------------
    # Check Redis Reset Token
    # -----------------------------------------------

    token_email = get_reset_token_email(
        reset_token
    )

    if token_email is None:

        st.error(
            "❌ Reset token has expired. "
            "Please generate a new token."
        )

    else:

        success, message = reset_password(
            reset_token,
            new_password
        )

        if success:

            # Remove token from Redis
            delete_reset_token(
                reset_token
            )

            st.success(
                "✅ Password reset successfully!"
            )

            st.session_state.pop(
                "reset_token",
                None
            )

            st.session_state.show_forgot_password = False

            st.info(
                "Please login using your new password."
            )

        else:

            st.error(
                f"❌ {message}"
            )


# ====================================================
# STOP APPLICATION FOR LOGGED-OUT USERS
# ====================================================

if not st.session_state.logged_in:

    st.stop()


# ----------------------------------------------------
# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------

with st.sidebar:

    st.title("💬 Conversations")

    # New Chat
    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        new_id = create_conversation()

        st.session_state.conversation_id = new_id

        st.rerun()

    st.divider()

# ----------------------------------------------------
# Recent Chats
# ----------------------------------------------------

    conversations = get_all_conversations()

    if conversations:

        st.subheader("Recent Chats")

        for conv in conversations:

            title = conv.get(
                "title",
                "New Chat"
            )

            conversation_id = str(
                conv["_id"]
            )

            menu_key = f"menu_{conversation_id}"
            delete_key = f"delete_{conversation_id}"
            rename_key = f"rename_{conversation_id}"

            # =========================================
            # DELETE CONFIRMATION
            # =========================================

            if st.session_state.get(
                delete_key,
                False
            ):

                st.warning(
                    "⚠️ Are you sure you want to delete this chat?"
                )

                yes_col, no_col = st.columns(2)

                with yes_col:

                    if st.button(
                        "Delete",
                        key=f"yes_delete_{conversation_id}",
                        use_container_width=True
                    ):

                        delete_conversation(
                            conversation_id
                        )

                        if (
                            st.session_state.conversation_id
                            == conversation_id
                        ):

                            st.session_state.conversation_id = (
                                create_conversation()
                            )

                        st.session_state.pop(
                            delete_key,
                            None
                        )

                        st.rerun()

                with no_col:

                    if st.button(
                        "Cancel",
                        key=f"cancel_delete_{conversation_id}",
                        use_container_width=True
                    ):

                        st.session_state.pop(
                            delete_key,
                            None
                        )

                        st.rerun()

            # =========================================
            # RENAME
            # =========================================

            elif st.session_state.get(
                rename_key,
                False
            ):

                new_title = st.text_input(
                    "Rename chat",
                    value=title,
                    key=f"rename_input_{conversation_id}"
                )

                save_col, cancel_col = st.columns(2)

                with save_col:

                    if st.button(
                        "Save",
                        key=f"save_rename_{conversation_id}",
                        use_container_width=True
                    ):

                        if new_title.strip():

                            update_title(
                                conversation_id,
                                new_title.strip()
                            )

                        st.session_state.pop(
                            rename_key,
                            None
                        )

                        st.rerun()

                with cancel_col:

                    if st.button(
                        "Cancel",
                        key=f"cancel_rename_{conversation_id}",
                        use_container_width=True
                    ):

                        st.session_state.pop(
                            rename_key,
                            None
                        )

                        st.rerun()

            # =========================================
            # NORMAL CHAT ROW
            # =========================================

            else:

                chat_col, dots_col = st.columns(
                    [6, 1]
                )

                with chat_col:

                    if st.button(
                        title,
                        key=f"chat_{conversation_id}",
                        use_container_width=True
                    ):

                        st.session_state.conversation_id = (
                            conversation_id
                        )

                        st.rerun()

                with dots_col:

                    if st.button(
                        "⋯",
                        key=f"dots_{conversation_id}",
                        help="Chat options",
                        use_container_width=True
                    ):

                        st.session_state[menu_key] = (
                            not st.session_state.get(
                                menu_key,
                                False
                            )
                        )

                        st.rerun()

            # =========================================
            # OPTIONS
            # =========================================

            if st.session_state.get(
                menu_key,
                False
            ):

                rename_col, delete_col = st.columns(2)

                with rename_col:

                    if st.button(
                        "✏️ Rename",
                        key=f"rename_button_{conversation_id}",
                        use_container_width=True
                    ):

                        st.session_state[rename_key] = True

                        st.session_state.pop(
                            menu_key,
                            None
                        )

                        st.rerun()

                with delete_col:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_button_{conversation_id}",
                        use_container_width=True
                    ):

                        st.session_state[delete_key] = True

                        st.session_state.pop(
                            menu_key,
                            None
                        )

                        st.rerun()
    # ====================================================
    # 🚪 LOGOUT
    # ====================================================

    st.divider()

    if st.session_state.user:

        st.caption(
            f"👤 Logged in as: "
            f"{st.session_state.user.get('email', '')}"
        )

    if st.button(
        "🚪 Logout",
        use_container_width=True,
        key="logout_button"
    ):

        # -----------------------------------------------
        # Get logged-in user's email
        # -----------------------------------------------

        user_email = None

        if st.session_state.user:

            user_email = (
                st.session_state.user.get(
                    "email"
                )
            )

        # -----------------------------------------------
        # Delete Redis Login Session
        # -----------------------------------------------

        if user_email:

            delete_login_session(
                user_email
            )

        # -----------------------------------------------
        # Logout
        # -----------------------------------------------

        logout_user()

        # -----------------------------------------------
        # Clear Login State
        # -----------------------------------------------

        st.session_state.logged_in = False

        st.session_state.user = None

        st.session_state.conversation_id = None

        st.session_state.conversation_initialized = False

        # -----------------------------------------------
        # Return to Login Screen
        # -----------------------------------------------

        st.rerun()
        
# ====================================================
# 📄 UPLOAD DOCUMENT
# ====================================================

st.subheader("📄 Upload Document")

uploaded_pdf = st.file_uploader(
    "Upload your PDF",
    type=["pdf"],
    key="main_pdf_uploader"
)


# ====================================================
# 📚 PROCESS PDF
# ====================================================

if uploaded_pdf is not None:

    if (
        not st.session_state.pdf_uploaded
        or
        st.session_state.pdf_name != uploaded_pdf.name
    ):

        with st.spinner(
            "📚 Processing PDF and creating vector database..."
        ):

            reader = PdfReader(
                uploaded_pdf
            )

            pdf_text = ""

            for page in reader.pages:

                text = page.extract_text()

                if text:

                    text = re.sub(
                        r"\s+",
                        " ",
                        text
                    )

                    text = text.replace(
                        "�",
                        ""
                    )

                    pdf_text += (
                        text
                        + "\n"
                    )

            # ----------------------------------------
            # Document Statistics
            # ----------------------------------------

            st.session_state.num_pages = (
                len(reader.pages)
            )

            st.session_state.extracted_characters = (
                len(pdf_text)
            )

            # ----------------------------------------
            # Create Chunks
            # ----------------------------------------

            chunk_size = 800
            overlap = 200

            chunks = []

            start = 0

            while start < len(pdf_text):

                end = start + chunk_size

                chunk = pdf_text[
                    start:end
                ]

                if chunk.strip():

                    chunks.append(
                        chunk
                    )

                start = end - overlap

            # ----------------------------------------
            # Create Vector Database
            # ----------------------------------------

            (
                faiss_index,
                embedding_model,
                embeddings
            ) = build_vectorstore(
                chunks
            )

            st.session_state.vectorstore = (
                faiss_index
            )

            st.session_state.embedding_model = (
                embedding_model
            )

            st.session_state.embedding_shape = (
                embeddings.shape
            )

            st.session_state.chunks = (
                chunks
            )

            # ----------------------------------------
            # Create RAG Chain
            # ----------------------------------------

            st.session_state.rag_chain = (
                create_rag_chain(
                    chunks,
                    faiss_index,
                    embedding_model
                )
            )
            save_document(
            pdf_name=uploaded_pdf.name,
            chunks=chunks,
            vectorstore=faiss_index,
            embedding_model=embedding_model,
            rag_chain=st.session_state.rag_chain,
            num_pages=st.session_state.num_pages,
            extracted_characters=st.session_state.extracted_characters,
            embedding_shape=st.session_state.embedding_shape,
        )

            st.session_state.pdf_uploaded = True

            st.session_state.pdf_name = (
                uploaded_pdf.name
            )

        st.success(
            "✅ PDF processed successfully."
        )

# ====================================================
# 📊 DOCUMENT STATISTICS
# ====================================================

if st.session_state.pdf_uploaded:

    with st.expander(
        "📊 Document Statistics",
        expanded=False
    ):

        st.divider()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📄 Pages",
                st.session_state.num_pages
            )

        with col2:
            st.metric(
                "🔤 Characters",
                f"{st.session_state.extracted_characters:,}"
            )

        with col3:
            st.metric(
                "✂️ Total Chunks",
                len(st.session_state.chunks)
            )

        with col4:
            st.metric(
                "🗂️ FAISS Vectors",
                st.session_state.vectorstore.ntotal
            )

        st.divider()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.write("**🧠 Embedding Model**")
            st.write("all-MiniLM-L6-v2")

        with col2:
            st.write("**🧠 Embedding Shape**")
            st.write(st.session_state.embedding_shape)

        with col3:
            st.write("**📏 Chunk Size**")
            st.write("800")

        with col4:
            st.write("**🔄 Chunk Overlap**")
            st.write("200")

        st.divider()



# ----------------------------------------------------
# Create First Conversation
# ----------------------------------------------------

if (
    st.session_state.conversation_id is None
    and not st.session_state.conversation_initialized
):

    st.session_state.conversation_id = (
        create_conversation()
    )

    st.session_state.conversation_initialized = True
# ----------------------------------------------------
# Get Current Conversation
# ----------------------------------------------------

conversation = get_conversation(
    st.session_state.conversation_id
)

messages = []

if conversation:

    messages = conversation.get(
        "messages",
        []
    )


# ----------------------------------------------------
# Display Previous Messages
# ----------------------------------------------------

for msg in messages:

    with st.chat_message(
        msg["role"]
    ):

        st.markdown(
            msg["content"]
        )


# ----------------------------------------------------
# Chat Input
# ----------------------------------------------------

question = st.chat_input(
    "Ask anything about the uploaded PDF..."
)


if question:

    # -----------------------------------------------
    # User Message
    # -----------------------------------------------

    with st.chat_message("user"):

        st.markdown(
            question
        )

    # -----------------------------------------------
    # Auto Title
    # -----------------------------------------------

    if conversation:

        if conversation.get(
            "title"
        ) == "New Chat":

            title = question.strip()

            if len(title) > 35:

                title = (
                    title[:35]
                    + "..."
                )

            update_title(
                st.session_state.conversation_id,
                title
            )

    # -----------------------------------------------
    # Assistant Response
    # -----------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        placeholder = st.empty()

        if (
            st.session_state.rag_chain
            is None
        ):

            placeholder.warning(
                "📄 Please upload a PDF first."
            )

        else:

            try:

                with st.spinner(
                    "🔍 Searching document..."
                ):

                    response = (
                        st.session_state.rag_chain(
                            question,
                            st.session_state.conversation_id
                        )
                    )

                answer = response.get(
                    "answer",
                    "This information is not available "
                    "in the uploaded document."
                )

                context = response.get(
                    "context",
                    ""
                )

                placeholder.markdown(
                    answer
                )

                with st.expander(
                    "🔍 View Retrieved PDF Context"
                ):

                    if context:

                        st.write(
                            context
                        )

                    else:

                        st.info(
                            "No relevant document context "
                            "was retrieved."
                        )

            except Exception as e:

                placeholder.error(
                    f"❌ Error: {e}"
                )


# ----------------------------------------------------
# Conversation Details
# ----------------------------------------------------

if st.session_state.conversation_id:

    latest_conversation = get_conversation(
        st.session_state.conversation_id
    )

    if latest_conversation:

        with st.sidebar:

            st.divider()

            st.subheader(
                "Conversation Details"
            )

            st.write(
                f"**Title:** "
                f"{latest_conversation.get('title', 'New Chat')}"
            )

            st.write(
                f"**Messages:** "
                f"{len(latest_conversation.get('messages', []))}"
            )


# ----------------------------------------------------
# PDF Status
# ----------------------------------------------------

if st.session_state.pdf_uploaded:

    st.success(
        "📄 PDF Loaded Successfully"
    )

else:

    st.info(
        "Upload a PDF to enable "
        "document-aware responses."
    )


# ----------------------------------------------------
# Footer
# ----------------------------------------------------

st.divider()

st.caption(
    "📚 Conversational AI Document Reader | "
    "Groq • FAISS • HuggingFace • MongoDB"
)