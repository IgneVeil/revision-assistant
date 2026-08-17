import psycopg
from app.config import DB_URL
from app.embeddings import embed_text

# Chunks further than this distance are treated as irrelevant and dropped.
# Tuned for Gemini embeddings (relevant chunks sit around 0.7-0.9).
MAX_DISTANCE = 0.95


def retrieve(query: str, k: int = 3) -> list[dict]:
    """Find up to k chunks closest to the query, dropping ones beyond MAX_DISTANCE."""
    query_embedding = embed_text(query)

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT content, embedding <-> %s::vector AS distance "
                "FROM chunks "
                "ORDER BY embedding <-> %s::vector "
                "LIMIT %s",
                (str(query_embedding), str(query_embedding), k),
            )
            rows = cur.fetchall()

    return [
        {"content": content, "distance": distance}
        for content, distance in rows
        if distance <= MAX_DISTANCE
    ]