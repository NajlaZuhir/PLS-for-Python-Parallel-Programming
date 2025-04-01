import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from src.quiz.openai_client import openai_chat
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from src.quiz import CHAPTER_MAP  # <--- Import CHAPTER_MAP from the package
from src.quiz.quiz_logic import (
    generate_quiz,
    process_chapter,
    generate_quiz_from_text,
    generate_hint,
    openai_chat
    # mistral_chat
)

def handle_question_type_change(question_type: str):
    """
    Checks if the user changed the question_type from the old one.
    If so, clears the existing quiz data so there's no leftover from the old type.
    """
    # 1) If we haven't stored an old_question_type yet, set it now
    if "old_question_type" not in st.session_state:
        st.session_state.old_question_type = question_type

    # 2) If the new question_type is different from the old one, reset quiz data
    if question_type != st.session_state.old_question_type:
        st.session_state.quiz_data = {}
        st.session_state.user_answers = {}
        st.session_state.hints = {}
        st.session_state.score = 0
        st.session_state.checked_answers = False

        # Update old_question_type to the new type
        st.session_state.old_question_type = question_type

        # Force a re-run so the UI resets
        st.rerun()



def render_quiz():
        st.markdown("""
        <h1 style='text-align: center;'>📘 Adaptive Quiz</h1>
        <p style='text-align: center; color: #666;'>Click Check Answers to view your score and explanations.</p>
    """, unsafe_allow_html=True)

        
        # Let the user choose a source for quiz generation:
        st.markdown("### 📚 Select Quiz Source")

        col1, col2, col3, col4 = st.columns(4)
        selected_style = "background-color: #ffeded; border: 2px solid red;"

        with col1:
            if st.button("📖 PDF Chapter", use_container_width=True, key="pdf_chapter"):
                st.session_state.source_method = "PDF Chapter"
                st.rerun()
            if st.session_state.source_method == "PDF Chapter":
                st.markdown(f"<div style='{selected_style}; text-align:center;'>✔ Selected</div>", unsafe_allow_html=True)

        with col2:
            if st.button("🔗 Web Link", use_container_width=True, key="web_link"):
                st.session_state.source_method = "Web Link"
                st.rerun()
            if st.session_state.source_method == "Web Link":
                st.markdown(f"<div style='{selected_style}; text-align:center;'>✔ Selected</div>", unsafe_allow_html=True)

        with col3:
            if st.button("🎥 YouTube Video", use_container_width=True, key="youtube_video"):
                st.session_state.source_method = "YouTube Video"
                st.rerun()
            if st.session_state.source_method == "YouTube Video":
                st.markdown(f"<div style='{selected_style}; text-align:center;'>✔ Selected</div>", unsafe_allow_html=True)

        with col4:
            if st.button("📂 Upload PDF", use_container_width=True, key="upload_pdf"):
                st.session_state.source_method = "Upload PDF"
                st.rerun()
            if st.session_state.source_method == "Upload PDF":
                st.markdown(f"<div style='{selected_style}; text-align:center;'>✔ Selected</div>", unsafe_allow_html=True)


        st.write(f"**Selected Source: `{st.session_state.source_method}`**")

        
        #################################################################
        # 1) PDF CHAPTER (INTERNAL)
        #################################################################
        if st.session_state.source_method == "PDF Chapter":
            with st.sidebar.expander("📖 PDF Chapter Settings", expanded=True):  # Auto-expanded for the selected method
                selected_chapter = st.selectbox("📖 Select a chapter:", list(CHAPTER_MAP.keys()))
                num_questions = st.number_input("📝 Number of questions:", min_value=1, max_value=50, value=3)
                st.session_state.difficulty = st.radio(
                    " 🎚 Select Difficulty",
                    ["Easy", "Medium", "Hard"],
                    index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty)
                )

                
                question_type = st.selectbox("🔢 Question Type", ["Multiple Choice", "True/False", "Fill in the Blanks", "Short Answer"])
                handle_question_type_change(question_type)
                if st.button("🚀 Generate Quiz"):
                    st.session_state.quiz_data = generate_quiz(
                        chapter_name=selected_chapter,
                        num_questions=num_questions,
                        question_type=question_type,
                        difficulty=st.session_state.difficulty

                    )
                    st.session_state.checked_answers = False
                    st.session_state.user_answers = {}
                    st.session_state.hints = {}
                    st.session_state.score = 0
                    st.rerun()

        #################################################################
        # 2) WEB LINK
        #################################################################
        elif st.session_state.source_method == "Web Link":
            with st.sidebar.expander("🔗 Web Link Quiz Settings", expanded=True):  # Auto-expands when selected
                st.markdown("Note: Model's tokem limit is 16000.")
                link_url = st.text_input("🔗 Enter web page URL:")
                num_questions = st.number_input("📝 Number of questions:", min_value=1, max_value=20, value=5)
                st.session_state.difficulty = st.radio(
                    " 🎚 Select Difficulty",
                    ["Easy", "Medium", "Hard"],
                    index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty)
                )
                question_type = st.selectbox("🔢 Question Type", ["Multiple Choice", "True/False", "Fill in the Blanks", "Short Answer"])
                handle_question_type_change(question_type)
                
                if st.button("🌍 Generate Quiz from Link"):
                    if not link_url.strip():
                        st.error("⚠️ Please enter a valid URL!")
                    else:
                        try:
                            resp = requests.get(link_url, timeout=10)
                            resp.raise_for_status()
                            html = resp.text
                            soup = BeautifulSoup(html, "html.parser")
                            raw_text = soup.get_text(separator="\n")
                            
                            st.session_state.quiz_data = generate_quiz_from_text(
                                raw_text=raw_text,
                                num_questions=num_questions,
                                question_type=question_type,
                                difficulty=st.session_state.difficulty

                            )
                            st.session_state.checked_answers = False
                            st.session_state.user_answers = {}
                            st.session_state.hints = {}
                            st.session_state.score = 0
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to fetch link content: {e}")


        #################################################################
        # 3) YOUTUBE VIDEO
        #################################################################
        elif st.session_state.source_method == "YouTube Video":
            with st.sidebar.expander("🎥 YouTube Video Quiz Settings", expanded=True):  # Auto-expands when selected
                yt_url = st.text_input("🎬 Enter YouTube video URL:")
                num_questions = st.number_input("📝 Number of questions:", min_value=1, max_value=10, value=3)
                st.session_state.difficulty = st.radio(
                    " 🎚 Select Difficulty",
                    ["Easy", "Medium", "Hard"],
                    index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty)
                )
                question_type = st.selectbox("🔢 Question Type", ["Multiple Choice", "True/False", "Fill in the Blanks", "Short Answer"])
                handle_question_type_change(question_type)

                if st.button("🎬 Generate Quiz from YouTube"):
                    if not yt_url.strip():
                        st.error("⚠️ Please enter a valid YouTube URL!")
                    else:
                        try:
                            video_id_match = re.search(r"v=([A-Za-z0-9_-]+)", yt_url)
                            if not video_id_match:
                                st.error("⚠️ Invalid YouTube URL format!")
                            else:
                                video_id = video_id_match.group(1)
                                try:
                                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                                    raw_text = "\n".join(item["text"] for item in transcript_list)
                                    
                                    # Call generate_quiz_from_text after successfully retrieving the transcript
                                    st.session_state.quiz_data = generate_quiz_from_text(
                                        raw_text=raw_text,
                                        num_questions=num_questions,
                                        question_type=question_type,
                                        difficulty=st.session_state.difficulty
                                    )
                                    st.session_state.checked_answers = False
                                    st.session_state.user_answers = {}
                                    st.session_state.hints = {}
                                    st.session_state.score = 0
                                    st.rerun()
                                    
                                except (TranscriptsDisabled, NoTranscriptFound) as te:
                                    st.error("❌ Transcript not available for this video.")
                                    raw_text = ""
                                    
                                    st.session_state.quiz_data = generate_quiz_from_text(
                                        raw_text=raw_text,
                                        num_questions=num_questions,
                                        question_type=question_type,
                                        difficulty=st.session_state.difficulty
                                    )
                                    st.session_state.checked_answers = False
                                    st.session_state.user_answers = {}
                                    st.session_state.hints = {}
                                    st.session_state.score = 0
                                    st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to fetch YouTube transcript: {e}")



        #################################################################
        # 4) UPLOAD PDF
        #################################################################
        else:  # "Upload PDF"
            with st.sidebar.expander("📂 Upload PDF Quiz Settings", expanded=True):  # Auto-expands when selected
                st.markdown("Note: Model's tokem limit is 16000.")
                uploaded_pdf = st.file_uploader("📄 Upload a PDF file", type=["pdf"])
                num_questions = st.number_input("📝 Number of questions:", min_value=1, max_value=20, value=5)
                st.session_state.difficulty = st.radio(
                    " 🎚 Select Difficulty",
                    ["Easy", "Medium", "Hard"],
                    index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty)
                )
                question_type = st.selectbox("🔢 Question Type", ["Multiple Choice", "True/False", "Fill in the Blanks", "Short Answer"])
                handle_question_type_change(question_type)

                if st.button("📑 Generate Quiz from Uploaded PDF"):
                    if not uploaded_pdf:
                        st.error("⚠️ Please upload a PDF file!")
                    else:
                        try:
                            from PyPDF2 import PdfReader
                            reader = PdfReader(uploaded_pdf)
                            raw_text = "".join([page.extract_text() or "" for page in reader.pages])
                            st.session_state.quiz_data = generate_quiz_from_text(
                                raw_text=raw_text,
                                num_questions=num_questions,
                                question_type=question_type,
                                difficulty=st.session_state.difficulty

                            )
                            st.session_state.checked_answers = False
                            st.session_state.user_answers = {}
                            st.session_state.hints = {}
                            st.session_state.score = 0
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to process uploaded PDF: {e}")


        # ---------------------------------------------------------------------
        # Display the quiz if we have it in st.session_state.quiz_data
        quiz_data = st.session_state.quiz_data
        questions = quiz_data.get("questions", [])
        
        if questions:
            difficulty_badge = {
                "Easy": "<span style='color: green;'>🟢 Easy</span>",
                "Medium": "<span style='color: orange;'>🟠 Medium</span>",
                "Hard": "<span style='color: red;'>🔴 Hard</span>"
            }

            st.markdown(f"""
                <div style="text-align: center; font-size: 20px; font-weight: bold; padding: 10px; border-radius: 8px; background-color: #f8f8f8; display: inline-block;">
                    Quiz Difficulty: {difficulty_badge.get(st.session_state.difficulty, 'Easy')}
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<hr style='margin-bottom: 20px;'>", unsafe_allow_html=True)

            correct_count = 0
            for i, q in enumerate(questions):
                q_text = q.get("question", "")
                q_options = q.get("options", [])
                correct_answer = q.get("answer", "")
                explanation = q.get("explanation", "No explanation found.")
        
                st.markdown(f"<h4>Q{i+1}. {q_text}</h4>", unsafe_allow_html=True)
                user_answer_key = f"user_answer_{i}"
                # Initialize the key with an empty string if it doesn't exist
                st.session_state.user_answers.setdefault(user_answer_key, "")

                # Now use the text input to update the value
                if question_type == "Multiple Choice":
                    # -- No text_input here --
                    all_options = ["(Select an answer)"] + q_options
                    selected_answer = st.radio(
                        f"Your answer for Q{i+1}",
                        all_options,
                        key=f"radio_{i}",
                        index=0
                    )
                    if selected_answer == "(Select an answer)":
                        st.markdown("<p style='color: #888;'>No answer selected yet.</p>", unsafe_allow_html=True)
                        st.session_state.user_answers[user_answer_key] = ""
                    else:
                        st.session_state.user_answers[user_answer_key] = selected_answer
                        st.markdown(
                            f"<p style='background-color:#eef8ff; padding:5px; border-radius:5px;'>"
                            f"✅ Your Selection: {selected_answer}</p>", 
                            unsafe_allow_html=True
                        )


                elif question_type == "True/False":
                    # -- No text_input here --
                    tf_options = ["(Select True or False)", "True", "False"]
                    selected_tf = st.radio(
                        f"Your answer for Q{i+1}",
                        tf_options,
                        key=f"tf_{i}",
                        index=0
                    )
                    if selected_tf == "(Select True or False)":
                        st.markdown("<p style='color: #888;'>No answer selected yet.</p>", unsafe_allow_html=True)
                        st.session_state.user_answers[user_answer_key] = ""
                    else:
                        st.session_state.user_answers[user_answer_key] = selected_tf
                        st.markdown(
                            f"<p style='background-color:#eef8ff; padding:5px; border-radius:5px;'>"
                            f"✅ Your Selection: {selected_tf}</p>", 
                            unsafe_allow_html=True
                        )

        
                # Hints if question_type is fill-in, short
                elif question_type in ["Fill in the Blanks", "Short Answer"]:
                    st.session_state.user_answers[user_answer_key] = st.text_input(
                        f"Your answer for Q{i+1}",
                        key=f"text_{i}"
                    )
                    hint_key = f"hint_{i}"
                    if hint_key not in st.session_state.hints:
                        st.session_state.hints[hint_key] = ""
                    if st.button("💡 Hint", key=f"hint_button_{i}"):
                        if st.session_state.source_method == "PDF Chapter":
                            # Only "PDF Chapter" uses process_chapter
                            vector_db = process_chapter(selected_chapter)
                            st.session_state.hints[hint_key] = generate_hint(vector_db, q_text, selected_chapter)
                        else:
                            st.session_state.hints[hint_key] = "Hint not implemented for this source."
                        st.rerun()
                    if st.session_state.hints[hint_key]:
                        st.info(f"Hint: {st.session_state.hints[hint_key]}")
        
                if st.session_state.checked_answers:
                    user_answer = st.session_state.user_answers[user_answer_key]
                    is_correct = False
                    if question_type in ["Multiple Choice", "True/False"]:
                        if correct_answer.lower() in str(user_answer).lower():
                            is_correct = True
                    else:
                        if correct_answer.strip().lower() == user_answer.strip().lower():
                            is_correct = True
        
                    if is_correct:
                        st.markdown(f"<p style='color: green; font-weight: bold;'>✔ Correct!</p>", unsafe_allow_html=True)
                        correct_count += 1
                    else:
                        st.markdown(f"<p style='color: red; font-weight: bold;'>✘ Incorrect! The correct answer is: {correct_answer}</p>", unsafe_allow_html=True)
                    st.info(f"**Explanation:** {explanation}")

                st.write("---")
        
            # Check answers
            if not st.session_state.checked_answers:
                if st.button("Check Answers"):
                    st.session_state.checked_answers = True
                    st.rerun()
            else:
                total = len(questions)
                score_percentage = (correct_count / total) * 100
                st.markdown(f"<h3 style='color: blue;'>Final Score: {correct_count}/{total} ({score_percentage:.1f}%)</h3>", unsafe_allow_html=True)
                st.progress(score_percentage / 100)

                if score_percentage > 80:
                    if st.session_state.difficulty == "Easy":
                        st.session_state.difficulty = "Medium"
                    elif st.session_state.difficulty == "Medium":
                        st.session_state.difficulty = "Hard"
                    st.info("Great job! Increasing difficulty for the next quiz.")
                elif score_percentage < 40:
                    if st.session_state.difficulty == "Hard":
                        st.session_state.difficulty = "Medium"
                    elif st.session_state.difficulty == "Medium":
                        st.session_state.difficulty = "Easy"
                    st.info("You might need more practice. Lowering difficulty for the next quiz.")
                else:
                    st.info("Your performance is average. Keeping the current difficulty.")
        
                # "Next Round" only for internal PDF
                if st.session_state.source_method == "PDF Chapter":
                    if st.button("🔄 Next Round"):
                        st.session_state.quiz_data = generate_quiz(
                            chapter_name=selected_chapter,
                            num_questions=num_questions,
                            question_type=question_type,
                            difficulty=st.session_state.difficulty
                        )
                        st.session_state.user_answers = {}
                        st.session_state.checked_answers = False
                        st.session_state.score = 0
                        st.session_state.hints = {}

                        st.rerun()
                else:
                    st.button("🔄 Next Round (Unavailable)", disabled=True)

        else:
            st.write("No quiz generated yet. Use the sidebar to generate one.")