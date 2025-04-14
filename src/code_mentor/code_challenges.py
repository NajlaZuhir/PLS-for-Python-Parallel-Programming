import streamlit as st
import openai
import json
import subprocess
import tempfile
import os
from streamlit_ace import st_ace

# Set your OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Please set your OPENAI_API_KEY in your .env file.")


def extract_json(text):
    """Extracts a JSON object from a string by locating the first '{' and the last '}'."""
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        json_str = text[start:end]
        return json.loads(json_str)
    except Exception as e:
        st.error(f"Could not extract valid JSON: {e}")
        return None

# Define the list of question types you want to cycle through.
question_types = ["write_code", "complete_code", "fix_bug", "find_bug", "design_optimize"]

# Initialize the question type index if it doesn't exist.
if 'question_type_index' not in st.session_state:
    st.session_state.question_type_index = 0

def generate_question(context="parallel and distributed computing using python"):
    """
    Generate a quiz question about parallel and distributed computing using Python.
    The question type is forced to be one of:
      - 'find_bug'
      - 'fix_bug'
      - 'complete_code'
      - 'write_code'
      - 'design_optimize'
      
    The returned JSON must have exactly the following keys:
      - type: the question type
      - prompt: the main question prompt
      - instructions: detailed instructions for the question
      - code: a code snippet to work with (empty string if not applicable)
      - test_case: a JSON object with keys 'input' and 'expected' for testing (null if not applicable)
    """
    current_type = question_types[st.session_state.question_type_index]
    st.session_state.question_type_index = (st.session_state.question_type_index + 1) % len(question_types)
    
    prompt = (
        f"Generate a quiz question about {context} for a Python quiz system. "
        f"The question should be of the type '{current_type}'. "
        "Ensure that the code uses only modules that come with the default Python installation. "
        "Do not use any external packages (for example, do not import numpy, requests, joblib, etc.). "
        "For 'complete_code' questions, include a clear placeholder marker such as '### INSERT CODE HERE' in the code snippet, "
        "and add a comment above the placeholder describing what code is expected. "
        "Return only valid JSON with exactly the following keys:\n"
        "- type: one of the types mentioned above\n"
        "- prompt: the question prompt\n"
        "- instructions: detailed instructions for the question\n"
        "- code: a code snippet that is either buggy, incomplete, or provided for analysis (use an empty string if not applicable). "
        "For complete_code questions, the snippet must include a placeholder line (e.g., '### INSERT CODE HERE') with a preceding comment that describes what code should be added.\n"
        "- test_case: a JSON object with keys 'input' and 'expected' for testing code-based questions (use null if not applicable)\n"
        "For example, return exactly:\n"
        '{"type": "complete_code", "prompt": "Complete the code to implement parallel sum using multiprocessing.", '
        '"instructions": "Fill in the missing parts in the provided code. Look for the line starting with \'### INSERT CODE HERE\' and implement the missing function logic.", '
        '"code": "import multiprocessing\\n\\ndef parallel_sum(numbers):\\n    # Calculate the sum in parallel\\n    ### INSERT CODE HERE  # Implement the logic to create a process pool and compute the sum in parallel\\n    pass\\n\\nif __name__ == \\"__main__\\":\\n    numbers = [1,2,3,4,5]\\n    print(parallel_sum(numbers))  # Expected output: 15", '
        '"test_case": {"input": [1,2,3,4,5], "expected": 15}}'
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()
        question = extract_json(answer)
        return question
    except Exception as e:
        st.error(f"Error generating question: {e}")
        return None

def run_code_in_docker(user_code):
    """
    Executes the provided user_code inside a Docker container as a sandbox.
    The code is written to a temporary file, mounted into the container,
    and then executed using the official python:3.9-slim image.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        tmp.write(user_code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "-v", f"{tmp_path}:/tmp/user_code.py", "python:3.9-slim", "python", "/tmp/user_code.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        error = result.stderr
        return output, error
    except Exception as e:
        return "", str(e)
    finally:
        os.remove(tmp_path)

# For testing as a standalone page
if __name__ == "__main__":
    st.title("Dynamic Python Quiz for Parallel & Distributed Computing")
    st.markdown("This quiz generates a variety of question types on parallel and distributed computing using Python. It also runs user code in a Docker sandbox for code-based questions.")
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
            height=300,
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
                if test_case and question.get("type") in ["complete_code", "fix_bug", "write_code"]:
                    expected_output = test_case.get("expected")
                    if str(expected_output).strip() == output.strip():
                        st.success("Test Passed! Your solution works correctly.")
                    else:
                        st.error(f"Test Failed: Expected output is {expected_output}, but got {output.strip()}.")
    st.markdown("---")
    st.info("Click **Next Question** to generate a new challenge!")
