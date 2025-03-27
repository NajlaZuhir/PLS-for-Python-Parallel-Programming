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

########################
# NEW: CODE-BASED QUESTION TEMPLATES
########################
CODE_BASED_TEMPLATES = {
    "Completion": """You are a precise technical assistant that always outputs valid JSON. Generate a code snippet with missing parts based on the provided context. The question should present a code snippet with certain lines removed (indicated by "_____") and ask the student to complete it. Provide the complete code in your answer.
""",
    "SpotTheBug": """You are a precise technical assistant that always outputs valid JSON. Given the following code snippet, identify and fix any bugs that might cause errors or undesirable behavior (such as deadlocks or race conditions). Provide the corrected code and a brief explanation of the fix.
""",
    "PredictOutput": """You are a precise technical assistant that always outputs valid JSON. Analyze the following parallel programming code snippet and predict its output. Include a brief explanation of how concurrency might affect the output.
""",  # Changed first line
    "Transform": """You are a precise technical assistant that always outputs valid JSON. Rewrite the following code snippet using a different parallel programming approach. Ensure equivalent functionality. Provide transformed code and explanation.
""",  # Changed first line
    "ExplainPerformance": """You are a precise technical assistant that always outputs valid JSON. Analyze the following code snippet and explain performance issues (e.g., excessive locking). Provide improvement suggestions.
"""  # Changed first line
}

# CODE_BASED_TEMPLATES = {
#     "Completion": """You are a helpful teaching assistant. Generate a code snippet with missing parts based on the provided context. The question should present a code snippet with certain lines removed (indicated by "_____") and ask the student to complete it. Provide the complete code in your answer.
# """,
#     "SpotTheBug": """You are a code debugging assistant. Given the following code snippet, identify and fix any bugs that might cause errors or undesirable behavior (such as deadlocks or race conditions). Provide the corrected code and a brief explanation of the fix.
# """,
#     "PredictOutput": """You are a code execution expert. Analyze the following parallel programming code snippet and predict its output. Include a brief explanation of how concurrency might affect the output.
# """,
#     "Transform": """You are an expert code converter. Rewrite the following code snippet using a different parallel programming approach. Ensure that the functionality remains equivalent. Provide the transformed code and a brief explanation of the changes.
# """,
#     "ExplainPerformance": """You are an optimization expert. Analyze the following code snippet and explain why it might suffer from performance issues (e.g., due to excessive locking or inefficient resource use). Provide suggestions for improvements.
# """
# }


def get_code_based_template():
    """Randomly select one of the code-based question types."""
    question_type = random.choice(list(CODE_BASED_TEMPLATES.keys()))
    return question_type, CODE_BASED_TEMPLATES[question_type]


# 2. Define get_prompt_template
def get_prompt_template(question_type):
    if question_type == "Multiple Choice":
        return PROMPT_MULTIPLE_CHOICE
    elif question_type == "True/False":
        return PROMPT_TRUE_FALSE
    elif question_type == "Fill in the Blanks":
        return PROMPT_FILL_IN_THE_BLANKS
    elif question_type == "Short Answer":
        return PROMPT_SHORT_ANSWER
    return ""
