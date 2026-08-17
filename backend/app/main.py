import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import DB_URL, FRONTEND_ORIGIN
from app.ingest import ingest_document
from app.generate import generate_question, mark_answer
from app.retrieve import retrieve

app = FastAPI(title="Revision Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class DeleteRequest(BaseModel):
    document_name: str


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


@app.post("/delete")
def delete_document(req: DeleteRequest):
    """Delete all chunks belonging to a document."""
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM chunks WHERE document = %s", (req.document_name,))
            deleted = cur.rowcount
        conn.commit()
    return {"deleted_chunks": deleted}


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
    sources = retrieve(req.topic, k=3)
    return {
        "feedback": feedback,
        "sources": [s["content"] for s in sources],
    }