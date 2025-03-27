import os
import openai
from openai.error import APIConnectionError, APIError
import streamlit as st

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_chat(prompt_text: str) -> str:
    """
    Handles OpenAI API calls with proper message formatting.
    Rate limit errors are not explicitly handled.
    """
    # Split prompt into system message (first line) and user message (rest)
    lines = prompt_text.split('\n', 1)
    system_message = lines[0].strip()
    user_message = lines[1].strip() if len(lines) > 1 else ''

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=3000
    )

        return response.choices[0].message.content.strip()
    except (APIConnectionError, APIError) as e:
        st.error(f"🌐 Connection error: {e}")
        return ""
