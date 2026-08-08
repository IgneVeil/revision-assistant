from app.chunking import chunk_text


def test_splits_into_multiple_chunks():
    # 2000 characters of "a", chunks of 800 -> should be more than one chunk
    text = "a" * 2000
    chunks = chunk_text(text, chunk_size=800, overlap=150)
    assert len(chunks) > 1


def test_chunks_overlap():
    # Number them so we can see the overlap: the start of chunk 2
    # should repeat the end of chunk 1.
    text = "".join(str(i % 10) for i in range(2000))
    chunks = chunk_text(text, chunk_size=800, overlap=150)
    end_of_first = chunks[0][-150:]        # last 150 chars of chunk 1
    start_of_second = chunks[1][:150]      # first 150 chars of chunk 2
    assert end_of_first == start_of_second


def test_bad_overlap_raises():
    # overlap >= chunk_size should be rejected
    try:
        chunk_text("hello", chunk_size=100, overlap=100)
        assert False, "should have raised ValueError"
    except ValueError:
        pass