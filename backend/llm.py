import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not configured")


client = genai.Client(
    api_key=api_key
)


MODEL_NAME = "gemini-3.6-flash"


def call_gemini(prompt):
    try:
        interaction = client.interactions.create(
            model=MODEL_NAME,
            input=prompt
        )

        return interaction.output_text

    except Exception as e:
        print("GEMINI ERROR:", repr(e))
        raise


def generate_answer(question, context):

    prompt = f"""
You are an AI PDF study assistant.

Answer the user's question using ONLY the information
provided in the PDF context.

If the answer cannot be found in the context, say:

"The answer is not available in the uploaded PDF."

Do not invent information.

Explain the answer clearly using simple language.

PDF CONTEXT:
{context}

USER QUESTION:
{question}
"""

    return call_gemini(prompt)


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

    return call_gemini(prompt)


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

    result = call_gemini(prompt).strip()

    if result.startswith("```"):
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

    return json.loads(result)