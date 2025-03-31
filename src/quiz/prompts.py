import random

# 1. Define get_dynamic_instruction first

def get_dynamic_instruction(difficulty):
    if difficulty == "Easy":
        return ("Generate straightforward recall questions. ...")
    elif difficulty == "Medium":
        return ("Generate questions that require some analysis. ...")
    elif difficulty == "Hard":
        return ("Generate questions that require multi-step reasoning. ...")
    return ""


########################
# 5. PROMPT TEMPLATES (Non-code-based)
########################
PROMPT_MULTIPLE_CHOICE = """"You are a precise technical assistant that always outputs valid JSON."
Difficulty: {difficulty}.

Additional Instructions: {dynamic_instruction}

Generate {num_questions} multiple-choice questions about: "{topic}" 
using EXCLUSIVELY this context:

{context}

Requirements:
1. Questions must be answerable using ONLY the provided context.
2. Provide 4 answer options per question (A) to D) that are highly plausible distractors requiring critical thought.
3. Clearly indicate the correct answer (e.g. "A").
4. Reflect {difficulty} complexity in the questions.
5. Output JSON in this format:
{{
  "questions": [
    {{
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "A"
    }}
  ]
}}
NO additional content. ONLY JSON.
"""

PROMPT_TRUE_FALSE = """"You are a precise technical assistant that always outputs valid JSON."
Difficulty: {difficulty}.

Additional Instructions: {dynamic_instruction}

Generate {num_questions} true/false questions about: "{topic}" 
using EXCLUSIVELY this context:

{context}

Requirements:
1. Questions must be answerable using ONLY the provided context.
2. Answers must be "True" or "False" only.
3. The options array MUST BE EMPTY.
4. Reflect {difficulty} complexity in the questions.
5. Output JSON in this format:
{{
  "questions": [
    {{
      "question": "...",
      "options": [],
      "answer": "True"
    }}
  ]
}}
NO additional content. ONLY JSON.
"""

PROMPT_FILL_IN_THE_BLANKS = """"You are a precise technical assistant that always outputs valid JSON."
Difficulty: {difficulty}.

Additional Instructions: {dynamic_instruction}

Generate {num_questions} fill-in-the-blank questions about: "{topic}" 
using EXCLUSIVELY this context:

{context}

Requirements:
1. Each question should be a sentence with a blank indicated by "_____".
2. Provide a single correct answer for the blank.
3. Reflect {difficulty} complexity in the questions.
4. Output JSON in this format:
{{
  "questions": [
    {{
      "question": "Python is a _____ language",
      "answer": "high-level"
    }}
  ]
}}
NO additional content. ONLY JSON.
"""

PROMPT_SHORT_ANSWER = """"You are a precise technical assistant that always outputs valid JSON."
Difficulty: {difficulty}.

Additional Instructions: {dynamic_instruction}

Generate {num_questions} short-answer questions about: "{topic}" 
using EXCLUSIVELY this context:

{context}

Requirements:
1. Provide a question that can be answered in a short phrase or sentence.
2. Provide a single correct answer.
3. Reflect {difficulty} complexity in the questions.
4. Output JSON in this format:
{{
  "questions": [
    {{
      "question": "...",
      "answer": "..."
    }}
  ]
}}
NO additional content. ONLY JSON.
"""

PROMPT_CODE_BASED = """"You are a precise technical assistant that always outputs valid JSON."
Difficulty: {difficulty}.

Additional Instructions: {dynamic_instruction}

Generate {num_questions} code-based questions about: "{topic}" using EXCLUSIVELY this context:

{context}

Requirements:
1. YOU MUST ALWAYS INCLUDE a multi-line Python code snippet in the "code_snippet" field, using triple backticks (```python ...```).
   If no code is in the context, invent a short, relevant Python snippet for demonstration.
2. The snippet must be valid Python code that illustrates or tests the concept from the question. 
3. Questions should ask the user to spot a bug, complete the code, or predict the output for that snippet.
4. Provide a single correct answer OR a comma-separated list of acceptable answers.
5. Reflect {difficulty} complexity in the questions.
6. Output JSON in this format:
{{
  "questions": [
    {{
      "question": "...",
      "code_snippet": "...",
      "answer": "..."
    }}
  ]
}}
NO additional content. ONLY JSON.
"""




def get_prompt_template(question_type):
    return {
        "Multiple Choice": PROMPT_MULTIPLE_CHOICE,
        "True/False": PROMPT_TRUE_FALSE,
        "Fill in the Blanks": PROMPT_FILL_IN_THE_BLANKS,
        "Short Answer": PROMPT_SHORT_ANSWER,
        "Code Based": PROMPT_CODE_BASED,   # <-- new entry
    }.get(question_type, "")




