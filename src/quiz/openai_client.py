import os
import openai                     # ← old import
import streamlit as st

# set the key once
openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_chat(prompt_input) -> str:
    """
    Sends a prompt to OpenAI's ChatCompletion API using the latest interface.

    If prompt_input is a list (e.g., a list of messages from ChatPromptTemplate),
    then it will convert that list into the required format.
    Otherwise, it splits the string into a system and user message.
    """

    if isinstance(prompt_input, list):
        role_map = {"human": "user", "ai": "assistant"}
        messages = [
            {
                "role": role_map.get(getattr(m, "type", ""), getattr(m, "role", "user")),
                "content": m.content,
            }
            if not isinstance(m, dict) else m        # keep plain dicts untouched
            for m in prompt_input
        ]
    else:
        # Otherwise, treat it as a string prompt
        lines = prompt_input.split('\n', 1)
        if len(lines) == 2:
            messages = [
                {"role": "system", "content": lines[0].strip()},
                {"role": "user", "content": lines[1].strip()}
            ]
        else:
            messages = [{"role": "user", "content": prompt_input.strip()}]

    try:
        response = openai.ChatCompletion.create(     # ← old style
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1500  # Adjust this as needed
        )
        return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        st.error(f"Error while accessing OpenAI API: {e}")
        return ""
