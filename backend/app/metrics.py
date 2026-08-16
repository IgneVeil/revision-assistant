import time
import psycopg

DB_URL = "postgresql://revision:revision@localhost:5432/revision"


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
    """Run func, measure how long it took in milliseconds, log it, and return the result."""
    start = time.perf_counter()                      # start the stopwatch
    result = func(*args, **kwargs)                   # do the actual work
    duration_ms = (time.perf_counter() - start) * 1000   # stop, convert to ms
    log_call(operation, duration_ms)                 # save the timing
    return result