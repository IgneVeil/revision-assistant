import httpx
from app.retrieve import retrieve

OLLAMA_URL = "http://localhost:11434/api/generate"
CHAT_MODEL = "llama3.1:8b"


def _ask_model(prompt: str) -> str:
    """Send a prompt to the local chat model and return its text reply."""
    response = httpx.post(
        OLLAMA_URL,
        json={"model": CHAT_MODEL, "prompt": prompt, "stream": False},
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def generate_question(topic: str, difficulty: str = "medium") -> str:
    """Generate a practice question from the notes most relevant to `topic`."""
    chunks = retrieve(topic, k=3)                          # get relevant notes
    context = "\n\n".join(c["content"] for c in chunks)    # join them into one block

    prompt = (
        f"You are a revision tutor. Using ONLY the notes below, write one "
        f"{difficulty}-difficulty practice question that tests understanding of them. "
        f"Do not invent facts that are not in the notes. Output only the question.\n\n"
        f"NOTES:\n{context}"
    )
    return _ask_model(prompt)


def mark_answer(question: str, student_answer: str, topic: str) -> str:
    """Mark a student's answer against the relevant notes."""
    chunks = retrieve(topic, k=3)
    context = "\n\n".join(c["content"] for c in chunks)

    prompt = (
        f"You are a revision tutor marking a student's answer. Judge it ONLY against "
        f"the notes below, not outside knowledge. Say whether it is correct, what was "
        f"missing or wrong, and give brief feedback.\n\n"
        f"NOTES:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        f"STUDENT ANSWER: {student_answer}"
    )
    return _ask_model(prompt)