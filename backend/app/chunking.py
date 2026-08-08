def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """
    Split a long string into overlapping chunks.

    - chunk_size: how many characters per chunk
    - overlap: how many characters each chunk repeats from the previous one,
      so a sentence split across a boundary isn't lost from both sides.
    """
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]           # take a slice of the text
        chunks.append(chunk.strip())      # store it (trim stray whitespace)
        start = end - overlap             # next chunk starts a bit before this one ended

    return [c for c in chunks if c]       # drop any empty chunks