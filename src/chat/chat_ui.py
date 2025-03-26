import streamlit as st
import uuid
from src.chat.chat import generate_response  # Make sure this import is correct
from src.database.db_operations import ChatArchive  # If needed for direct DB ops
from src.auth.auth import get_current_user  # If you need user info here


def get_chat_title(messages):
    """
    Utility function to generate a short title from the first user message.
    """
    for msg in messages:
        if msg["role"] == "user":
            # Return up to 50 characters of the user's first message
            return msg["content"][:50] + ("..." if len(msg["content"]) > 50 else "")
    return "New Chat"

def render_chat(current_user, chat_archive):
    """
    Renders the entire Chatbot UI:
    1. Sidebar Chat History
    2. Chat Mode Selection
    3. Display of Chat Messages
    4. Chat Input
    """

    # ------------------- SIDEBAR: Chat History -------------------
    with st.sidebar:
        st.title("📜 Chat History")

        # New Chat Button
        if st.button("➕ New Chat", key="new_chat", use_container_width=True):
            st.session_state.current_chat_id = None
            st.session_state.messages = []
            st.session_state.mode_selected = False
            st.session_state.chat_mode = None
            st.rerun()

        # Retrieve previous chats from the database
        previous_chats = chat_archive.get_user_conversations(current_user["username"])

        # Display each chat in a list with a delete button
        for chat in previous_chats:
            chat_id = chat["session_id"]
            # Use our utility to generate a short title
            chat_title = st.session_state.chat_titles.get(chat_id, get_chat_title(chat["messages"]))

            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(chat_title, key=f"chat_{chat_id}", use_container_width=True):
                    st.session_state.current_chat_id = chat_id
                    st.session_state.messages = chat["messages"]
                    st.session_state.chat_mode = chat["mode"]
                    st.session_state.mode_selected = True
                    st.rerun()

            with col2:
                if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat"):
                    chat_archive.delete_chat(chat_id)
                    st.rerun()

    # ------------------- MAIN CHAT LOGIC -------------------
    # If we have not selected a chat or chat mode, show a mode selection radio
    if not st.session_state.mode_selected and not st.session_state.current_chat_id:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div style='text-align: center;'><h3>Select Your Learning Chatbot Mode</h3></div>", unsafe_allow_html=True)
            mode = st.radio("🎯 Learning Mode", ["Normal", "Socratic"], horizontal=True)
            if st.button("🚀 Start Learning", use_container_width=True):
                st.session_state.chat_mode = mode
                st.session_state.mode_selected = True
                # Create a new chat ID
                st.session_state.current_chat_id = str(uuid.uuid4())
                st.session_state.messages = []
                # Archive empty conversation just to initialize
                chat_archive.archive_conversation([], mode, current_user)
                st.rerun()

    # If a chat mode is selected, show the current mode at the top
    if st.session_state.mode_selected:
        st.markdown(f"<div style='text-align: center; color: #666;'>📌 Current Mode: <b>{st.session_state.chat_mode}</b></div>", unsafe_allow_html=True)

    # If we still don't have a mode, just stop here
    if not st.session_state.chat_mode:
        st.stop()

    # ------------------- DISPLAY EXISTING MESSAGES -------------------
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # ------------------- CHAT INPUT -------------------
    if prompt := st.chat_input("💬 What would you like to know?"):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate and display assistant response
        with st.chat_message("assistant"):
            response = generate_response(prompt, mode=st.session_state.chat_mode, top=5)
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Update chat title if this is the first user query
        if len(st.session_state.messages) == 2:
            st.session_state.chat_titles[st.session_state.current_chat_id] = get_chat_title(st.session_state.messages)

        # Archive the updated conversation
        chat_archive.archive_conversation(st.session_state.messages, st.session_state.chat_mode, current_user)
        st.rerun()
