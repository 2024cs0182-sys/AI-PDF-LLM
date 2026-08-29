import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not configured")

client = genai.Client(api_key=api_key)


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

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


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

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


def generate_quiz(text, number_of_questions=10, difficulty="medium"):

    prompt = f"""
You are an AI quiz generator.

Create exactly {number_of_questions} multiple-choice
questions from the provided PDF content.

Difficulty: {difficulty}

Each question must have exactly 4 options.

Return ONLY valid JSON.

Use this exact format:

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

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    quiz_text = response.text.strip()

    if quiz_text.startswith("```"):
        quiz_text = quiz_text.replace("```json", "")
        quiz_text = quiz_text.replace("```", "")
        quiz_text = quiz_text.strip()

    return json.loads(quiz_text)