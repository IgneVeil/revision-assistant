import psycopg
from app.config import DB_URL
from app.chunking import chunk_text
from app.embeddings import embed_text


def ingest_document(document_name: str, text: str) -> int:
    """Chunk text, embed each chunk, store every chunk. Returns count stored."""
    chunks = chunk_text(text)

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            for chunk in chunks:
                embedding = embed_text(chunk)
                cur.execute(
                    "INSERT INTO chunks (document, content, embedding) "
                    "VALUES (%s, %s, %s)",
                    (document_name, chunk, str(embedding)),
                )
        conn.commit()

    return len(chunks)