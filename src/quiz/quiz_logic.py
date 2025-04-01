# src/quiz/quiz_logic.py

import re
import json
import random
import streamlit as st
import numpy as np

from langchain.prompts import ChatPromptTemplate
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from src.quiz.faiss_utils import process_chapter, embeddings
from src.quiz.prompts import get_dynamic_instruction, get_prompt_template
from src.quiz.openai_client import openai_chat

#################################################
# 1. Utility Functions
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

def check_answer_with_openai(user_answer: str, question: str) -> bool:
    """
    Uses OpenAI to evaluate whether the user's answer adequately addresses the question.
    The prompt forces a single-word response: YES or NO.
    """
    prompt = f"""
You are an expert teaching assistant.
Evaluate whether the user's answer adequately addresses the following question.
Question: "{question}"
User's Answer: "{user_answer}"
Respond with exactly one word: YES if the answer is adequate, NO if it is not.
Do not include any extra text or punctuation.
"""
    response = openai_chat(prompt).strip().upper()
    return response == "YES"





#################################################
# 2. Explanation and Hint Generation
#################################################

def generate_explanation(vector_db: FAISS, question_text: str, correct_answer: str, chapter_name: str) -> str:
    """
    For each question, finds the best matching chunk and asks OpenAI for a concise explanation.
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
    Generates a brief hint (without revealing the full answer) for fill-in-the-blank and short-answer questions.
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
# 3. Generate Question Skeleton and Quiz for a Chapter
#################################################

def generate_question_skeleton(chapter_name: str, num_questions: int, question_type: str, difficulty="Easy"):
    """
    Builds a question skeleton from a specified chapter:
    - Loads and filters chunks from the FAISS vector store.
    - Creates an appropriate prompt using the provided context.
    - Calls OpenAI to generate questions.
    """
    vector_db = process_chapter(chapter_name)

    # Manage used_chunks to avoid repeated usage
    if "used_chunks" not in st.session_state:
        st.session_state.used_chunks = set()

    # Retrieve a subset of documents from the vector store
    all_docs = vector_db.similarity_search(query="", k=10)
    filtered_docs = [doc for doc in all_docs if doc.metadata.get("chunk_id") not in st.session_state.used_chunks]

    if len(filtered_docs) < 5:
        st.session_state.used_chunks.clear()
        filtered_docs = all_docs

    # Combine page content from filtered documents to form the context
    context_chunks = [doc.page_content.strip() for doc in filtered_docs]
    context = "\n\n".join(context_chunks)

    dynamic_instruction = get_dynamic_instruction(difficulty)
    template_str = get_prompt_template(question_type)
    if not template_str:
        return {"questions": []}

    # Build the final prompt using LangChain's ChatPromptTemplate
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

    # Mark filtered chunks as used
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
    Generates a complete quiz for a chapter:
    - Calls generate_question_skeleton to create a question skeleton.
    - Retrieves explanations from the vector store for each question.
    """
    skeleton = generate_question_skeleton(chapter_name, num_questions, question_type, difficulty)
    questions = skeleton.get("questions", [])
    vector_db = process_chapter(chapter_name)  # For explanations

    final_questions = []
    for q in questions:
        q_text = q.get("question", "")
        q_answer = q.get("answer", "")
        q_options = q.get("options", [])
        # For certain question types, options are not needed.
        if question_type in ["True/False", "Fill in the Blanks", "Short Answer"]:
            q_options = []

        explanation = generate_explanation(vector_db, q_text, q_answer, chapter_name) if q_text and q_answer else "Explanation not found."
        final_questions.append({
            "question": q_text,
            "options": q_options,
            "answer": q_answer,
            "explanation": explanation
        })
    return {"questions": final_questions}

#################################################
# 4. Generate Quiz from Raw Text (e.g., from a Web Link)
#################################################

def generate_quiz_from_text(raw_text: str, num_questions=5, question_type="Multiple Choice", difficulty="Easy"):
    """
    Similar to generate_quiz but uses raw_text as the source instead of a chapter.
    Splits the text into chunks, builds an in-memory FAISS index, and generates questions.
    """
    doc = Document(page_content=raw_text, metadata={"page": 1})
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", " "]
    )
    chunks = text_splitter.split_documents([doc])
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
        if question_type in ["True/False", "Fill in the Blanks", "Short Answer"]:
            q_options = []
        final_questions.append({
            "question": q_text,
            "options": q_options,
            "answer": q_answer,
            "explanation": "No explanation (from link-based)."
        })
    return {"questions": final_questions}
