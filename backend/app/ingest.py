import psycopg
from app.chunking import chunk_text
from app.embeddings import embed_text

# How to connect to your local database (matches your docker-compose settings).
DB_URL = "postgresql://revision:revision@localhost:5432/revision"


def ingest_document(document_name: str, text: str) -> int:
    """
    Take a document's text, chunk it, embed each chunk, and save every
    chunk into the database. Returns how many chunks were stored.
    """
    chunks = chunk_text(text)                     # 1. split into chunks (your function)

    with psycopg.connect(DB_URL) as conn:         # 2. open a connection to the database
        with conn.cursor() as cur:                #    a cursor is what runs commands
            for chunk in chunks:                  # 3. for each chunk...
                embedding = embed_text(chunk)     #    ...turn it into 768 numbers (your function)
                cur.execute(                      #    ...and save it as a new row
                    "INSERT INTO chunks (document, content, embedding) "
                    "VALUES (%s, %s, %s)",
                    (document_name, chunk, str(embedding)),
                )
        conn.commit()                             # 4. save the changes for real

    return len(chunks)