CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS metrics (
    id          BIGSERIAL PRIMARY KEY,
    operation   TEXT NOT NULL,
    duration_ms DOUBLE PRECISION NOT NULL,
    created_at  TIMESTAMP DEFAULT now()
);