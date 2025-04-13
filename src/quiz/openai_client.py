import os
import openai
from openai import OpenAI
import streamlit as st

# Initialize OpenAI client
client = OpenAI(
    api_key=st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
)

def openai_chat(prompt_text: str) -> str:
    # Split prompt into system and user messages
    lines = prompt_text.split('\n', 1)
    system_message = lines[0].strip()
    user_message = lines[1].strip() if len(lines) > 1 else ''

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=1500
    )
    return response.choices[0].message.content.strip()