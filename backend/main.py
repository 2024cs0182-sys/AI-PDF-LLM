from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
    description="AI-powered PDF analysis, Q&A, summary and quiz generation",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# GLOBAL VARIABLES
# =========================================================

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

vector_store = None
pdf_text = ""


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "AI PDF LLM is running successfully!"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================================================
# UPLOAD PDF
# =========================================================

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    global vector_store
    global pdf_text

    # Check file type
    if not file.filename.lower().endswith(".pdf"):

        return JSONResponse(
            status_code=400,
            content={
                "error": "Only PDF files are allowed"
            }
        )

    try:

        # Create file path
        file_path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        # Read uploaded file
        contents = await file.read()

        # Save PDF
        with open(file_path, "wb") as f:
            f.write(contents)

        # Extract text
        extracted_text = extract_text_from_pdf(
            file_path
        )

        if not extracted_text.strip():

            return JSONResponse(
                status_code=400,
                content={
                    "error": "No readable text found in PDF"
                }
            )

        # Store PDF text
        pdf_text = extracted_text

        # Split into chunks
        chunks = split_text(
            extracted_text
        )

        if not chunks:

            return JSONResponse(
                status_code=400,
                content={
                    "error": "Unable to create PDF chunks"
                }
            )

        # Create embeddings
        embeddings = create_embeddings(
            chunks
        )

        # Determine vector dimension
        dimension = embeddings.shape[1]

        # Create vector store
        vector_store = VectorStore(
            dimension
        )

        # Add vectors
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

    except Exception as e:

        print(
            "UPLOAD ERROR:",
            repr(e)
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )


# =========================================================
# ASK QUESTION
# =========================================================

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

    if not question.strip():

        return JSONResponse(
            status_code=400,
            content={
                "error": "Question cannot be empty"
            }
        )

    try:

        # Convert question to embedding
        query_embedding = create_query_embedding(
            question
        )

        # Search relevant chunks
        relevant_chunks = vector_store.search(
            query_embedding,
            top_k=3
        )

        if not relevant_chunks:

            return JSONResponse(
                status_code=400,
                content={
                    "error": "No relevant information found in the PDF"
                }
            )

        # Combine chunks
        context = "\n\n".join(
            relevant_chunks
        )

        # Generate AI answer
        answer = generate_answer(
            question,
            context
        )

        return {
            "question": question,
            "answer": answer,
            "sources_used": len(relevant_chunks)
        }

    except Exception as e:

        print(
            "ASK ERROR:",
            repr(e)
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )


# =========================================================
# SUMMARY
# =========================================================

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

    try:

        summary = generate_summary(
            pdf_text
        )

        return {
            "summary": summary
        }

    except Exception as e:

        print(
            "SUMMARY ERROR:",
            repr(e)
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )


# =========================================================
# QUIZ
# =========================================================

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

    # Validate number
    if number_of_questions < 1 or number_of_questions > 20:

        return JSONResponse(
            status_code=400,
            content={
                "error": "Number of questions must be between 1 and 20"
            }
        )

    # Validate difficulty
    allowed_difficulties = [
        "easy",
        "medium",
        "hard"
    ]

    difficulty = difficulty.lower()

    if difficulty not in allowed_difficulties:

        return JSONResponse(
            status_code=400,
            content={
                "error": "Difficulty must be easy, medium, or hard"
            }
        )

    try:

        quiz = generate_quiz(
            pdf_text,
            number_of_questions,
            difficulty
        )

        return {
            "number_of_questions": len(quiz),
            "difficulty": difficulty,
            "quiz": quiz
        }

    except Exception as e:

        print(
            "QUIZ ERROR:",
            repr(e)
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )