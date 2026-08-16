import os
import httpx
from dotenv import load_dotenv

load_dotenv()  # read the .env file so GEMINI_API_KEY is available

# Local Ollama settings (used when no Gemini key is set)
OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_EMBED_MODEL = "nomic-embed-text"

# Gemini settings (used when GEMINI_API_KEY is present)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBED_MODEL = "gemini-embedding-001"

# IMPORTANT: this must match the vector size in your database.
EMBEDDING_DIM = 3072


def _embed_with_ollama(text: str) -> list[float]:
    response = httpx.post(
        OLLAMA_URL,
        json={"model": OLLAMA_EMBED_MODEL, "prompt": text},
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json()["embedding"]


def _embed_with_gemini(text: str) -> list[float]:
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    result = client.models.embed_content(
        model=GEMINI_EMBED_MODEL,
        contents=text,
    )
    return result.embeddings[0].values


def embed_text(text: str) -> list[float]:
    """Embed text using Gemini if a key is set, otherwise local Ollama."""
    if GEMINI_API_KEY:
        return _embed_with_gemini(text)
    return _embed_with_ollama(text)