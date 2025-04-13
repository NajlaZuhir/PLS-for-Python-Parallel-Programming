import os
import time
from dotenv import load_dotenv

load_dotenv()
import streamlit as st
from mistralai import Mistral, UserMessage
from mistralai.models import SDKError

# Handle Mistral API key
api_key = os.getenv("MISTRAL_API_KEY")
try:
    if not api_key:
        mistral_api_key = st.secrets["MISTRAL_API_KEY"]
except (FileNotFoundError, AttributeError, KeyError):
    pass

if not api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env or Streamlit secrets.")

client = Mistral(api_key=api_key)

def review_code(code):
    """
    Reviews the provided parallel programming code using Mistral.
    
    The agent acts as a code reviewer by:
    1. Checking for syntax errors.
    2. Identifying potential deadlocks or race conditions.
    3. Highlighting inefficiencies and opportunities for better parallelization.
    4. Suggesting improvements and optimizations.
    
    Returns the review feedback as a string.
    """
    prompt = f"""
    You are a code review assistant specialized in parallel programming. Please debug this code::
    {code}
    
    dont exceed 5-10 lines excluding the code snippet

    """

    max_retries = 3
    wait_time = 5
    messages = [UserMessage(content=prompt)]
    for attempt in range(max_retries):
        try:
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except SDKError as e:
            if "429" in str(e):
                print(f"⚠️ Rate limit exceeded. Retrying in {wait_time} seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
                wait_time *= 2
            else:
                raise e
    return "Error: Unable to retrieve code review after multiple attempts."

# For testing purposes
if __name__ == "__main__":
    sample_code = """
import threading

def worker():
    print("Worker thread")

threads = []
for i in range(5):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)
for t in threads:
    t.join()
"""
    feedback = review_code(sample_code)
    print("Code Review Feedback:")
    print(feedback)
