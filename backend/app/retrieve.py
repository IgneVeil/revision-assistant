import psycopg
from app.embeddings import embed_text

DB_URL = "postgresql://revision:revision@localhost:5432/revision"


def retrieve(query: str, k: int = 3) -> list[dict]:
    """
    Find the k chunks whose meaning is closest to the query.
    Returns a list of {content, distance}, nearest first.
    """
    query_embedding = embed_text(query)      # embed the QUESTION, same model as the chunks

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT content, embedding <-> %s::vector AS distance "  # measure distance
                "FROM chunks "
                "ORDER BY embedding <-> %s::vector "                      # nearest first
                "LIMIT %s",                                              # only the top k
                (str(query_embedding), str(query_embedding), k),
            )
            rows = cur.fetchall()

    return [{"content": content, "distance": distance} for content, distance in rows]