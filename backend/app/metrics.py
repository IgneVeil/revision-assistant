import time
import psycopg
from app.config import DB_URL


def log_call(operation: str, duration_ms: float) -> None:
    """Save one timing record to the database."""
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO metrics (operation, duration_ms) VALUES (%s, %s)",
                (operation, duration_ms),
            )
        conn.commit()


def timed(operation: str, func, *args, **kwargs):
    """Run func, measure how long it took in ms, log it, and return the result."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    duration_ms = (time.perf_counter() - start) * 1000
    log_call(operation, duration_ms)
    return result