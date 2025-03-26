import streamlit as st
import os
from src.code_mentor.code_review import review_code
from src.code_mentor.code_converter import convert_code

def render_code_mentor():

    """
    Renders the entire Code Mentor UI:
    1. Mode Selection (Debugger or Converter)
    2. Debugger: Code Review
    3. Converter: Code Conversion
    """
    st.markdown("<h2 style='text-align: center;'>🛠️ Code Mentor Mode</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Select one of the following code mentoring options: <b>Debugger</b> or <b>Converter</b>.</p>", unsafe_allow_html=True)

    # ------------------- MODE SELECTION -------------------
    if not st.session_state.code_mentor_mode:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            mentor_mode = st.radio("Code Mentor Options", ["Debugger", "Converter"], horizontal=True)
            if st.button("🚀 Proceed", use_container_width=True):
                st.session_state.code_mentor_mode = mentor_mode
                st.rerun()

    else:
        # ------------------- DEBUGGER MODE -------------------
        if st.session_state.code_mentor_mode == "Debugger":
            st.markdown("<h3 style='text-align: center;'>🔍 AI-Powered Code Review & Debugging</h3>", unsafe_allow_html=True)
            st.markdown("Paste your parallel programming code below. The AI agent will analyze it and suggest improvements.")

            code_input = st.text_area("Enter your code here:", height=300)
            if st.button("🔎 Review Code", use_container_width=True):
                if code_input.strip() == "":
                    st.error("⚠️ Please enter some code to review.")
                else:
                    feedback = review_code(code_input)
                    st.session_state.code_review_feedback = feedback
                    st.rerun()

            if st.session_state.code_review_feedback:
                st.markdown("<h4>📋 Code Review Feedback</h4>", unsafe_allow_html=True)

                # Construct your HTML, optionally including the raw AI feedback
                html_feedback = f"""
                <div style='border:1px solid #ccc; padding:10px; border-radius:5px;'>
                    <pre style="white-space: pre-wrap; background-color: #f8f8f8; padding: 10px;">
            {st.session_state.code_review_feedback}
                    </pre>
                </div>
                """

                # Now render that HTML
                st.markdown(html_feedback, unsafe_allow_html=True)


        # ------------------- CONVERTER MODE -------------------
        elif st.session_state.code_mentor_mode == "Converter":
            st.markdown("<h3 style='text-align: center;'>🔄 AI-Powered Code Converter</h3>", unsafe_allow_html=True)
            st.markdown("Convert your parallel programming code from one paradigm to another. Paste your code below and select the target paradigm.")

            converter_code_input = st.text_area("Enter your code here:", height=300)
            target_paradigm = st.selectbox(
                "🎯 Select target paradigm:", 
                ["threading", "multiprocessing", "async", "mpi4py", "Celery", "Hybrid Approaches"]
            )

            if st.button("⚡ Convert Code", use_container_width=True):
                if converter_code_input.strip() == "":
                    st.error("⚠️ Please enter some code to convert.")
                else:
                    conversion_result = convert_code(converter_code_input, target_paradigm)
                    st.session_state.code_converter_feedback = conversion_result
                    st.rerun()

            if st.session_state.code_converter_feedback:
                st.markdown("<h4>🔁 Converted Code</h4>", unsafe_allow_html=True)
                st.code(st.session_state.code_converter_feedback, language="python")

            
            if st.session_state.code_review_feedback:
                st.markdown("<h4>📋 Code Review Feedback</h4>", unsafe_allow_html=True)

                # Construct your HTML, optionally including the raw AI feedback
                html_feedback = f"""
                <div style='border:1px solid #ccc; padding:10px; border-radius:5px;'>
                    <pre style="white-space: pre-wrap; background-color: #f8f8f8; padding: 10px;">
            {st.session_state.code_review_feedback}
                    </pre>
                </div>
                """

        # ------------------- CHANGE MODE BUTTON -------------------
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Change Code Mentor Option", use_container_width=True):
                st.session_state.code_mentor_mode = None
                st.session_state.code_review_feedback = ""
                st.session_state.code_converter_feedback = ""
                st.rerun()
