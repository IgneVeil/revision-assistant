"""
Retrieval evals: for a known question, check the RIGHT chunk comes back on top.
These need the local database + Ollama running, so they're marked 'eval'
and skipped in normal CI (which has neither).
"""
import pytest
from app.retrieve import retrieve

# Each case: a question, and a word we expect to appear in the top result.
EVAL_CASES = [
    ("How do plants make food from light?", "Photosynthesis"),
    ("Where does respiration happen in the cell?", "respiration"),
    ("What pigment absorbs light in plants?", "Chlorophyll"),
]


@pytest.mark.eval
@pytest.mark.parametrize("question, expected_word", EVAL_CASES)
def test_top_chunk_is_relevant(question, expected_word):
    results = retrieve(question, k=3)
    assert results, "retrieval returned nothing"
    top_chunk = results[0]["content"]
    assert expected_word.lower() in top_chunk.lower(), (
        f"For '{question}', expected top chunk to mention "
        f"'{expected_word}', but got: {top_chunk[:80]}"
    )