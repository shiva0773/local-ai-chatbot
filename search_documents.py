
from pathlib import Path

import chromadb
import ollama


BASE_DIR = Path(__file__).parent
DB_DIR = BASE_DIR / "chroma_db"

EMBEDDING_MODEL = "nomic-embed-text"
COLLECTION_NAME = "documents"


def main():
    client = chromadb.PersistentClient(path=str(DB_DIR))

    collection = client.get_collection(name=COLLECTION_NAME)

    question = input("Ask a question about your documents: ")

    if not question.strip():
        print("Please enter a question.")
        return

    result = ollama.embed(
        model=EMBEDDING_MODEL,
        input=question,
    )

    search_results = collection.query(
        query_embeddings=[result["embeddings"][0]],
        n_results=min(3, collection.count()),
    )

    print("\nRelevant passages:\n")

    for index, text in enumerate(search_results["documents"][0]):
        metadata = search_results["metadatas"][0][index]
        distance = search_results["distances"][0][index]

        print(f"Source: {metadata['source']}")
        print(f"Page: {metadata['page']}")
        print(f"Similarity distance: {distance:.4f}")
        print(f"Text: {text}")
        print("-" * 60)


if __name__ == "__main__":
    main()
