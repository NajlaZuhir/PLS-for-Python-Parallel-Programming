import streamlit as st
from datetime import datetime

def login():
    """Checks if a user is logged in. If not, shows a login form."""
    if "user" not in st.session_state:
        st.title("🔐 Login")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h3 style='text-align: center;'>Welcome to Professor Neural</h3>", unsafe_allow_html=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True):
                users = {
                    "studentA": {"password": "passwordA", "name": "Student A", "role": "student"},
                    "studentB": {"password": "passwordB", "name": "Student B", "role": "student"}
                }
                if username in users and users[username]["password"] == password:
                    st.session_state.user = {
                        "username": username,
                        "name": users[username]["name"],
                        "role": users[username]["role"],
                        "login_time": datetime.now().isoformat()
                    }
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        return False
    return True

def logout():
    """Provides a logout button in the sidebar."""
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

def get_current_user():
    """Retrieves the current logged-in user details."""
    return st.session_state.get("user", None)
