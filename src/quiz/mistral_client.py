# src/quiz/mistral_client.py

import os
import time
from mistralai import Mistral, UserMessage
from mistralai.models import SDKError
import streamlit as st
# Load Mistral API key from environment
API_KEY = os.getenv("MISTRAL_API_KEY")
if not API_KEY:
    raise ValueError("Please set your MISTRAL_API_KEY in your .env file.")

# Initialize Mistral client
client = Mistral(api_key=API_KEY)

def mistral_chat(prompt_text: str, max_retries=5, wait_time=10) -> str:
    messages = [UserMessage(content=prompt_text)]
    for attempt in range(max_retries):
        try:
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except SDKError as e:
            error_str = str(e)
            if "429" in error_str:
                print(f"⚠️ Rate limit exceeded. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
                wait_time *= 2
            elif "502" in error_str:
                st.error("Quiz generation is temporarily unavailable due to server issues (502 Bad Gateway). Please try again later.")
                return ""
            else:
                raise e
    raise RuntimeError("❌ Failed after multiple retries due to API rate limits.")

