import httpx

# Where your local Ollama is listening, and which model to use.
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

# nomic-embed-text always returns vectors of this length.
EMBEDDING_DIM = 768


def embed_text(text: str) -> list[float]:
    """
    Turn a piece of text into an embedding (a list of 768 numbers)
    by asking the local Ollama server.
    """
    response = httpx.post(
        OLLAMA_URL,
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60.0,
    )
    response.raise_for_status()          # blow up loudly if the request failed
    data = response.json()               # read Ollama's reply as a dict
    return data["embedding"]             # pull out the list of numbers