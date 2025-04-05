import streamlit as st
from enum import Enum
from textwrap import dedent
from markdown import markdown

# Import code review and converter functions
from src.code_mentor.code_review import review_code
from src.code_mentor.code_converter import convert_code

# Import code challenges functions
from src.code_mentor.code_challenges import generate_question, run_code_in_docker

# Optional: streamlit_ace editor
try:
    from streamlit_ace import st_ace
    ACE_AVAILABLE = True
except ImportError:
    ACE_AVAILABLE = False

class CodeMentorMode(str, Enum):
    DEBUGGER = "Debugger"
    CONVERTER = "Converter"
    CHALLENGES = "Challenges"

def render_code_review_feedback(feedback: str):
    st.markdown("### 📋 Code Review Feedback")
    with st.expander("🔧 Suggested Improvements", expanded=True):
        if "```python" in feedback:
            parts = feedback.split("```python")
            summary = parts[0].strip()
            code_block = parts[1].split("```")[0].strip()
        else:
            summary = feedback
            code_block = ""
        st.markdown(f"""
        <div style="border-left: 5px solid #f39c12; padding: 10px 15px; background-color: #fff8e1;">
            <strong>🧐 Summary:</strong><br>{summary}
        </div>
        """, unsafe_allow_html=True)
        if code_block:
            st.markdown("**✅ Revised Code Suggestion:**")
            st.code(dedent(code_block), language="python")

def render_code_converter_feedback(feedback: str):
    st.markdown("### 🔁 Converted Code")
    with st.expander("🔧 Converted Output", expanded=True):
        if "```python" in feedback:
            parts = feedback.split("```python")
            intro = parts[0].strip()
            converted_code = parts[1].split("```")[0].strip()
            explanation = parts[1].split("```")[1].strip() if "```" in parts[1] else ""
        else:
            intro = feedback
            converted_code = ""
            explanation = ""
        if converted_code:
            st.markdown("**✅ Converted Code:**")
            st.code(dedent(converted_code), language="python")
        if explanation:
            st.markdown("**📝 Explanation:**")
            html_expl = markdown(explanation)
            st.markdown(
                f"""
                <div style="
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    background-color: #eef6fc;
                    font-size: 0.95rem;
                    line-height: 1.6;
                ">
                    {html_expl}
                </div>
                """,
                unsafe_allow_html=True,
            )

def render_debugger_ui():
    st.markdown("<h3 style='text-align: center;'>🔍 AI-Powered Code Review & Debugging</h3>", unsafe_allow_html=True)
    st.markdown("Paste your parallel programming code below. The AI agent will analyze it and suggest improvements.")
    if ACE_AVAILABLE:
        code_input = st_ace(language='python', theme='monokai', height=400)
    else:
        code_input = st.text_area("Enter your code here:", value=st.session_state.get("code_input", ""), height=300)
    st.session_state.code_input = code_input
    if st.button("🔎 Review Code", use_container_width=True):
        if code_input.strip() == "":
            st.error("⚠️ Please enter some code to review.")
        else:
            with st.spinner("Analyzing your code..."):
                feedback = review_code(code_input)
                st.session_state.code_review_feedback = feedback
            st.rerun()
    if st.session_state.get("code_review_feedback"):
        render_code_review_feedback(st.session_state.code_review_feedback)

def render_converter_ui():
    st.markdown("<h3 style='text-align: center;'>🔄 AI-Powered Code Converter</h3>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>Convert your parallel programming code from one paradigm to another.</div>", unsafe_allow_html=True)
    if ACE_AVAILABLE:
        converter_code_input = st_ace(language='python', theme='monokai', height=400)
    else:
        converter_code_input = st.text_area("Enter your code here:", value=st.session_state.get("converted_code_input", ""), height=300)
    st.session_state.converted_code_input = converter_code_input
    target_paradigm = st.selectbox(
        "🎯 Select target paradigm:",
        ["threading", "multiprocessing", "async", "mpi4py", "Celery", "Hybrid Approaches"]
    )
    if st.button("⚡ Convert Code", use_container_width=True):
        if converter_code_input.strip() == "":
            st.error("⚠️ Please enter some code to convert.")
        else:
            with st.spinner("Converting your code..."):
                conversion_result = convert_code(converter_code_input, target_paradigm)
                st.session_state.code_converter_feedback = conversion_result
            st.rerun()
    if st.session_state.get("code_converter_feedback"):
        render_code_converter_feedback(st.session_state.code_converter_feedback)
    if st.session_state.get("code_review_feedback"):
        with st.expander("🧠 Code Review Feedback (Optional)"):
            render_code_review_feedback(st.session_state.code_review_feedback)

