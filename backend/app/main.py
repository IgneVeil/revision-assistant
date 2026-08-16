from fastapi import FastAPI
from pydantic import BaseModel

from app.ingest import ingest_document
from app.generate import generate_question, mark_answer

app = FastAPI(title="Revision Assistant API")


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
    return {"feedback": feedback}