
from pathlib import Path
import hashlib
import io

import chromadb
import ollama
import streamlit as st
from docx import Document
from pypdf import PdfReader

import database

# ---------------- Configuration ----------------
MODEL = "qwen2.5-coder:3b"
EMBEDDING_MODEL = "nomic-embed-text"
COLLECTION_NAME = "documents"

BASE_DIR = Path(__file__).parent
DB_DIR = BASE_DIR / "chroma_db"

SUPPORTED_TYPES = ["pdf", "txt", "md", "docx"]


# ---------------- ChromaDB ----------------
@st.cache_resource
def get_collection():
    client = chromadb.PersistentClient(path=str(DB_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def split_text(text, chunk_size=500, overlap=100):
    text = " ".join(text.split())
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])

        if end == len(text):
            break

        start = end - overlap

    return chunks


# ---------------- Document extraction ----------------
def extract_document(uploaded_file):
    name = uploaded_file.name
    suffix = Path(name).suffix.lower()
    raw_bytes = uploaded_file.getvalue()

    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(raw_bytes))
        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((page_number, text))

        return pages

    if suffix in [".txt", ".md"]:
        text = raw_bytes.decode("utf-8-sig", errors="replace")
        return [(1, text)] if text.strip() else []

    if suffix == ".docx":
        doc = Document(io.BytesIO(raw_bytes))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]

        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text for cell in row.cells))

        text = "\n".join(parts)
        return [(1, text)] if text.strip() else []

    raise ValueError(f"Unsupported file type: {suffix}")


# ---------------- Index documents ----------------
def index_document(uploaded_file):
    collection = get_collection()
    source_name = Path(uploaded_file.name).name
    raw_bytes = uploaded_file.getvalue()
    file_hash = hashlib.sha256(raw_bytes).hexdigest()

    try:
        pages = extract_document(uploaded_file)
    except Exception as exc:
        return False, f"Could not read {source_name}: {exc}"

    documents = []
    metadatas = []
    ids = []

    for page_number, page_text in pages:
        chunks = split_text(page_text)

        for chunk_number, chunk in enumerate(chunks, start=1):
            chunk_id = (
                f"{file_hash[:16]}_p{page_number}_c{chunk_number}"
            )

            documents.append(chunk)
            metadatas.append({
                "source": source_name,
                "page": page_number,
                "chunk": chunk_number,
                "file_hash": file_hash,
            })
            ids.append(chunk_id)

    if not documents:
        return False, f"No extractable text found in {source_name}."

    try:
        embeddings = []

        for chunk in documents:
            response = ollama.embeddings(
                model=EMBEDDING_MODEL,
                prompt=chunk,
            )
            embeddings.append(response["embedding"])

        # Remove an older indexed version of this same filename.
        existing = collection.get(
            where={"source": source_name},
            include=["metadatas"],
        )

        if existing["ids"]:
            collection.delete(ids=existing["ids"])

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        return True, f"Indexed {len(documents)} chunks from {source_name}."

    except Exception as exc:
        return False, f"Indexing failed for {source_name}: {exc}"


# ---------------- Retrieval ----------------
def retrieve_relevant_documents(question, top_k=3):
    collection = get_collection()

    if collection.count() == 0:
        return []

    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=question,
    )

    results = collection.query(
        query_embeddings=[response["embedding"]],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    passages = []

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        passages.append({
            "text": text,
            "source": metadata.get("source", "Unknown"),
            "page": metadata.get("page", 1),
            "distance": distance,
        })

    return passages


# ---------------- Streamlit UI ----------------
st.set_page_config(
    page_title="Local AI Document Chat",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Local AI Document Chat")
st.caption("Ask questions about your own PDF, text, Markdown, and Word documents.")

# Upload files directly from your computer.
with st.sidebar:
    st.header("📁 Add documents")

    uploaded_files = st.file_uploader(
        "Choose documents from your computer",
        type=SUPPORTED_TYPES,
        accept_multiple_files=True,
        help="Supported: PDF, TXT, MD, DOCX",
    )

    if st.button(
        "Index selected documents",
        disabled=not uploaded_files,
        width="stretch",
    ):
        for uploaded_file in uploaded_files:
            with st.spinner(f"Indexing {uploaded_file.name}..."):
                success, message = index_document(uploaded_file)

            if success:
                st.success(message)
            else:
                st.error(message)

    collection = get_collection()
    st.caption(f"Indexed chunks: {collection.count()}")

    st.divider()
    st.header("💬 Chat history")

    if st.button("➕ New chat", width="stretch"):
        st.session_state.pop("conversation_id", None)
        st.rerun()

    # Keep compatibility with the existing database module.
    conversations = database.get_conversations()

    for conversation in conversations:
        conversation_id = conversation['id']
        title = conversation['title']

        if st.button(
            title,
            key=f"conversation_{conversation_id}",
            width="stretch",
        ):
            st.session_state["conversation_id"] = conversation_id
            st.rerun()


# Create a new conversation when needed.
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = database.create_conversation(
        "New conversation"
    )

conversation_id = st.session_state["conversation_id"]

# Load saved messages.
messages = database.get_messages(conversation_id)

for message in messages:
    role = message['role']
    content = message['content']

    with st.chat_message(role):
        st.markdown(content)


question = st.chat_input("Ask a question about your indexed documents...")

if question:
    database.save_message(conversation_id, "user", question)

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            passages = retrieve_relevant_documents(question)

            if not passages:
                answer = (
                    "No documents have been indexed yet. "
                    "Upload one or more documents in the sidebar and "
                    "click **Index selected documents**."
                )
            else:
                context_parts = []

                for passage in passages:
                    context_parts.append(
                        f"[Source: {passage['source']}, "
                        f"Page: {passage['page']}]\n"
                        f"{passage['text']}"
                    )

                context = "\n\n".join(context_parts)

                response = ollama.chat(
                    model=MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Answer the user's question using only the "
                                "provided document context. Cite claims using "
                                "[Source: filename, Page: number]. If the "
                                "context does not contain the answer, say "
                                "that the indexed documents do not provide "
                                "enough information. Do not invent facts."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Document context:\n{context}\n\n"
                                f"Question: {question}"
                            ),
                        },
                    ],
                )

                answer = response["message"]["content"]

        except Exception as exc:
            answer = f"An error occurred: {exc}"

        st.markdown(answer)

    database.save_message(conversation_id, "assistant", answer)
