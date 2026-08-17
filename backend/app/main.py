import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.ingest import ingest_document
from app.generate import generate_question, mark_answer
from app.retrieve import retrieve

DB_URL = "postgresql://revision:revision@localhost:5432/revision"

app = FastAPI(title="Revision Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # allow the frontend to call this API
    allow_methods=["*"],
    allow_headers=["*"],
)


# These describe what the caller must send in each request.
class IngestRequest(BaseModel):
    document_name: str
    text: str


class QuestionRequest(BaseModel):
    topic: str
    difficulty: str = "medium"


class MarkRequest(BaseModel):
    question: str
    student_answer: str
    topic: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/documents")
def documents():
    """Return the list of distinct saved note titles."""
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT document FROM chunks ORDER BY document")
            rows = cur.fetchall()
    return {"documents": [r[0] for r in rows]}


@app.post("/ingest")
def ingest(req: IngestRequest):
    count = ingest_document(req.document_name, req.text)
    return {"chunks_stored": count}


@app.post("/question")
def question(req: QuestionRequest):
    q = generate_question(req.topic, req.difficulty)
    return {"question": q}


@app.post("/mark")
def mark(req: MarkRequest):
    feedback = mark_answer(req.question, req.student_answer, req.topic)
    sources = retrieve(req.topic, k=3)                    # the notes it judged against
    return {
        "feedback": feedback,
        "sources": [s["content"] for s in sources],       # just the text of each chunk
    }