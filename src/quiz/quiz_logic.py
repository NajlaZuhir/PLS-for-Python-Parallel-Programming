# src/quiz/quiz_logic.py

import re
import json
import random
import streamlit as st

from langchain.prompts import ChatPromptTemplate
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from src.quiz.faiss_utils import process_chapter, embeddings
from src.quiz.prompts import (
    get_dynamic_instruction,
    get_prompt_template,

)
# from src.quiz.mistral_client import mistral_chat
from src.quiz.openai_client import openai_chat

#################################################
# 1. Utility: Extract JSON from Mistral response
#################################################
def extract_json(response_text: str) -> str:
    """
    Extracts JSON content from the Mistral response, ignoring markdown fences if present.
    """
    match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    json_match = re.search(r"(\{.*\})", response_text, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()
    return response_text

#################################################
# 2. Explanation + Hint Generation
#################################################
def generate_explanation(vector_db: FAISS, question_text: str, correct_answer: str, chapter_name: str) -> str:
    """
    For each question, finds the best matching chunk and asks Mistral for a concise explanation.
    """
    docs = vector_db.similarity_search(question_text, k=1)
    if not docs:
        return "Explanation not found."
    doc_text = docs[0].page_content.strip()
    explanation_prompt = f"""
You are a helpful assistant. Use the following context from {chapter_name} to explain the correct answer:

CONTEXT:
{doc_text}

QUESTION: {question_text}
CORRECT ANSWER: {correct_answer}

Requirements:
- Provide a concise explanation based solely on the chapter content.
- Output only the explanation, nothing else.
"""
    return openai_chat(explanation_prompt)

def generate_hint(vector_db: FAISS, question_text: str, chapter_name: str) -> str:
    """
    For fill-in-the-blank and short-answer questions,
    generate a brief hint (without revealing the full answer) to help guide the student.
    """
    docs = vector_db.similarity_search(question_text, k=1)
    if not docs:
        return "Hint not available."
    doc_text = docs[0].page_content.strip()
    hint_prompt = f"""
You are a helpful assistant. Based on the following context from {chapter_name},
provide a brief hint for the question below without revealing the full answer.

CONTEXT:
{doc_text}

QUESTION: {question_text}

Requirements:
- Provide a concise hint that helps the student recall the answer.
- Do not include the full answer.
- Output only the hint.
"""
    return openai_chat(hint_prompt)

#################################################
# 3. Generate Questions for a Chapter
#################################################
def generate_question_skeleton(chapter_name: str, num_questions: int, question_type: str, difficulty="Easy"):
    """
    Builds a question skeleton from a specified chapter:
    - Loads/filters chunks from FAISS
    - Creates appropriate prompt
    - Calls Mistral for question generation
    """
    vector_db = process_chapter(chapter_name)

    # Manage used_chunks to avoid repeated usage
    if "used_chunks" not in st.session_state:
        st.session_state.used_chunks = set()

    # Instead of returning *all* chunks:
    all_docs = vector_db.similarity_search(query="", k=10)  # or k=5, etc.
    filtered_docs = [doc for doc in all_docs if doc.metadata.get("chunk_id") not in st.session_state.used_chunks]

    if len(filtered_docs) < 5:
        st.session_state.used_chunks.clear()
        filtered_docs = all_docs


    context_chunks = [doc.page_content.strip() for doc in filtered_docs]
    context = "\n\n".join(context_chunks)

    dynamic_instruction = get_dynamic_instruction(difficulty)


    template_str = get_prompt_template(question_type)
    if not template_str:
        return {"questions": []}

    # Build final prompt via LangChain ChatPromptTemplate
    messages = ChatPromptTemplate.from_template(template_str).format_messages(
        num_questions=num_questions,
        topic=chapter_name,
        context=context,
        difficulty=difficulty,
        dynamic_instruction=dynamic_instruction
    )
    final_prompt = "\n\n".join(msg.content for msg in messages)

    response_text = openai_chat(final_prompt)
    response_text = extract_json(response_text)

    # Mark chunks as used
    for doc in filtered_docs:
        st.session_state.used_chunks.add(doc.metadata["chunk_id"])

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        data = {"questions": []}
    print("DEBUG: Response JSON:", data)
    return data

def generate_quiz(chapter_name, num_questions, question_type="Multiple Choice", difficulty="Easy"):
    """
    1. Generates a question skeleton via generate_question_skeleton.
    2. For each question, retrieves a short explanation from the vector DB.
    """
    skeleton = generate_question_skeleton(chapter_name, num_questions, question_type, difficulty)
    questions = skeleton.get("questions", [])

    vector_db = process_chapter(chapter_name)  # For explanations

    final_questions = []
    for q in questions:
        q_text = q.get("question", "")
        q_answer = q.get("answer", "")
        q_options = q.get("options", [])

        # If question_type is in certain categories, no options are needed
        if question_type in ["True/False", "Fill in the Blanks", "Short Answer"
        ]:
            q_options = []

        # Generate explanation if possible
        if q_text and q_answer:
            explanation = generate_explanation(vector_db, q_text, q_answer, chapter_name)
        else:
            explanation = "Explanation not found."

        final_questions.append({
            "question": q_text,
            "options": q_options,
            "answer": q_answer,
            "explanation": explanation,
            "code_snippet": q.get("code_snippet", "")  # Add this line
        })

    return {"questions": final_questions}

#################################################
# 4. For Text-based quiz (from link, etc.)
#################################################
def generate_quiz_from_text(
    raw_text: str,
    num_questions=5,
    question_type="Multiple Choice",
    difficulty="Easy"
):
    """
    Similar logic, but using raw_text instead of chapters.
    Chunks text, builds FAISS, calls Mistral to generate questions.
    """

    # Create single Document
    doc = Document(page_content=raw_text, metadata={"page": 1})

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", " "]
    )
    chunks = text_splitter.split_documents([doc])

    # Build in-memory FAISS index
    vector_db = FAISS.from_documents(chunks, embeddings)

    dynamic_instruction = get_dynamic_instruction(difficulty)


    template_str = get_prompt_template(question_type)
    prompt = template_str.format(
        num_questions=num_questions,
        topic="Python Programming (from link)",
        context=raw_text,
        difficulty=difficulty,
        dynamic_instruction=dynamic_instruction
    )

    response_text = openai_chat(prompt)
    response_text = extract_json(response_text)

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        data = {"questions": []}

    final_questions = []
    for q in data.get("questions", []):
        q_text = q.get("question", "")
        q_answer = q.get("answer", "")
        q_options = q.get("options", [])

        # If question_type in certain categories, no options
        if question_type in ["True/False", "Fill in the Blanks", "Short Answer"]:
            q_options = []

        # Minimal explanation or "No explanation (from link-based)."
        final_questions.append({
            "question": q_text,
            "options": q_options,
            "answer": q_answer,
            "explanation": "No explanation (from link-based).",
            "code_snippet": q.get("code_snippet", "")  # Add this line
        })

    return {"questions": final_questions}