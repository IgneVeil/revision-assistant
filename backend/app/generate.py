import os
import time
import httpx
from dotenv import load_dotenv
from app.retrieve import retrieve
from app.metrics import timed

load_dotenv()

# Local Ollama settings (used when no Gemini key is set)
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_CHAT_MODEL = "llama3.1:8b"

# Gemini settings (used when GEMINI_API_KEY is present)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_CHAT_MODEL = "gemini-flash-latest"


def _ask_ollama(prompt: str) -> str:
    response = httpx.post(
        OLLAMA_URL,
        json={"model": OLLAMA_CHAT_MODEL, "prompt": prompt, "stream": False},
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def _ask_gemini(prompt: str) -> str:
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)

    last_error = None
    for attempt in range(4):                      # try up to 4 times
        try:
            result = client.models.generate_content(
                model=GEMINI_CHAT_MODEL,
                contents=prompt,
            )
            return result.text.strip()
        except Exception as e:
            last_error = e
            time.sleep(2 * (attempt + 1))         # wait 2s, 4s, 6s between tries

    raise last_error                              # all retries failed


def _ask_model(prompt: str) -> str:
    """Use Gemini if a key is set, otherwise local Ollama. Timed either way."""
    if GEMINI_API_KEY:
        return timed("chat_generate", _ask_gemini, prompt)
    return timed("chat_generate", _ask_ollama, prompt)


def generate_question(topic: str, difficulty: str = "medium") -> str:
    """Generate a practice question from the notes most relevant to `topic`."""
    chunks = retrieve(topic, k=3)
    context = "\n\n".join(c["content"] for c in chunks)

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