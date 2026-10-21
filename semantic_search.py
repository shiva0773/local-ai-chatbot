
import ollama
import chromadb

EMBEDDING_MODEL = "nomic-embed-text"

documents = [
    "Employees must change their passwords every 90 days.",
    "Shipment cancellation does not automatically void associated invoices.",
    "Playwright supports browser automation using JavaScript and Python.",
]

client = chromadb.Client()

collection = client.create_collection(
    name="learning_demo",
    embedding_function=None,
)

# Convert and store each document as a vector.
for index, document in enumerate(documents):
    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=document,
    )

    collection.add(
        ids=[str(index)],
        documents=[document],
        embeddings=response["embeddings"],
    )

print("Knowledge base created successfully!")

# Search by meaning.
while True:
    question = input("\nAsk a question (or type 'exit'): ").strip()

    if question.lower() == "exit":
        break

    if not question:
        continue

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=question,
    )

    results = collection.query(
        query_embeddings=response["embeddings"],
        n_results=1,
    )

    print("\nMost relevant passages:")

    for document, distance in zip(
        results["documents"][0],
        results["distances"][0],
    ):
        print(f"- {document} (distance: {distance:.4f})")
