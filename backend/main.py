from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os

from backend.pdf_processor import extract_text_from_pdf
from backend.chunker import split_text
from backend.embeddings import (
    create_embeddings,
    create_query_embedding
)
from backend.vector_store import VectorStore
from backend.llm import (
    generate_answer,
    generate_summary,
    generate_quiz
)


app = FastAPI(
    title="AI PDF Analyzer and Quiz Generator",
    description="LLM-powered PDF analysis and quiz generation system",
    version="1.0.0"
)


UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


vector_store = None
pdf_text = ""


@app.get("/")
def home():

    return {
        "message": "AI PDF LLM is running successfully!"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    global vector_store, pdf_text

    if not file.filename.lower().endswith(".pdf"):

        return JSONResponse(
            status_code=400,
            content={
                "error": "Only PDF files are allowed"
            }
        )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    extracted_text = extract_text_from_pdf(
        file_path
    )

    pdf_text = extracted_text

    chunks = split_text(
        extracted_text
    )

    if not chunks:

        return JSONResponse(
            status_code=400,
            content={
                "error": "No readable text found in PDF"
            }
        )

    embeddings = create_embeddings(
        chunks
    )

    dimension = embeddings.shape[1]

    vector_store = VectorStore(
        dimension
    )

    vector_store.add(
        embeddings,
        chunks
    )

    return {
        "filename": file.filename,
        "message": "PDF processed successfully",
        "characters": len(extracted_text),
        "chunks": len(chunks),
        "embedding_dimension": dimension
    }


@app.post("/ask")
async def ask_question(question: str):

    global vector_store

    if vector_store is None:

        return JSONResponse(
            status_code=400,
            content={
                "error": "Please upload a PDF first"
            }
        )

    query_embedding = create_query_embedding(
        question
    )

    relevant_chunks = vector_store.search(
        query_embedding,
        top_k=3
    )

    context = "\n\n".join(
        relevant_chunks
    )

    answer = generate_answer(
        question,
        context
    )

    return {
        "question": question,
        "answer": answer,
        "sources_used": len(relevant_chunks)
    }


@app.post("/summary")
async def create_summary():

    global pdf_text

    if not pdf_text:

        return JSONResponse(
            status_code=400,
            content={
                "error": "Please upload a PDF first"
            }
        )

    summary = generate_summary(
        pdf_text
    )

    return {
        "summary": summary
    }


@app.post("/quiz")
async def create_quiz(
    number_of_questions: int = 10,
    difficulty: str = "medium"
):

    global pdf_text

    if not pdf_text:

        return JSONResponse(
            status_code=400,
            content={
                "error": "Please upload a PDF first"
            }
        )

    if number_of_questions < 1 or number_of_questions > 20:

        return JSONResponse(
            status_code=400,
            content={
                "error": "Number of questions must be between 1 and 20"
            }
        )

    allowed_difficulties = [
        "easy",
        "medium",
        "hard"
    ]

    if difficulty.lower() not in allowed_difficulties:

        return JSONResponse(
            status_code=400,
            content={
                "error": "Difficulty must be easy, medium, or hard"
            }
        )

    quiz = generate_quiz(
        pdf_text,
        number_of_questions,
        difficulty.lower()
    )

    return {
        "number_of_questions": len(quiz),
        "difficulty": difficulty.lower(),
        "quiz": quiz
    }