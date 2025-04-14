import os
import time
from dotenv import load_dotenv

load_dotenv()

from mistralai import Mistral, UserMessage
from mistralai.models import SDKError

# Get your Mistral API key from environment
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("Please set your MISTRAL_API_KEY in your .env file.")

client = Mistral(api_key=api_key)

def convert_code(code, target_paradigm):
    """
    Converts the given parallel programming code to use the target paradigm.
    
    For example, it can convert code from using multiprocessing to threading,
    from threading to async, from anything to mpi4py, Celery, or a Hybrid Approach, etc.
    
    The function uses Mistral to:
    1. Analyze the current code's approach.
    2. Convert the code to use the target paradigm.
    3. Provide a brief explanation of the changes made.
    
    Returns a string containing the converted code and explanation.
    """
    prompt = f"""
You are an expert code converter specialized in parallel programming. Your task is to convert the following code so that it uses {target_paradigm} instead of its current approach. Ensure that the functionality remains equivalent, and make any necessary adjustments for the new paradigm.

Code:
{code}

Provide your output in the following format:
- **Converted Code:** (the complete converted code)
- **Explanation:** (a brief explanation of the changes made)

Only output the converted code and explanation in a structured format.
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
    return "Error: Unable to convert code after multiple attempts."

# For testing purposes
if __name__ == "__main__":
    sample_code = """
import multiprocessing

def worker(task_id):
    print(f"Worker {task_id} is processing.")

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=4)
    pool.map(worker, range(10))
    pool.close()
    pool.join()
"""
    target = "threading"  # Example: convert code t
