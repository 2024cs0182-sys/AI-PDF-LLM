import os
import json

from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY is not configured")


# =========================================================
# OPENROUTER CLIENT
# =========================================================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)


MODEL_NAME = "openrouter/free"


# =========================================================
# COMMON AI FUNCTION
# =========================================================

def call_ai(prompt):

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

        print("OPENROUTER ERROR:", repr(e))

        raise


# =========================================================
# ASK QUESTION
# =========================================================

def generate_answer(question, context):

    prompt = f"""
You are an AI PDF study assistant.

Answer the user's question using ONLY the information
provided in the PDF context.

If the answer cannot be found in the PDF context, say:

"The answer is not available in the uploaded PDF."

Do not invent information.

Explain the answer clearly using simple language.

PDF CONTEXT:
{context}

USER QUESTION:
{question}
"""

    return call_ai(prompt)


# =========================================================
# SUMMARY
# =========================================================

def generate_summary(text):

    prompt = f"""
You are an AI PDF study assistant.

Create a clear and useful summary of the following PDF.

Include:

1. Main topic
2. Important concepts
3. Key points
4. Important definitions
5. Short conclusion

Use simple language.

PDF CONTENT:
{text[:20000]}
"""

    return call_ai(prompt)


# =========================================================
# QUIZ GENERATOR
# =========================================================

def generate_quiz(
    text,
    number_of_questions=10,
    difficulty="medium"
):

    prompt = f"""
You are an AI quiz generator.

Create exactly {number_of_questions}
multiple-choice questions from the PDF content.

Difficulty: {difficulty}

Each question must have exactly 4 options.

Return ONLY valid JSON.

Use exactly this format:

[
    {{
        "question": "Question text",
        "options": [
            "Option A",
            "Option B",
            "Option C",
            "Option D"
        ],
        "correct_answer": "Option A",
        "explanation": "Short explanation"
    }}
]

Rules:

- Questions must come only from the PDF.
- Do not invent facts.
- Each question must have one correct answer.
- Do not include Markdown.
- Do not include ```json.
- Return only the JSON array.

PDF CONTENT:
{text[:30000]}
"""

    result = call_ai(prompt).strip()

    if result.startswith("```"):

        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

    return json.loads(result)