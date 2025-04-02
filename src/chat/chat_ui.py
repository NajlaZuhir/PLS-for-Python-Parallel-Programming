import streamlit as st
import uuid
from src.chat.chat_logic import generate_response
from src.database.db_operations import ChatArchive
from src.auth.auth import get_current_user

def get_chat_title(messages):
    for msg in messages:
        if msg["role"] == "user":
            return msg["content"][:50] + ("..." if len(msg["content"]) > 50 else "")
    return "New Chat"

def render_mode_selector(chat_archive, current_user):
    st.markdown("<h3 style='text-align: center;'>🎯 Select Your Learning Chatbot Mode</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧩 Normal Mode", key="mode_normal", use_container_width=True):
            _init_new_chat("Normal", chat_archive, current_user)

        st.markdown("<div style='text-align: center; color: gray;'>Straightforward Q&A</div>", unsafe_allow_html=True)

    with col2:
        if st.button("🧠 Socratic Mode", key="mode_socratic", use_container_width=True):
            _init_new_chat("Socratic", chat_archive, current_user)

        st.markdown("<div style='text-align: center; color: gray;'>Prompted reasoning through questions</div>", unsafe_allow_html=True)

def _init_new_chat(mode, chat_archive, current_user):
    st.session_state.chat_mode = mode
    st.session_state.mode_selected = True
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.messages = []
    chat_archive.archive_conversation([], mode, current_user)
    st.rerun()

def render_chat(current_user, chat_archive: ChatArchive):
    # ------------ Init Session State ------------ #
    for k, v in {
        "mode_selected": False,
        "chat_mode": None,
        "messages": [],
        "chat_titles": {}
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ------------ SIDEBAR ------------ #
    with st.sidebar:
        st.title("📜 Chat History")
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.current_chat_id = None
            st.session_state.messages = []
            st.session_state.mode_selected = False
            st.session_state.chat_mode = None
            st.rerun()

        previous_chats = chat_archive.get_user_conversations(current_user["username"])

        for chat in previous_chats:
            chat_id = chat["session_id"]
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

    # ------------ MODE SELECTION ------------ #
    if not st.session_state.mode_selected and not st.session_state.current_chat_id:
        render_mode_selector(chat_archive, current_user)
        st.stop()

    # ------------ CURRENT MODE BANNER ------------ #
    if st.session_state.mode_selected:
        st.markdown(f"""
            <div style='text-align:center; color:#666; margin-top:10px;'>
                📌 Current Mode: <b>{st.session_state.chat_mode}</b>
            </div>
        """, unsafe_allow_html=True)

    if not st.session_state.chat_mode:
        st.stop()

    # ------------ CHAT DISPLAY ------------ #

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # --------------------CHAT INPUT------------
    if prompt := st.chat_input("💬 What would you like to know?"):
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            response = generate_response(prompt, mode=st.session_state.chat_mode, top=5)
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        if len(st.session_state.messages) == 2:
            st.session_state.chat_titles[st.session_state.current_chat_id] = get_chat_title(st.session_state.messages)

        chat_archive.archive_conversation(st.session_state.messages, st.session_state.chat_mode, current_user)
        st.rerun()

