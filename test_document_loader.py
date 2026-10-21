
from document_loader import load_pdf

pdf_path = "documents/sample.pdf"

documents = load_pdf(pdf_path)

print(f"Total chunks created: {len(documents)}")

for document in documents[:3]:
    print("\n--- Chunk ---")
    print(f"Source: {document['source']}")
    print(f"Page: {document['page']}")
    print(f"Chunk: {document['chunk']}")
    print(f"Text: {document['text'][:200]}")
