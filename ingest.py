
from pathlib import Path

import chromadb
import ollama

from document_loader import load_pdf


BASE_DIR = Path(__file__).parent
DOCUMENTS_DIR = BASE_DIR / "documents"
DB_DIR = BASE_DIR / "chroma_db"

EMBEDDING_MODEL = "nomic-embed-text"
COLLECTION_NAME = "documents"


def main():
    client = chromadb.PersistentClient(path=str(DB_DIR))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {DOCUMENTS_DIR}")
        return

    for pdf_path in pdf_files:
        documents = load_pdf(pdf_path)

        if not documents:
            print(f"No extractable text found in {pdf_path.name}")
            continue

        ids = []
        texts = []
        metadatas = []
        embeddings = []

        for index, document in enumerate(documents):
            result = ollama.embed(
                model=EMBEDDING_MODEL,
                input=document["text"],
            )

            ids.append(
                f"{document['source']}-page-{document['page']}-chunk-{document['chunk']}"
            )
            texts.append(document["text"])
            metadatas.append(
                {
                    "source": document["source"],
                    "page": document["page"],
                    "chunk": document["chunk"],
                }
            )
            embeddings.append(result["embeddings"][0])

        collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        print(f"Indexed {len(documents)} chunks from {pdf_path.name}")

    print(f"Total chunks in ChromaDB: {collection.count()}")
    print(f"Database location: {DB_DIR}")


if __name__ == "__main__":
    main()
