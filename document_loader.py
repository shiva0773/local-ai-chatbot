
from pathlib import Path

from pypdf import PdfReader


def split_text(text, chunk_size=500, overlap=100):
    """Split text into overlapping chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size - 1")

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def load_pdf(file_path):
    """Extract text from a PDF and retain its page numbers."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")

    reader = PdfReader(str(path))
    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if not text.strip():
            continue

        for chunk_number, chunk in enumerate(split_text(text), start=1):
            documents.append(
                {
                    "text": chunk,
                    "source": path.name,
                    "page": page_number,
                    "chunk": chunk_number,
                }
            )

    return documents
