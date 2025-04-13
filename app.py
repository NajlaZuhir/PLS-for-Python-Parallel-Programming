"""
Professor Neural - Main Streamlit Application

This application provides three main activities:
1. Quiz
2. Chatbot
3. Code Mentor

Each activity is defined in its own module (within the src/ folder)
and imported here. The user can log in, select an activity, and the 
corresponding UI is rendered. All session state initialization
occurs here to ensure consistent state management.
"""

from dotenv import load_dotenv
load_dotenv()  # Load environment FIRST

import os
import openai
import streamlit as st
from src.database.db_operations import ChatArchive
from src.auth.auth import login, logout, get_current_user
from src.chat.chat_ui import render_chat
from src.quiz.quiz_ui import render_quiz
from src.code_mentor.code_mentor_ui import render_code_mentor

# ------------------- Initialize Session States FIRST -------------------
# Initialize all session state variables at the VERY BEGINNING

# Core activity tracking
if "activity" not in st.session_state:
    st.session_state.activity = None

# Chat-related states
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "chat_titles" not in st.session_state:
    st.session_state.chat_titles = {}
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode_selected" not in st.session_state:
    st.session_state.mode_selected = False
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = None

# Quiz-related states
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {}
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "checked_answers" not in st.session_state:
    st.session_state.checked_answers = False
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Easy"
if "score" not in st.session_state:
    st.session_state.score = 0
if "hints" not in st.session_state:
    st.session_state.hints = {}
if "source_method" not in st.session_state:
    st.session_state.source_method = "PDF Chapter"

# Initialize used_chunks for quiz logic
if "used_chunks" not in st.session_state:
    st.session_state.used_chunks = set()

# Code Mentor-related states
if "code_mentor_mode" not in st.session_state:
    st.session_state.code_mentor_mode = None
if "code_review_feedback" not in st.session_state:
    st.session_state.code_review_feedback = ""
if "code_converter_feedback" not in st.session_state:
    st.session_state.code_converter_feedback = ""

# ------------------- Load Environment & OpenAI Key -------------------
# Handle OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
try:
    if not openai_api_key:
        openai_api_key = st.secrets["OPENAI_API_KEY"]
except (FileNotFoundError, AttributeError, KeyError):
    pass

if not openai.api_key:
    st.error("Error: No OPENAI_API_KEY found in environment!")
    st.stop()
    
openai.api_key = openai_api_key
# ------------------- Helper Function: Load CSS -------------------
def load_css(file_path: str):
    """Loads and injects CSS styles"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.error(f"CSS file not found: {file_path}")

# ------------------- Streamlit Page Configuration -------------------
st.set_page_config(
    page_title="Professor Neural",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ------------------- Main Header -------------------
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 0;'>🤖 Professor Neural</h1>
    <h3 style='text-align: center; color: #666666; font-weight: 300; margin-top: 0;'>
        Your AI Tutor for Parallel and Distributed Computing
    </h3>
""", unsafe_allow_html=True)

# ------------------- Authentication -------------------
if not login():
    st.stop()

current_user = get_current_user()
st.markdown(
    f"<p style='text-align: center; color: #666666;'>Welcome, {current_user['name']}!</p>",
    unsafe_allow_html=True
)

# ------------------- Sidebar Components -------------------
with st.sidebar:
    logout()
    
    if st.session_state.activity is not None:
        if st.button("Back to Menu"):
            # Reset all session states
            st.session_state.update({
                "activity": None,
                "mode_selected": False,
                "chat_mode": None,
                "current_chat_id": None,
                "messages": [],
                "chat_titles": {},
                "quiz_data": {},
                "user_answers": {},
                "checked_answers": False,
                "score": 0,
                "hints": {},
                "code_review_feedback": "",
                "code_converter_feedback": "",
                "code_mentor_mode": None,
                "question": None,
                "question_type_index": 0
            })
            st.rerun()


    # ------------------- Main Activity Selection -------------------
    # ------------------- Main Activity Selection -------------------
if st.session_state.activity is None:
    st.markdown("""
        <h2 style='text-align: center;'>🚀 Select an Activity</h2>
        <p style='text-align: center; color: #666;'>How would you like to learn today?</p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📘 Quiz", use_container_width=True):
            st.session_state.activity = "Quiz"
            st.rerun()
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'> </p>", unsafe_allow_html=True)
        
        # New Game button with upcoming note
        if st.button("🎮 Games", use_container_width=True):
            st.session_state.activity = "Games"
            st.rerun()
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Upcoming...</p>", unsafe_allow_html=True)

    with col2:
        if st.button("💬 Chatbot", use_container_width=True):
            st.session_state.activity = "Chatbot"
            st.rerun()
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'> </p>", unsafe_allow_html=True)
        
        # New Dashboard button with upcoming note
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.activity = "Dashboard"
            st.rerun()
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Upcoming...</p>", unsafe_allow_html=True)

    with col3:
        if st.button("🛠️ Code Mentor", use_container_width=True):
            st.session_state.activity = "Code Mentor"
            st.rerun()
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'> </p>", unsafe_allow_html=True)
        
        # New Challenges button with upcoming note
        if st.button("📅 My Planner", use_container_width=True):
            st.session_state.activity = "📅 My Planner"
            st.rerun()
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Upcoming...</p>", unsafe_allow_html=True)

# ------------------- Load CSS After State Initialization -------------------
load_css("src/chat/chat_styles.css")

# ------------------- Service Initialization -------------------
chat_archive = ChatArchive()

# ------------------- Activity Routing -------------------
if st.session_state.activity == "Quiz":
    render_quiz()
elif st.session_state.activity == "Chatbot":
    render_chat(current_user, chat_archive)
elif st.session_state.activity == "Code Mentor":
    render_code_mentor()
