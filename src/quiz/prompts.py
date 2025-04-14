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
2. Do **not** reference code snippets, function names, provided context, or programming questions
3. constructs – ask conceptual questions only.
4. Provide 4 answer options per question (A) to D) that are highly plausible distractors requiring critical thought.
5. Clearly indicate the correct answer (e.g. "A").
6. Reflect {difficulty} complexity in the questions.
7. Output JSON in this format:
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
2. Do **not** reference code snippets, function names, provided context, or programming questions
3. constructs – ask conceptual questions only.
4. Answers must be "True" or "False" only.
5. The options array MUST BE EMPTY.
6. Reflect {difficulty} complexity in the questions.
7. Output JSON in this format:
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
2.Do **not** reference code snippets, function names, provided context, or programming questions
3.constructs – ask conceptual questions only.
4. Provide a single correct answer for the blank.
5. Reflect {difficulty} complexity in the questions.
6. Output JSON in this format:
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

PROMPT_MULTIPLE_SELECT = """"You are a precise technical assistant that always outputs valid JSON."
Difficulty: {difficulty}.

Additional Instructions: {dynamic_instruction}

Generate {num_questions} multiple select questions about: "{topic}" 
using EXCLUSIVELY this context:

{context}

Requirements:
1. Each question must provide several options.
2. Do **not** reference code snippets, function names, provided context, or programming questions
3. constructs – ask conceptual questions only.
4. There can be more than one correct answer.
5. Provide answer options labeled (A), (B), (C), (D), etc.
6. Clearly indicate the correct answers as a list (e.g. ["A", "C"]).
7. Reflect {difficulty} complexity in the questions.
8. Output JSON in this format:
{{
  "questions": [
    {{
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": ["A", "C"]
    }}
  ]
}}

NO additional content. ONLY JSON.
"""




# 2. Define get_prompt_template
def get_prompt_template(question_type):
    if question_type == "Multiple Choice":
        return PROMPT_MULTIPLE_CHOICE
    elif question_type == "True/False":
        return PROMPT_TRUE_FALSE
    elif question_type == "Fill in the Blanks":
        return PROMPT_FILL_IN_THE_BLANKS
    elif question_type == "Multiple Select":
        return PROMPT_MULTIPLE_SELECT
    return ""