def render_code_challenges_ui():
    st.markdown("<h3 style='text-align: center;'>🧩 Code Challenges</h3>", unsafe_allow_html=True)
    st.markdown("Test your skills with dynamic Python quiz questions focused on parallel and distributed computing.")
    if st.button("Generate Question"):
        new_q = generate_question()
        if new_q:
            st.session_state.question = new_q
    question = st.session_state.get("question")
    if question:
        st.subheader("Question Type: " + question.get("type", "Unknown").replace("_", " ").title())
        st.markdown("### " + question.get("prompt", "No prompt provided."))
        st.markdown("**Instructions:** " + question.get("instructions", "No instructions provided."))
        code_snippet = question.get("code", "")
        unique_key = f"ace_editor_{hash(question.get('prompt', code_snippet))}"
        user_code = st_ace(
            value=code_snippet,
            language="python",
            theme="monokai",
            height=400,
            key=unique_key
        )
        if st.button("Run Code"):
            output, error = run_code_in_docker(user_code)
            if error:
                if "SyntaxError" in error:
                    st.error("It looks like there is a syntax error in your code. Please check your code for typos or missing punctuation. Full error message:")
                else:
                    st.error("Code execution failed with the following error:")
                st.code(error, language="python")
            else:
                st.write("### Output:")
                st.code(output)
                test_case = question.get("test_case")
                if test_case and question.get("type") in ["complete_code", "fix_bug", "write_code", "predict_output"]:
                    expected_output = test_case.get("expected")
                    if str(expected_output).strip() == output.strip():
                        st.success("Test Passed! Your solution works correctly.")
                    else:
                        st.error(f"Test Failed: Expected output is {expected_output}, but got {output.strip()}.")

def render_mode_selection():
    st.markdown("""
    <style>
        button[kind="primary"] {
            transition: all 0.2s ease;
            border-radius: 8px !important;
        }
        button[kind="primary"]:hover {
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            transform: translateY(-1px);
        }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h3 style='text-align: center;'>🧑‍🏫 Select Your Code Mentor Mode</h3>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🐞 Debugger", key="select_debugger", use_container_width=True):
            st.session_state.code_mentor_mode = "Debugger"
            st.rerun()
        st.markdown("<div style='text-align: center; color: gray;'>Code review, issue spotting, & suggestions</div>", unsafe_allow_html=True)
    with col2:
        if st.button("🔁 Converter", key="select_converter", use_container_width=True):
            st.session_state.code_mentor_mode = "Converter"
            st.rerun()
        st.markdown("<div style='text-align: center; color: gray;'>Transform code across paradigms</div>", unsafe_allow_html=True)
    with col3:
        if st.button("🧩 Challenges", key="select_challenges", use_container_width=True):
            st.session_state.code_mentor_mode = "Challenges"
            st.rerun()
        st.markdown("<div style='text-align: center; color: gray;'>Test your skills with dynamic code challenges</div>", unsafe_allow_html=True)

def render_code_mentor():
    # Initialize session state variables if not already set.
    for key, value in {
        "code_mentor_mode": None,
        "code_review_feedback": "",
        "code_converter_feedback": "",
        "code_input": "",
        "converted_code_input": "",
        "question": None,
        "question_type_index": 0
    }.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state.code_mentor_mode:
        render_mode_selection()
        st.stop()

    st.markdown(f"""
            <div style='text-align:center; color:#666; margin-top:10px;'>
                📌 Current Mode: <b>{st.session_state.code_mentor_mode}</b>
            </div>
        """, unsafe_allow_html=True)

    if st.session_state.code_mentor_mode == CodeMentorMode.DEBUGGER.value:
        render_debugger_ui()
    elif st.session_state.code_mentor_mode == CodeMentorMode.CONVERTER.value:
        render_converter_ui()
    elif st.session_state.code_mentor_mode == CodeMentorMode.CHALLENGES.value:
        render_code_challenges_ui()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Change Code Mentor Option", use_container_width=True):
            st.session_state.code_mentor_mode = None
            st.session_state.code_review_feedback = ""
            st.session_state.code_converter_feedback = ""
            st.session_state.code_input = ""
            st.session_state.converted_code_input = ""
            st.session_state.question = None
            st.session_state.question_type_index = 0
            st.rerun()
