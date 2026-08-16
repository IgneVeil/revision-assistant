import psycopg
from app.embeddings import embed_text

DB_URL = "postgresql://revision:revision@localhost:5432/revision"

# Chunks further than this distance are treated as irrelevant and dropped.
MAX_DISTANCE = 18.0


def retrieve(query: str, k: int = 3) -> list[dict]:
    """
    Find up to k chunks closest in meaning to the query,
    dropping any that are further away than MAX_DISTANCE.
    """
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

    # Keep only chunks that are actually close enough to be relevant.
    return [
        {"content": content, "distance": distance}
        for content, distance in rows
        if distance <= MAX_DISTANCE
    ]